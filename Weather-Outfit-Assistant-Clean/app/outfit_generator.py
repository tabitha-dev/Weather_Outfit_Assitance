"""
Comprehensive Weather and Activity-Based Outfit Generation System
Supports: Sunny/Warm, Hot/Humid, Cold, Rainy, Snowy, Windy
Activities: Hiking, Formal, Travel, Outdoor Sports, Beach, Commuting
"""

def determine_weather_category(temperature, condition):
    """Categorize weather conditions"""
    condition_lower = condition.lower()
    
    if temperature > 80:
        return 'hot_humid' if any(x in condition_lower for x in ['humid', 'muggy', 'sticky']) else 'sunny_warm'
    elif 'snow' in condition_lower or temperature < 32:
        return 'snowy'
    elif any(x in condition_lower for x in ['rain', 'drizzle', 'shower', 'precipitation']):
        return 'rainy'
    elif any(x in condition_lower for x in ['wind', 'gust', 'breezy']):
        return 'windy'
    elif temperature < 45:
        return 'cold'
    elif temperature > 70:
        return 'sunny_warm'
    else:
        return 'mild'


def get_primary_color(color_palette):
    """Get primary color preference"""
    prefers_neutral = any('neutral' in c.lower() for c in color_palette)
    prefers_blues = any('blue' in c.lower() for c in color_palette)
    prefers_earth = any('earth' in c.lower() for c in color_palette)
    
    if prefers_neutral:
        return 'neutral'
    elif prefers_blues:
        return 'blues'
    elif prefers_earth:
        return 'earth'
    else:
        return 'neutral'


