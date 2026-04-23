from pydantic import BaseModel, Field

from app.models.message import Message
from app.models.persona import Demographics, Interest


class AgentState(BaseModel):
    session_id: str
    messages: list[Message] = Field(default_factory=list)
    current_node: str = "greeting"
    first_name: str | None = None
    demographics: Demographics | None = None
    demographics_partial: dict[str, str | int] = Field(default_factory=dict)
    demographics_pending_field: str | None = "first_name"
    dimension_scores: dict[str, list[float]] = Field(default_factory=dict)
    interests_detected: list[str] = Field(default_factory=list)
    interest_probed: Interest | None = None
    interest_to_probe_topic: str | None = None
    values_ranked: list[str] = Field(default_factory=list)
    dealbreakers: list[str] = Field(default_factory=list)
    complete: bool = False
