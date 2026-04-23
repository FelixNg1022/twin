from typing import Literal

from pydantic import BaseModel, Field


class ProbeOutput(BaseModel):
    """Merged output of a scoring probe node. One Claude call per turn."""

    scores: dict[str, float] = Field(
        description="Per-dimension scores in [0, 1]. Keys are dimension names like "
        "'extraversion', 'intuition', 'thinking', 'judging'. Higher = first MBTI "
        "letter (E/N/T/J).",
    )
    evidence: str = Field(
        description="One-sentence justification for the scores, grounded in the "
        "user's last response. Written in third person.",
    )
    interests_detected: list[str] = Field(
        default_factory=list,
        description="Topics the user mentioned that could be probed further "
        "(e.g., 'hiking', 'indie music'). Use generic topic names, not full "
        "sentences.",
    )
    interest_to_probe: str | None = Field(
        default=None,
        description="If any detected interest is distinctive enough to warrant a "
        "follow-up question (not 'watching TV' or 'scrolling phone'), pick exactly "
        "one. Otherwise null. Only used by probe_weekend.",
    )
    next_message: str = Field(
        description="The next message to send to the user. Natural iMessage "
        "texture: short, lowercase okay, no form-style phrasing.",
    )


class InterestProbeOutput(BaseModel):
    """Output of the adaptive_interest node — no scoring, just detail mining."""

    specific_details: str = Field(
        description="Specific factual details about the interest extracted from "
        "the user's response. E.g., 'solo multi-day trips, last one West Coast "
        "Trail'. Empty string if user gave a vague answer.",
    )
    depth_signal: Literal["low", "medium", "high"] = Field(
        description="'high' if user gave specific details (place/time/routine), "
        "'medium' if user gave a concrete detail but not fully specific, "
        "'low' if user just reconfirmed without elaboration.",
    )
    next_message: str = Field(
        description="Short acknowledgement and pivot back to the main flow. "
        "Natural texture.",
    )
