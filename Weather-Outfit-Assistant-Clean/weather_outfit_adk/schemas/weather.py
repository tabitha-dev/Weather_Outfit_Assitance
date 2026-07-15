from pydantic import BaseModel, Field
from typing import Optional


class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Fahrenheit")
    feels_like: float = Field(description="Feels like temperature in Fahrenheit")
    condition: str = Field(description="Weather condition (e.g., clear, cloudy, rain)")
    rain_chance: float = Field(description="Chance of rain as percentage (0-100)")
    wind_speed: float = Field(description="Wind speed in mph")
    humidity: Optional[float] = Field(default=None, description="Humidity percentage")
    timestamp: str = Field(description="Time of forecast")


class ForecastData(BaseModel):
    city: str = Field(description="City name")
    current: WeatherData = Field(description="Current weather conditions")
    min_temp: Optional[float] = Field(default=None, description="Minimum temperature for the day")
    max_temp: Optional[float] = Field(default=None, description="Maximum temperature for the day")
    summary: str = Field(description="Brief weather summary (e.g., 'mild', 'cold', 'hot')")
