import os
import http.client
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from ..schemas.weather import WeatherData, ForecastData

weather_cache: Dict[str, Dict[str, Any]] = {}

# Common city coordinates mapping (lat, lon, altitude_meters)
CITY_COORDINATES = {
    "seattle": (47.6062, -122.3321, 50),
    "redmond": (47.6740, -122.1215, 50),
    "new york": (40.7128, -74.0060, 10),
    "los angeles": (34.0522, -118.2437, 71),
    "chicago": (41.8781, -87.6298, 179),
    "san francisco": (37.7749, -122.4194, 52),
    "miami": (25.7617, -80.1918, 2),
    "boston": (42.3601, -71.0589, 5),
    "denver": (39.7392, -104.9903, 1609),
    "portland": (45.5152, -122.6784, 15),
    "austin": (30.2672, -97.7431, 149),
    "phoenix": (33.4484, -112.0740, 331),
    "atlanta": (33.7490, -84.3880, 320),
    "dallas": (32.7767, -96.7970, 131),
    "houston": (29.7604, -95.3698, 12),
}


def _geocode_city(city: str) -> Optional[Tuple[float, float, int]]:
    """
    Convert city name to coordinates using free Open-Meteo geocoding API.
    Falls back to hardcoded coordinates for common cities.
    
    Returns:
        Tuple of (latitude, longitude, altitude) or None
    """
    city_lower = city.lower().split(',')[0].strip()
    
    if city_lower in CITY_COORDINATES:
        return CITY_COORDINATES[city_lower]
    
    try:
        import urllib.request
        import urllib.parse
        
        encoded_city = urllib.parse.quote(city)
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json"
        
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                lat = result["latitude"]
                lon = result["longitude"]
                alt = result.get("elevation", 0)
                return (lat, lon, int(alt))
    except Exception as e:
        print(f"Geocoding failed for {city}: {e}")
    
    return (47.6062, -122.3321, 50)


def get_current_weather(city: str, datetime_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current weather conditions for a city using Meteostat RapidAPI.
    
    Args:
        city: City name (e.g., "Redmond, WA", "Seattle")
        datetime_str: Optional datetime string (ISO format) - if None, uses current date
    
    Returns:
        Dictionary with weather data including temperature, feels_like, condition, 
        rain_chance, and wind_speed
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        return {
            "temperature": 65.0,
            "feels_like": 63.0,
            "condition": "partly cloudy",
            "rain_chance": 20.0,
            "wind_speed": 8.0,
            "humidity": 55.0,
            "timestamp": datetime.now().isoformat(),
            "note": "Using mock data - set RAPIDAPI_KEY for real data"
        }
    
    coords = _geocode_city(city)
    if not coords:
        return {
            "temperature": 65.0,
            "feels_like": 63.0,
            "condition": "partly cloudy",
            "rain_chance": 20.0,
            "wind_speed": 8.0,
            "humidity": 55.0,
            "timestamp": datetime.now().isoformat(),
            "error": f"Could not geocode city: {city}",
            "note": "Using mock data - geocoding failed"
        }
    
    lat, lon, alt = coords
    
    target_date = datetime.now()
    if datetime_str:
        try:
            target_date = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except:
            pass
    
    start_date = target_date.strftime("%Y-%m-%d")
    end_date = target_date.strftime("%Y-%m-%d")
    
    try:
        conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "meteostat.p.rapidapi.com"
        }
        
        endpoint = f"/point/daily?lat={lat}&lon={lon}&alt={alt}&start={start_date}&end={end_date}"
        
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data_raw = res.read()
        data = json.loads(data_raw.decode("utf-8"))
        
        conn.close()
        
        if data.get("data") and len(data["data"]) > 0:
            weather = data["data"][0]
            
            temp_c = weather.get("tavg") or weather.get("tmax") or 20.0
            temp_f = (temp_c * 9/5) + 32
            
            wind_speed_kmh = weather.get("wspd", 0.0)
            wind_speed_mph = wind_speed_kmh * 0.621371
            
            prcp = weather.get("prcp", 0.0)
            rain_chance = min(100.0, prcp * 10) if prcp else 0.0
            
            condition = _get_condition_from_data(weather)
            
            return {
                "temperature": round(temp_f, 1),
                "feels_like": round(temp_f - 2, 1),
                "condition": condition,
                "rain_chance": round(rain_chance, 1),
                "wind_speed": round(wind_speed_mph, 1),
                "humidity": weather.get("rhum", 50.0),
                "timestamp": target_date.isoformat(),
                "city": city,
                "source": "meteostat"
            }
        else:
            raise Exception("No weather data available for this date")
            
    except Exception as e:
        return {
            "temperature": 65.0,
            "feels_like": 63.0,
            "condition": "partly cloudy",
            "rain_chance": 20.0,
            "wind_speed": 8.0,
            "humidity": 55.0,
            "timestamp": datetime.now().isoformat(),
            "error": f"API error: {str(e)}",
            "note": "Using mock data due to API error"
        }


def _get_condition_from_data(weather: Dict[str, Any]) -> str:
    """Determine weather condition from Meteostat data."""
    prcp = weather.get("prcp", 0.0)
    snow = weather.get("snow", 0.0)
    
    if snow and snow > 0:
        return "snowy"
    elif prcp and prcp > 10:
        return "rainy"
    elif prcp and prcp > 2:
        return "light rain"
    else:
        return "partly cloudy"


def get_hourly_forecast(city: str, datetime_str: str) -> Dict[str, Any]:
    """
    Get hourly forecast for a specific time.
    
    Args:
        city: City name
        datetime_str: Target datetime (ISO format)
    
    Returns:
        Dictionary with forecast data
    """
    current = get_current_weather(city, datetime_str)
    
    return {
        "city": city,
        "target_time": datetime_str,
        "forecast": current,
        "min_temp": current["temperature"] - 5,
        "max_temp": current["temperature"] + 8,
        "summary": _get_temp_summary(current["temperature"])
    }


def get_weather_smart(city: str, datetime_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Get weather with caching to reduce API calls.
    Cache is valid for 30 minutes.
    
    Args:
        city: City name
        datetime_str: Optional datetime string
    
    Returns:
        Cached or fresh weather data
    """
    cache_key = f"{city}_{datetime_str or 'current'}"
    now = datetime.now()
    
    if cache_key in weather_cache:
        cached_data = weather_cache[cache_key]
        cache_time = datetime.fromisoformat(cached_data["cached_at"])
        
        if now - cache_time < timedelta(minutes=30):
            cached_data["from_cache"] = True
            return cached_data
    
    weather_data = get_current_weather(city, datetime_str)
    weather_data["cached_at"] = now.isoformat()
    weather_data["from_cache"] = False
    
    weather_cache[cache_key] = weather_data
    
    return weather_data


def _get_temp_summary(temp: float) -> str:
    """Get temperature summary label."""
    if temp < 32:
        return "freezing"
    elif temp < 50:
        return "cold"
    elif temp < 65:
        return "cool"
    elif temp < 75:
        return "mild"
    elif temp < 85:
        return "warm"
    else:
        return "hot"
