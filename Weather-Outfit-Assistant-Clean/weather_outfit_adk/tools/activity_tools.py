from typing import Dict, Any
from ..schemas.outfit import ActivityContext


def classify_activity(activity_text: str) -> Dict[str, Any]:
    """
    Classify user activity into structured context.
    
    Args:
        activity_text: Free text describing the activity (e.g., "hiking", "office meeting", "date night")
    
    Returns:
        Dictionary with activity category, formality_level, movement_level, and notes
    """
    activity_lower = activity_text.lower()
    
    activity_rules = {
        "work": {
            "keywords": ["work", "office", "meeting", "presentation", "business"],
            "formality": "business_casual",
            "movement": "low"
        },
        "sports": {
            "keywords": ["hike", "hiking", "bike", "biking", "cycling", "run", "running", "gym", "workout", "exercise"],
            "formality": "casual",
            "movement": "high"
        },
        "formal": {
            "keywords": ["date", "dinner", "restaurant", "party", "event", "wedding", "formal"],
            "formality": "formal",
            "movement": "low"
        },
        "casual": {
            "keywords": ["walk", "walking", "shopping", "errands", "casual", "coffee", "hanging out"],
            "formality": "casual",
            "movement": "medium"
        }
    }
    
    category = "casual"
    formality = "casual"
    movement = "medium"
    notes = ""
    
    for act_cat, rules in activity_rules.items():
        if any(keyword in activity_lower for keyword in rules["keywords"]):
            category = act_cat
            formality = rules["formality"]
            movement = rules["movement"]
            
            if category == "sports":
                notes = "Recommend flexible, breathable clothing"
            elif category == "formal":
                notes = "Prioritize style and appearance"
            elif category == "work":
                notes = "Balance comfort and professionalism"
            
            break
    
    return {
        "category": category,
        "formality_level": formality,
        "movement_level": movement,
        "notes": notes or "General outdoor activity"
    }
