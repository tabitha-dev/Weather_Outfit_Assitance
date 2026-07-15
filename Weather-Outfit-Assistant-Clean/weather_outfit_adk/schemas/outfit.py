from pydantic import BaseModel, Field
from typing import Optional


class ActivityContext(BaseModel):
    category: str = Field(description="Activity category: work, casual, sports, formal")
    formality_level: str = Field(description="Formality: casual, business_casual, formal")
    movement_level: str = Field(description="Movement intensity: low, medium, high")
    notes: Optional[str] = Field(default=None, description="Additional context")


class OutfitPlan(BaseModel):
    top: str = Field(description="Top layer recommendation (e.g., t-shirt, sweater)")
    bottom: str = Field(description="Bottom recommendation (e.g., jeans, shorts)")
    outer_layer: Optional[str] = Field(default=None, description="Jacket or coat if needed")
    footwear: str = Field(description="Shoe recommendation")
    accessories: list[str] = Field(default_factory=list, description="Accessories like umbrella, hat, scarf")
    notes: str = Field(description="Explanation and reasoning for the outfit")
