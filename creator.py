"""
Creator Profile Model for consistency across scenes.
Ensures non-sexualized, authentic fashion and lifestyle presentation.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class CreatorProfile:
    creator_id: str = "creator_01"
    name: str = "Aria"
    age_range: str = "22-26"
    general_appearance: str = "Graceful Indian urban creator, natural warm undertone, expressive smiling eyes"
    hair_type: str = "Dark brown soft natural waves"
    hairstyle: str = "Open shoulder-length waves with soft natural parting"
    outfit: str = "Western chic tailored pastel blazer with pleated trousers"
    footwear: str = "Minimalist nude block heels with firm ground contact"
    accessories: str = "Delicate gold pendant, sleek smartwatch, structured half-moon handbag"
    personality: str = "Warm, enthusiastic, relatable bestie with confident poise"
    mood_style: str = "Upbeat, aspirational, candid"
    body_language: str = "Dynamic natural stride, fluid gestures, engaging eye contact with lens"
    visual_style: str = "Clean, vibrant daylight, 4k photorealistic cinematic"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreatorProfile":
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