def generate_weather_based_outfit(temperature, condition, color_pref):
    """Generate outfit items based on weather conditions"""
    weather_type = determine_weather_category(temperature, condition)
    items = []
    
    # Color mappings
    colors = {
        'neutral': {'light': 'white', 'dark': 'black', 'accent': 'gray'},
        'blues': {'light': 'light blue', 'dark': 'navy', 'accent': 'blue'},
        'earth': {'light': 'tan', 'dark': 'brown', 'accent': 'olive'}
    }
    c = colors.get(color_pref, colors['neutral'])
    
    # SUNNY AND WARM (70-80°F)
    if weather_type == 'sunny_warm':
        items.extend([
            {"category": "Top", "name": "Light Cotton Shirt", "description": f"{c['light'].capitalize()} breathable cotton"},
            {"category": "Bottoms", "name": "Shorts", "description": f"{c['dark'].capitalize()} cotton shorts"},
            {"category": "Footwear", "name": "Breathable Sneakers", "description": f"{c['light'].capitalize()} mesh sneakers or sandals"},
            {"category": "Accessory", "name": "Sunglasses", "description": "UV protection sunglasses"},
            {"category": "Accessory", "name": "Sun Hat", "description": f"{c['accent'].capitalize()} wide-brim hat"},
            {"category": "Accessory", "name": "Sunscreen", "description": "SPF 30+ light sunscreen"},
            {"category": "Accessory", "name": "Water Bottle", "description": "Reusable insulated bottle"}
        ])
    
    # HOT AND HUMID (>80°F)
    elif weather_type == 'hot_humid':
        items.extend([
            {"category": "Top", "name": "Sleeveless Top", "description": f"{c['light'].capitalize()} moisture-wicking tank"},
            {"category": "Bottoms", "name": "Loose Shorts", "description": f"{c['dark'].capitalize()} lightweight shorts"},
            {"category": "Footwear", "name": "Open Sandals", "description": f"{c['dark'].capitalize()} comfortable sandals"},
            {"category": "Accessory", "name": "Sweat-Resistant Sunscreen", "description": "SPF 50+ sport sunscreen"},
            {"category": "Accessory", "name": "Light Hat", "description": f"{c['accent'].capitalize()} breathable cap"},
            {"category": "Accessory", "name": "Cooling Towel", "description": "Microfiber cooling towel"},
            {"category": "Accessory", "name": "Water Bottle", "description": "Large hydration bottle"}
        ])
    
    # COLD (<45°F)
    elif weather_type == 'cold':
        items.extend([
            {"category": "Base Layer", "name": "Thermal Top", "description": f"{c['dark'].capitalize()} thermal undershirt"},
            {"category": "Top", "name": "Wool Sweater", "description": f"{c['accent'].capitalize()} warm sweater"},
            {"category": "Outerwear", "name": "Thick Jacket", "description": f"{c['dark'].capitalize()} insulated jacket"},
            {"category": "Bottoms", "name": "Warm Pants", "description": f"{c['dark'].capitalize()} lined pants"},
            {"category": "Footwear", "name": "Insulated Boots", "description": f"{c['dark'].capitalize()} winter boots"},
            {"category": "Accessory", "name": "Wool Socks", "description": f"{c['dark'].capitalize()} thick wool socks"},
            {"category": "Accessory", "name": "Gloves", "description": f"{c['dark'].capitalize()} insulated gloves"},
            {"category": "Accessory", "name": "Scarf", "description": f"{c['accent'].capitalize()} warm scarf"},
            {"category": "Accessory", "name": "Warm Hat", "description": f"{c['accent'].capitalize()} wool beanie"}
        ])
    
    # RAINY
    elif weather_type == 'rainy':
        items.extend([
            {"category": "Outerwear", "name": "Waterproof Jacket", "description": f"{c['dark'].capitalize()} rain jacket with hood"},
            {"category": "Bottoms", "name": "Quick-Dry Pants", "description": f"{c['dark'].capitalize()} water-resistant pants"},
            {"category": "Footwear", "name": "Water-Resistant Shoes", "description": f"{c['dark'].capitalize()} waterproof boots"},
            {"category": "Accessory", "name": "Umbrella", "description": "Compact windproof umbrella"},
            {"category": "Accessory", "name": "Waterproof Hat", "description": f"{c['accent'].capitalize()} rain hat"},
            {"category": "Accessory", "name": "Backpack Rain Cover", "description": "Waterproof pack cover"}
        ])
    
    # SNOWY (<32°F or snow condition)
    elif weather_type == 'snowy':
        items.extend([
            {"category": "Outerwear", "name": "Insulated Coat", "description": f"{c['dark'].capitalize()} heavy winter coat"},
            {"category": "Base Layer", "name": "Thermal Layers", "description": f"{c['dark'].capitalize()} full thermal set"},
            {"category": "Bottoms", "name": "Snow Pants", "description": f"{c['dark'].capitalize()} waterproof snow pants"},
            {"category": "Footwear", "name": "Snow Boots", "description": f"{c['dark'].capitalize()} insulated snow boots"},
            {"category": "Accessory", "name": "Waterproof Gloves", "description": f"{c['dark'].capitalize()} ski gloves"},
            {"category": "Accessory", "name": "Warm Hat", "description": f"{c['accent'].capitalize()} lined winter hat"},
            {"category": "Accessory", "name": "Face Covering", "description": f"{c['dark'].capitalize()} neck warmer or balaclava"},
            {"category": "Accessory", "name": "Snow Goggles", "description": "UV protection snow goggles"}
        ])
    
    # WINDY
    elif weather_type == 'windy':
        items.extend([
            {"category": "Outerwear", "name": "Wind-Resistant Jacket", "description": f"{c['dark'].capitalize()} windbreaker"},
            {"category": "Base Layer", "name": "Windproof Base Layer", "description": f"{c['dark'].capitalize()} thermal layer"},
            {"category": "Bottoms", "name": "Secure Pants", "description": f"{c['dark'].capitalize()} fitted pants"},
            {"category": "Footwear", "name": "Closed Shoes", "description": f"{c['dark'].capitalize()} secure sneakers"},
            {"category": "Accessory", "name": "Secure Hat", "description": f"{c['accent'].capitalize()} fitted cap or headband"},
            {"category": "Accessory", "name": "Windproof Sunglasses", "description": "Secure wrap-around eyewear"},
            {"category": "Accessory", "name": "Lip Balm", "description": "Moisturizing lip protection"}
        ])
    
    # MILD (Default for moderate weather 45-70°F)
    else:
        items.extend([
            {"category": "Top", "name": "Long-Sleeve Shirt", "description": f"{c['accent'].capitalize()} cotton shirt"},
            {"category": "Bottoms", "name": "Jeans", "description": f"{c['dark'].capitalize()} comfortable jeans"},
            {"category": "Footwear", "name": "Sneakers", "description": f"{c['light'].capitalize()} casual sneakers"},
            {"category": "Outerwear", "name": "Light Jacket", "description": f"{c['accent'].capitalize()} versatile jacket"},
            {"category": "Accessory", "name": "Watch", "description": f"{c['accent'].capitalize()} timepiece"},
            {"category": "Accessory", "name": "Socks", "description": f"{c['dark'].capitalize()} cotton socks"},
            {"category": "Accessory", "name": "Belt", "description": f"{c['dark'].capitalize()} casual belt"}
        ])
    
    return items


