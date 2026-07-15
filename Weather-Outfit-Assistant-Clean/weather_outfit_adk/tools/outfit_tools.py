from typing import Dict, Any, List, Optional


def plan_outfit(
    temperature: float,
    rain_chance: float,
    wind_speed: float,
    activity_category: str = "casual",
    formality_level: str = "casual",
    movement_level: str = "medium",
    persona: str = "practical",
    comfort_profile: str = "neutral"
) -> Dict[str, Any]:
    """
    Compute outfit recommendations based on weather and context.
    
    Args:
        temperature: Temperature in Fahrenheit
        rain_chance: Rain probability (0-100)
        wind_speed: Wind speed in mph
        activity_category: Type of activity (work, casual, sports, formal)
        formality_level: Required formality (casual, business_casual, formal)
        movement_level: Activity intensity (low, medium, high)
        persona: Style preference (practical, fashion, kid_friendly)
        comfort_profile: Temperature sensitivity (runs_cold, neutral, runs_hot)
    
    Returns:
        Dictionary with outfit plan including top, bottom, outer_layer, footwear, accessories, notes
    """
    adjusted_temp = _adjust_for_comfort(temperature, comfort_profile)
    
    top = _select_top(adjusted_temp, activity_category, formality_level)
    bottom = _select_bottom(adjusted_temp, activity_category, movement_level)
    outer_layer = _select_outer_layer(adjusted_temp, wind_speed, rain_chance, formality_level)
    footwear = _select_footwear(activity_category, formality_level, rain_chance)
    accessories = _select_accessories(rain_chance, wind_speed, adjusted_temp, activity_category)
    
    notes = _generate_notes(
        temperature, adjusted_temp, rain_chance, wind_speed,
        activity_category, persona, comfort_profile
    )
    
    return {
        "top": top,
        "bottom": bottom,
        "outer_layer": outer_layer,
        "footwear": footwear,
        "accessories": accessories,
        "notes": notes
    }


def _adjust_for_comfort(temp: float, comfort_profile: str) -> float:
    """Adjust perceived temperature based on comfort profile."""
    if comfort_profile == "runs_cold":
        return temp - 5
    elif comfort_profile == "runs_hot":
        return temp + 5
    return temp


def _select_top(temp: float, activity: str, formality: str) -> str:
    """Select appropriate top layer."""
    if formality == "formal":
        if temp < 60:
            return "dress shirt or blouse with sweater"
        return "dress shirt or blouse"
    
    if activity == "sports":
        return "moisture-wicking athletic shirt or tank"
    
    if temp < 40:
        return "long-sleeve thermal or henley"
    elif temp < 60:
        return "long-sleeve shirt or light sweater"
    elif temp < 75:
        return "t-shirt or short-sleeve shirt"
    else:
        return "light t-shirt or tank top"


def _select_bottom(temp: float, activity: str, movement: str) -> str:
    """Select appropriate bottom layer."""
    if activity == "sports":
        if temp < 50:
            return "athletic leggings or joggers"
        return "athletic shorts or breathable pants"
    
    if temp < 40:
        return "warm pants or jeans"
    elif temp < 65:
        return "jeans or casual pants"
    elif temp < 80:
        return "light pants or shorts"
    else:
        return "shorts or light skirt"


def _select_outer_layer(temp: float, wind: float, rain: float, formality: str) -> Optional[str]:
    """Select jacket or coat if needed."""
    if temp >= 75 and wind < 15 and rain < 30:
        return None
    
    needs_warmth = temp < 50
    needs_wind_protection = wind > 15
    needs_rain_protection = rain > 40
    
    if formality == "formal":
        if needs_rain_protection:
            return "dress coat with rain protection"
        elif needs_warmth:
            return "wool coat or blazer"
        return None
    
    if needs_rain_protection:
        if needs_warmth:
            return "insulated rain jacket"
        return "light rain jacket or windbreaker"
    
    if needs_warmth:
        if temp < 32:
            return "heavy winter coat"
        elif temp < 50:
            return "medium jacket or fleece"
        return "light jacket"
    
    if needs_wind_protection:
        return "windbreaker"
    
    return None


def _select_footwear(activity: str, formality: str, rain: float) -> str:
    """Select appropriate footwear."""
    if formality == "formal":
        if rain > 40:
            return "dress shoes (waterproof if possible)"
        return "dress shoes or heels"
    
    if activity == "sports":
        return "athletic shoes or trail shoes"
    
    if rain > 40:
        return "waterproof boots or rain boots"
    elif activity == "work":
        return "comfortable work shoes or loafers"
    
    return "sneakers or casual shoes"


def _select_accessories(rain: float, wind: float, temp: float, activity: str) -> List[str]:
    """Select accessories like umbrella, hat, scarf."""
    accessories = []
    
    if rain > 40:
        accessories.append("umbrella")
    
    if temp < 40:
        accessories.append("warm hat or beanie")
        accessories.append("scarf")
        if temp < 30:
            accessories.append("gloves")
    
    if wind > 20 and activity == "sports":
        accessories.append("windproof cap")
    
    if temp > 80:
        accessories.append("sunglasses")
        accessories.append("sunscreen")
    
    return accessories


def _generate_notes(
    orig_temp: float, adj_temp: float, rain: float, wind: float,
    activity: str, persona: str, comfort_profile: str
) -> str:
    """Generate outfit explanation."""
    notes = []
    
    if persona == "kid_friendly":
        if adj_temp < 50:
            notes.append("Bundle up warm - it's chilly out there!")
        elif rain > 40:
            notes.append("Don't forget your rain gear for puddle jumping!")
        else:
            notes.append("Perfect weather for fun outside!")
    elif persona == "fashion":
        notes.append("Layer colors and textures for a stylish look.")
        if rain > 40:
            notes.append("Rain doesn't mean sacrificing style - try a trendy rain jacket.")
    else:
        temp_desc = "cold" if adj_temp < 50 else "mild" if adj_temp < 70 else "warm"
        notes.append(f"Weather is {temp_desc} at {int(orig_temp)}°F.")
    
    if comfort_profile == "runs_cold":
        notes.append("Since you tend to feel cold, adding extra layers is recommended.")
    elif comfort_profile == "runs_hot":
        notes.append("Since you tend to feel warm, lighter options are better.")
    
    if activity == "sports":
        notes.append("Choose breathable, flexible clothing for movement.")
    elif activity == "formal":
        notes.append("Dress to impress while staying comfortable.")
    
    return " ".join(notes)
