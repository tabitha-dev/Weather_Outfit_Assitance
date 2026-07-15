from typing import Dict, Any, Optional


def check_safety(
    temperature: float,
    wind_speed: float,
    rain_chance: float,
    condition: str = ""
) -> Dict[str, Any]:
    """
    Check weather conditions for safety concerns and generate warnings.
    
    Args:
        temperature: Temperature in Fahrenheit
        wind_speed: Wind speed in mph
        rain_chance: Rain probability (0-100)
        condition: Weather condition description
    
    Returns:
        Dictionary with risk_level (none, low, medium, high) and safety_message
    """
    risk_level = "none"
    warnings = []
    
    if temperature < 20:
        risk_level = "high"
        warnings.append("⚠️ Extreme cold warning: Protect your ears, hands, and face. Limit outdoor exposure.")
    elif temperature < 32:
        risk_level = "medium"
        warnings.append("❄️ Freezing temperatures: Wear warm layers and watch for ice on walkways.")
    
    if temperature > 95:
        risk_level = "high"
        warnings.append("🌡️ Extreme heat warning: Stay hydrated, wear light colors, and avoid prolonged sun exposure.")
    elif temperature > 85:
        risk_level = "medium"
        warnings.append("☀️ Hot weather: Drink plenty of water and take breaks in shade.")
    
    if wind_speed > 25:
        risk_level = "high" if risk_level != "high" else "high"
        warnings.append("💨 Strong winds: Secure loose items and avoid using umbrellas.")
    elif wind_speed > 15:
        if risk_level == "none":
            risk_level = "low"
        warnings.append("🌬️ Windy conditions: Consider a windproof jacket.")
    
    if rain_chance > 70 or "storm" in condition.lower() or "thunder" in condition.lower():
        risk_level = "high" if risk_level != "high" else "high"
        warnings.append("⛈️ Storm warning: Carry rain gear and avoid open areas during lightning.")
    elif rain_chance > 50:
        if risk_level == "none":
            risk_level = "low"
        warnings.append("🌧️ High chance of rain: Bring an umbrella or rain jacket.")
    
    if "snow" in condition.lower():
        risk_level = "medium" if risk_level == "none" else "high"
        warnings.append("🌨️ Snow expected: Dress warmly and watch for slippery conditions.")
    
    safety_message = " ".join(warnings) if warnings else None
    
    return {
        "risk_level": risk_level,
        "safety_message": safety_message,
        "has_warnings": len(warnings) > 0
    }