def generate_formal_outfit_weather_aware(temperature, condition, color_pref):
    """Generate weather-specific formal outfit"""
    items = []
    
    colors = {
        'neutral': {'light': 'white', 'dark': 'black', 'accent': 'gray'},
        'blues': {'light': 'light blue', 'dark': 'navy', 'accent': 'blue'},
        'earth': {'light': 'tan', 'dark': 'brown', 'accent': 'olive'}
    }
    c = colors.get(color_pref, colors['neutral'])
    condition_lower = condition.lower()
    
    # FORMAL IN COLD WEATHER (<50°F)
    if temperature < 50:
        items.extend([
            {"category": "Suit", "name": "Wool Suit", "description": f"{c['dark'].capitalize()} wool suit"},
            {"category": "Top", "name": "Long-Sleeve Button Shirt", "description": f"{c['light'].capitalize()} dress shirt"},
            {"category": "Base Layer", "name": "Knit Sweater", "description": f"{c['accent'].capitalize()} thin thermal layer"},
            {"category": "Outerwear", "name": "Overcoat", "description": f"{c['dark'].capitalize()} thick overcoat"},
            {"category": "Accessory", "name": "Warm Scarf", "description": f"{c['accent'].capitalize()} formal scarf"},
            {"category": "Accessory", "name": "Leather Gloves", "description": f"{c['dark'].capitalize()} dress gloves"},
            {"category": "Footwear", "name": "Dress Shoes", "description": f"{c['dark'].capitalize()} leather with warm socks"}
        ])
    
    # FORMAL IN RAINY WEATHER
    elif 'rain' in condition_lower:
        items.extend([
            {"category": "Outerwear", "name": "Water-Resistant Coat", "description": f"{c['dark'].capitalize()} formal raincoat"},
            {"category": "Footwear", "name": "Water-Resistant Dress Shoes", "description": f"{c['dark'].capitalize()} waterproof leather"},
            {"category": "Accessory", "name": "Compact Umbrella", "description": "Professional black umbrella"},
            {"category": "Bottoms", "name": "Quick-Dry Dress Pants", "description": f"{c['dark'].capitalize()} water-resistant"},
            {"category": "Top", "name": "Button Shirt", "description": f"{c['light'].capitalize()} formal shirt"},
            {"category": "Outerwear", "name": "Blazer", "description": f"{c['dark'].capitalize()} smooth finish blazer"}
        ])
    
    # FORMAL IN SUNNY/WARM WEATHER (>70°F)
    elif temperature > 70 or 'sunny' in condition_lower or 'clear' in condition_lower:
        items.extend([
            {"category": "Suit", "name": "Light-Colored Suit", "description": f"{c['light'].capitalize()} linen or cotton"},
            {"category": "Top", "name": "Cotton Shirt", "description": f"{c['light'].capitalize()} breathable dress shirt"},
            {"category": "Outerwear", "name": "Light Blazer", "description": f"{c['accent'].capitalize()} breathable blazer"},
            {"category": "Accessory", "name": "Polarized Sunglasses", "description": "Professional eyewear"},
            {"category": "Footwear", "name": "Dress Shoes", "description": f"{c['dark'].capitalize()} with breathable socks"},
            {"category": "Accessory", "name": "Dress Hat", "description": f"{c['accent'].capitalize()} optional formal hat"}
        ])
    
    # FORMAL IN WARM WEATHER (50-70°F, default)
    else:
        items.extend([
            {"category": "Suit", "name": "Lightweight Suit", "description": f"{c['dark'].capitalize()} breathable fabric"},
            {"category": "Top", "name": "Cotton Button Shirt", "description": f"{c['light'].capitalize()} dress shirt"},
            {"category": "Base Layer", "name": "Moisture-Wicking Undershirt", "description": "Thin breathable layer"},
            {"category": "Outerwear", "name": "Light Blazer", "description": f"{c['accent'].capitalize()} versatile jacket"},
            {"category": "Footwear", "name": "Dress Shoes", "description": f"{c['dark'].capitalize()} with thin socks"},
            {"category": "Accessory", "name": "Watch", "description": "Classic dress watch"}
        ])
    
    return items


