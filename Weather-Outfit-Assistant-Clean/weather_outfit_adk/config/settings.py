import os
from typing import Optional


class Settings:
    """Application configuration settings."""
    
    def __init__(self):
        self.weather_api_key: Optional[str] = os.getenv("RAPIDAPI_KEY")
        self.google_cloud_project: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.default_model: str = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash-exp")
        self.enable_caching: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    def validate(self) -> bool:
        """Check if required settings are present."""
        if not self.weather_api_key:
            print("⚠️  RAPIDAPI_KEY not set - using mock weather data")
        
        if not self.google_cloud_project:
            print("ℹ️  GOOGLE_CLOUD_PROJECT not set - required for deployment")
            return False
        
        return True


settings = Settings()
