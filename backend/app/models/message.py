from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["user", "assistant"]
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
