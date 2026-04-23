from __future__ import annotations

from app.models.persona import Personality, PersonalityDimensions


def _avg(values: list[float]) -> float:
    if not values:
        return 0.5
    return sum(values) / len(values)


def derive_mbti(dimension_scores: dict[str, list[float]]) -> Personality:
    """Derive MBTI letter + continuous dimensions from accumulated scores.

    Rule: for each of extraversion/intuition/thinking/judging, average the
    collected scores (default 0.5 if missing). If avg >= 0.5, use the first
    MBTI letter; else the second.
    """
    e = _avg(dimension_scores.get("extraversion", []))
    n = _avg(dimension_scores.get("intuition", []))
    t = _avg(dimension_scores.get("thinking", []))
    j = _avg(dimension_scores.get("judging", []))

    mbti = (
        ("E" if e >= 0.5 else "I")
        + ("N" if n >= 0.5 else "S")
        + ("T" if t >= 0.5 else "F")
        + ("J" if j >= 0.5 else "P")
    )

    return Personality(
        mbti=mbti,
        dimensions=PersonalityDimensions(
            extraversion=e, intuition=n, thinking=t, judging=j
        ),
    )
