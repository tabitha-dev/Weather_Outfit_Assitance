"""Tools for managing user preferences and memory."""
from typing import Dict, Any, Optional
from ..memory.user_memory import UserMemory
from ..schemas.memory import PersonaType, ComfortProfile

# Global memory instance (in production, this would be a database or Agent Engine memory)
user_memory = UserMemory()


def get_user_preferences(user_id: str = "default_user") -> Dict[str, Any]:
    """
    Retrieve user preferences from memory.
    
    Args:
        user_id: Unique user identifier (defaults to "default_user" for demo)
    
    Returns:
        Dictionary with user preferences including persona, comfort_profile, default_city, style_notes
    """
    prefs = user_memory.get_preferences(user_id)
    return {
        "persona": prefs.persona.value,
        "comfort_profile": prefs.comfort_profile.value,
        "default_city": prefs.default_city,
        "style_notes": prefs.style_notes
    }


def update_user_preferences(
    user_id: str = "default_user",
    persona: Optional[str] = None,
    comfort_profile: Optional[str] = None,
    default_city: Optional[str] = None,
    style_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update user preferences in memory.
    
    Args:
        user_id: Unique user identifier
        persona: Style persona (practical, fashion, kid_friendly)
        comfort_profile: Temperature sensitivity (runs_cold, neutral, runs_hot)
        default_city: Default city for weather queries
        style_notes: Additional style preferences
    
    Returns:
        Updated preferences dictionary
    """
    # Convert string inputs to enum types if provided
    persona_enum = PersonaType(persona) if persona else None
    comfort_enum = ComfortProfile(comfort_profile) if comfort_profile else None
    
    prefs = user_memory.update_preferences(
        user_id=user_id,
        persona=persona_enum,
        comfort_profile=comfort_enum,
        default_city=default_city,
        style_notes=style_notes
    )
    
    return {
        "persona": prefs.persona.value,
        "comfort_profile": prefs.comfort_profile.value,
        "default_city": prefs.default_city,
        "style_notes": prefs.style_notes,
        "message": "Preferences updated successfully"
    }


# Expose the memory instance for direct access if needed
def get_memory_instance() -> UserMemory:
    """Get the global UserMemory instance."""
    return user_memory
