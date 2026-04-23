from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Demographics(BaseModel):
    age: int
    gender: str
    sexual_orientation: str
    campus: str
    travel_radius_km: int


class PersonalityDimensions(BaseModel):
    """MBTI-oriented continuous scores. The first four dimensions map to the
    four MBTI axes used to derive the letter. `neuroticism` is the fifth Big
    Five axis — probed behaviorally but not reflected in the MBTI letter.
    """

    extraversion: float = Field(ge=0.0, le=1.0)
    intuition: float = Field(ge=0.0, le=1.0)
    thinking: float = Field(ge=0.0, le=1.0)
    judging: float = Field(ge=0.0, le=1.0)
    neuroticism: float = Field(ge=0.0, le=1.0, default=0.5)


class Personality(BaseModel):
    mbti: str = Field(pattern=r"^[EI][SN][TF][JP]$")
    dimensions: PersonalityDimensions


class Interest(BaseModel):
    topic: str
    depth_signal: Literal["low", "medium", "high"]
    specific_details: str = ""


class Persona(BaseModel):
    session_id: str
    summary: str
    demographics: Demographics
    personality: Personality
    values_ranked: list[str]
    interests: list[Interest]
    dealbreakers: list[str]
    conversation_hooks: list[str]
    created_at: datetime