def generate_activity_based_additions(activity, color_pref):
    """Generate additional items based on specific activities"""
    items = []
    
    # Color mappings
    colors = {
        'neutral': {'light': 'white', 'dark': 'black', 'accent': 'gray'},
        'blues': {'light': 'light blue', 'dark': 'navy', 'accent': 'blue'},
        'earth': {'light': 'tan', 'dark': 'brown', 'accent': 'olive'}
    }
    c = colors.get(color_pref, colors['neutral'])
    
    activity_lower = activity.lower()
    
    # HIKING
    if 'hiking' in activity_lower or 'camping' in activity_lower:
        items.extend([
            {"category": "Top", "name": "Moisture-Wicking Shirt", "description": f"{c['accent'].capitalize()} breathable long-sleeve"},
            {"category": "Footwear", "name": "Trail Boots", "description": f"{c['dark'].capitalize()} sturdy hiking boots"},
            {"category": "Bottoms", "name": "Trekking Pants", "description": f"{c['dark'].capitalize()} light hiking pants"},
            {"category": "Accessory", "name": "Backpack", "description": f"{c['accent'].capitalize()} 20L day pack"},
            {"category": "Accessory", "name": "Water Reservoir", "description": "2L hydration bladder"},
            {"category": "Accessory", "name": "Trail Hat", "description": f"{c['accent'].capitalize()} sun protection hat"},
            {"category": "Accessory", "name": "Bug Spray", "description": "DEET insect repellent"},
            {"category": "Accessory", "name": "Trail Gloves", "description": f"{c['dark'].capitalize()} light gloves"},
            {"category": "Accessory", "name": "Trail Snacks", "description": "Energy bars and nuts"}
        ])
    
    # FORMAL - handled separately with weather awareness
    elif 'formal' in activity_lower:
        # Formal outfits are generated weather-aware in the main function
        # This is just a placeholder that gets replaced
        items.extend([
            {"category": "Top", "name": "Button Shirt", "description": f"{c['light'].capitalize()} dress shirt"},
            {"category": "Bottoms", "name": "Tailored Pants", "description": f"{c['dark'].capitalize()} dress pants"},
            {"category": "Outerwear", "name": "Blazer", "description": f"{c['dark'].capitalize()} suit jacket"},
            {"category": "Footwear", "name": "Formal Shoes", "description": f"{c['dark'].capitalize()} leather shoes"}
        ])
    
    # TRAVEL
    elif 'travel' in activity_lower:
        items.extend([
            {"category": "Top", "name": "Comfortable Travel Top", "description": f"{c['accent'].capitalize()} soft cotton"},
            {"category": "Bottoms", "name": "Stretch Pants", "description": f"{c['dark'].capitalize()} flexible travel pants"},
            {"category": "Outerwear", "name": "Light Travel Jacket", "description": f"{c['accent'].capitalize()} packable jacket"},
            {"category": "Footwear", "name": "Slip-On Shoes", "description": f"{c['dark'].capitalize()} easy security shoes"},
            {"category": "Accessory", "name": "Neck Pillow", "description": "Travel comfort pillow"},
            {"category": "Accessory", "name": "Eye Mask", "description": "Sleep mask"},
            {"category": "Accessory", "name": "Compact Toiletries", "description": "TSA-approved kit"},
            {"category": "Accessory", "name": "Water Bottle", "description": "Collapsible bottle"},
            {"category": "Accessory", "name": "Day Bag", "description": f"{c['dark'].capitalize()} lightweight backpack"},
            {"category": "Accessory", "name": "Document Holder", "description": "Travel organizer"}
        ])
    
    # OUTDOOR SPORTS
    elif 'sport' in activity_lower or 'gym' in activity_lower or 'exercise' in activity_lower:
        items.extend([
            {"category": "Top", "name": "Athletic Shirt", "description": f"{c['accent'].capitalize()} moisture-wicking top"},
            {"category": "Bottoms", "name": "Sport Shorts", "description": f"{c['dark'].capitalize()} flexible athletic shorts"},
            {"category": "Footwear", "name": "Sport Shoes", "description": f"{c['accent'].capitalize()} activity-specific shoes"},
            {"category": "Accessory", "name": "Sports Visor", "description": f"{c['accent'].capitalize()} sun visor"},
            {"category": "Accessory", "name": "Sweatband", "description": f"{c['accent'].capitalize()} moisture control band"},
            {"category": "Accessory", "name": "Sports Sunglasses", "description": "Wrap-around protection"},
            {"category": "Accessory", "name": "Hydration Bottle", "description": "Sports water bottle"}
        ])
    
    # BEACH
    elif 'beach' in activity_lower or 'pool' in activity_lower:
        items.extend([
            {"category": "Swimwear", "name": "Swimsuit", "description": f"{c['accent'].capitalize()} swim attire"},
            {"category": "Top", "name": "Light Cover-Up", "description": f"{c['light'].capitalize()} beach cover"},
            {"category": "Footwear", "name": "Flip-Flops", "description": f"{c['accent'].capitalize()} beach sandals"},
            {"category": "Accessory", "name": "Beach Hat", "description": f"{c['accent'].capitalize()} straw sun hat"},
            {"category": "Accessory", "name": "Sunscreen", "description": "SPF 50+ waterproof"},
            {"category": "Accessory", "name": "Sunglasses", "description": "Polarized beach glasses"},
            {"category": "Accessory", "name": "Beach Towel", "description": f"{c['accent'].capitalize()} large towel"},
            {"category": "Accessory", "name": "Waterproof Bag", "description": "Beach tote"}
        ])
    
    # COMMUTING
    elif 'commut' in activity_lower or 'work' in activity_lower or 'city' in activity_lower:
        items.extend([
            {"category": "Footwear", "name": "Comfortable Walking Shoes", "description": f"{c['dark'].capitalize()} supportive shoes"},
            {"category": "Outerwear", "name": "Weather Layer", "description": f"{c['accent'].capitalize()} appropriate outer layer"},
            {"category": "Accessory", "name": "Commute Bag", "description": f"{c['dark'].capitalize()} light tote or backpack"},
            {"category": "Accessory", "name": "Compact Umbrella", "description": "Travel umbrella"},
            {"category": "Accessory", "name": "Phone Power Bank", "description": "Portable charger"},
            {"category": "Accessory", "name": "Reusable Bottle", "description": "Eco-friendly bottle"}
        ])
    
    return items


