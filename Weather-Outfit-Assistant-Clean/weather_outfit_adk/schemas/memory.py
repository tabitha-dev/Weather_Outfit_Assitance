from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PersonaType(str, Enum):
    PRACTICAL = "practical"
    FASHION = "fashion"
    KID_FRIENDLY = "kid_friendly"


class ComfortProfile(str, Enum):
    RUNS_COLD = "runs_cold"
    NEUTRAL = "neutral"
    RUNS_HOT = "runs_hot"


class UserPreferences(BaseModel):
    persona: PersonaType = Field(default=PersonaType.PRACTICAL, description="Style persona")
    comfort_profile: ComfortProfile = Field(default=ComfortProfile.NEUTRAL, description="Temperature sensitivity")
    default_city: Optional[str] = Field(default=None, description="User's default city")
    style_notes: Optional[str] = Field(default=None, description="Additional style preferences")
