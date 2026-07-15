from typing import Dict, Optional
from ..schemas.memory import UserPreferences, PersonaType, ComfortProfile


class UserMemory:
    """
    Manages long-term user preferences and profile data.
    In production, this would connect to a database or Agent Engine memory API.
    """
    
    def __init__(self):
        self._memory_store: Dict[str, UserPreferences] = {}
    
    def get_preferences(self, user_id: str) -> UserPreferences:
        """
        Retrieve user preferences from memory.
        
        Args:
            user_id: Unique user identifier
        
        Returns:
            UserPreferences object with stored or default preferences
        """
        if user_id not in self._memory_store:
            self._memory_store[user_id] = UserPreferences()
        
        return self._memory_store[user_id]
    
    def update_preferences(
        self,
        user_id: str,
        persona: Optional[PersonaType] = None,
        comfort_profile: Optional[ComfortProfile] = None,
        default_city: Optional[str] = None,
        style_notes: Optional[str] = None
    ) -> UserPreferences:
        """
        Update user preferences in memory.
        
        Args:
            user_id: Unique user identifier
            persona: Style persona preference
            comfort_profile: Temperature sensitivity
            default_city: Default city for weather queries
            style_notes: Additional style preferences
        
        Returns:
            Updated UserPreferences object
        """
        current_prefs = self.get_preferences(user_id)
        
        if persona is not None:
            current_prefs.persona = persona
        if comfort_profile is not None:
            current_prefs.comfort_profile = comfort_profile
        if default_city is not None:
            current_prefs.default_city = default_city
        if style_notes is not None:
            current_prefs.style_notes = style_notes
        
        self._memory_store[user_id] = current_prefs
        
        return current_prefs
    
    def clear_preferences(self, user_id: str) -> None:
        """Clear preferences for a user."""
        if user_id in self._memory_store:
            del self._memory_store[user_id]