def apply_physical_needs_adjustments(items, temperature, condition, physical_needs):
    """Placeholder - physical needs feature not yet implemented"""
    return items


def generate_comprehensive_outfit(temperature, condition, style_preferences, clothing_types, color_palette, activity=None, physical_needs=None):
    """
    Main function to generate comprehensive outfit recommendations
    Combines weather-based items with optional activity-based additions and physical needs
    Returns 6-10 items maximum for optimal UX
    
    Args:
        physical_needs: Dict with keys like 'mobility', 'foot_sensitivity', 'skin_sensitivity', 'transport'
    """
    # Determine primary color preference
    color_pref = get_primary_color(color_palette)
    
    # Default physical needs if not provided
    if physical_needs is None:
        physical_needs = {}
    
    # Special handling for FORMAL activity - completely weather-aware
    if activity and 'formal' in activity.lower():
        items = generate_formal_outfit_weather_aware(temperature, condition, color_pref)
        items = apply_physical_needs_adjustments(items, temperature, condition, physical_needs)
        return items[:10]
    
    # Generate base weather-appropriate outfit for non-formal activities
    items = generate_weather_based_outfit(temperature, condition, color_pref)
    
    # Apply physical needs adjustments to base outfit
    items = apply_physical_needs_adjustments(items, temperature, condition, physical_needs)
    
    # Add activity-specific items if activity is specified
    if activity:
        activity_items = generate_activity_based_additions(activity, color_pref)
        
        # Prioritize core weather items + selective activity additions
        # Keep essential weather items (always first 6 items)
        core_weather_items = items[:6]
        
        # For activity mode: Replace some weather accessories with activity-specific items
        # Merge avoiding duplicates by category+name
        existing_keys = {(item['category'], item['name']) for item in core_weather_items}
        combined = core_weather_items.copy()
        
        # Add activity items that don't duplicate existing categories/names
        for activity_item in activity_items:
            key = (activity_item['category'], activity_item['name'])
            if key not in existing_keys and len(combined) < 10:
                combined.append(activity_item)
                existing_keys.add(key)
        
        items = combined
    
    # Ensure we always return 6-10 items
    if len(items) < 6:
        # Pad with basic accessories if needed (shouldn't happen with current logic)
        items = items[:10]
    else:
        # Cap at exactly 10 items
        items = items[:10]
    
    return items
