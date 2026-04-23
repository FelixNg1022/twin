from datetime import datetime

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from app.agent.prompts import load
from app.agent.state import AgentState
from app.channels.base import Channel
from app.config import settings
from app.models.message import Message
from app.models.persona import Demographics
from app.models.probe import ProbeOutput
from app.services.anthropic_client import get_client
from app.services.structured_call import structured_call


def _get_channel(config: RunnableConfig) -> Channel:
    configurable = config.get("configurable", {}) if config else {}
    channel = configurable.get("channel")
    if channel is None:
        raise RuntimeError("Channel not provided in config.configurable.channel")
    return channel


async def _send(state: AgentState, channel: Channel, text: str) -> None:
    """Deliver via channel AND append to state.messages for transcript."""
    await channel.deliver(state.session_id, text)
    state.messages.append(Message(role="assistant", text=text, created_at=datetime.utcnow()))


def _user_last_text(state: AgentState) -> str:
    for msg in reversed(state.messages):
        if msg.role == "user":
            return msg.text
    return ""


def _pending_user_input(state: AgentState) -> str:
    """Return the user's most recent message IF it hasn't been consumed yet.

    Fresh-entry rule: if the last message in state.messages is an assistant
    message, the prior user message has already been consumed by the previous
    node. This node should send its opening question rather than reprocess
    stale input.
    """
    if not state.messages:
        return ""
    if state.messages[-1].role != "user":
        return ""
    return state.messages[-1].text


# ---------- greeting ----------

async def greeting_node(state: AgentState, config: RunnableConfig) -> dict:
    """First turn: introduce Twin and ask for the user's first name."""
    channel = _get_channel(config)
    client = get_client()

    system = load("greeting")
    response = await client.messages.create(
        model=settings.anthropic_turn_model,
        max_tokens=200,
        system=system,
        messages=[{"role": "user", "content": "<BEGIN>"}],
    )
    text = "".join(block.text for block in response.content if block.type == "text").strip()

    await _send(state, channel, text)
    return {
        "messages": state.messages,
        "current_node": "collect_demographics",
        "demographics_pending_field": "first_name",
    }


# ---------- demographics ----------

_DEMOGRAPHIC_FIELDS = ("first_name", "age", "gender", "sexual_orientation", "campus", "travel_radius_km")


class _DemographicsStep(BaseModel):
    """Output of one step of the demographics loop."""

    extracted_value: str | None = Field(
        default=None,
        description="The parsed value for PENDING_FIELD, or null if the user's "
        "message didn't clearly answer it.",
    )
    next_field: str | None = Field(
        default=None,
        description="The next field to ask about, chosen from {first_name, age, "
        "gender, sexual_orientation, campus, travel_radius_km}. Null if all "
        "fields are now filled.",
    )
    next_message: str = Field(
        description="The next text message to send. Short, casual, one question "
        "max.",
    )


def _build_demographics_system(state: AgentState) -> str:
    template = load("demographics")
    partial = state.demographics_partial
    return template.format(
        first_name=state.first_name or "(not yet)",
        age=partial.get("age", "(not yet)"),
        gender=partial.get("gender", "(not yet)"),
        sexual_orientation=partial.get("sexual_orientation", "(not yet)"),
        campus=partial.get("campus", "(not yet)"),
        travel_radius_km=partial.get("travel_radius_km", "(not yet)"),
    )


def _apply_extracted(state: AgentState, field: str, raw_value: str) -> None:
    """Store the extracted value into state.first_name or state.demographics_partial."""
    if field == "first_name":
        state.first_name = raw_value.strip().title()
        return

    if field in ("age", "travel_radius_km"):
        digits = "".join(c for c in raw_value if c.isdigit())
        if digits:
            state.demographics_partial[field] = int(digits)
    else:
        state.demographics_partial[field] = raw_value.strip()


def _try_finalize_demographics(state: AgentState) -> None:
    """If all demographic fields are populated, build a Demographics object."""
    required = ("age", "gender", "sexual_orientation", "campus", "travel_radius_km")
    if all(f in state.demographics_partial for f in required):
        try:
            state.demographics = Demographics(**{k: state.demographics_partial[k] for k in required})
        except Exception:
            # Validation failed (e.g. age wasn't really an int). Leave demographics=None;
            # we'll try again once the LLM re-asks the problematic field.
            state.demographics = None


async def demographics_node(state: AgentState, config: RunnableConfig) -> dict:
    """One turn of demographics: parse user's last message, ask for next field.

    Uses a self-loop in the graph; interrupt_before=["demographics"] pauses
    after each turn until the user replies.
    """
    channel = _get_channel(config)
    pending = state.demographics_pending_field or "first_name"
    user_text = _pending_user_input(state)

    system = _build_demographics_system(state)
    messages = [
        {
            "role": "user",
            "content": (
                f"PENDING_FIELD: {pending}\n"
                f"USER_MESSAGE: {user_text or '(no user message yet — send the first question)'}"
            ),
        }
    ]

    step = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=_DemographicsStep,
        tool_name="demographics_step",
        tool_description="Parse one demographic answer and produce the next question.",
    )

    if step.extracted_value and pending:
        _apply_extracted(state, pending, step.extracted_value)
        _try_finalize_demographics(state)

    await _send(state, channel, step.next_message)

    if step.next_field and step.next_field in _DEMOGRAPHIC_FIELDS:
        return {
            "messages": state.messages,
            "first_name": state.first_name,
            "demographics": state.demographics,
            "demographics_partial": state.demographics_partial,
            "demographics_pending_field": step.next_field,
            "current_node": "collect_demographics",
        }
    # All fields filled — transition out
    return {
        "messages": state.messages,
        "first_name": state.first_name,
        "demographics": state.demographics,
        "demographics_partial": state.demographics_partial,
        "demographics_pending_field": None,
        "current_node": "probe_weekend",
    }


# ---------- probe_weekend ----------

async def probe_weekend_node(state: AgentState, config: RunnableConfig) -> dict:
    """Asks about last Saturday, scores extraversion, mines interests."""
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("probe_weekend")
    user_content = (
        f"FIRST_NAME: {state.first_name or 'unknown'}\n"
        f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}"
    )
    messages = [{"role": "user", "content": user_content}]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this probe. Just send the question.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {
            "messages": state.messages,
            "current_node": "probe_weekend",
        }

    probe = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=ProbeOutput,
        tool_name="probe_output",
        tool_description="Record scores, detected interests, and the next message.",
    )

    new_scores = dict(state.dimension_scores)
    for dim, score in probe.scores.items():
        new_scores.setdefault(dim, []).append(score)

    new_interests = list(state.interests_detected)
    for t in probe.interests_detected:
        if t not in new_interests:
            new_interests.append(t)

    await _send(state, channel, probe.next_message)

    next_node = "adaptive_interest" if probe.interest_to_probe else "probe_planning"
    return {
        "messages": state.messages,
        "dimension_scores": new_scores,
        "interests_detected": new_interests,
        "interest_to_probe_topic": probe.interest_to_probe,
        "current_node": next_node,
    }


# ---------- adaptive_interest ----------

from app.models.persona import Interest
from app.models.probe import InterestProbeOutput


async def adaptive_interest_node(state: AgentState, config: RunnableConfig) -> dict:
    """One follow-up probe about the distinctive interest from probe_weekend."""
    channel = _get_channel(config)
    topic = state.interest_to_probe_topic or ""
    user_text = _pending_user_input(state)

    system = load("adaptive_interest").format(
        topic=topic,
        user_message=user_text or "(no reply yet)",
    )
    messages = [
        {
            "role": "user",
            "content": f"TOPIC_BEING_PROBED: {topic}\nUSER_MESSAGE: {user_text}",
        }
    ]

    probe = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=InterestProbeOutput,
        tool_name="interest_probe_output",
        tool_description="Extract specific details and depth signal for the interest.",
    )

    await _send(state, channel, probe.next_message)

    interest = Interest(
        topic=topic,
        depth_signal=probe.depth_signal,
        specific_details=probe.specific_details,
    )
    return {
        "messages": state.messages,
        "interest_probed": interest,
        "interest_to_probe_topic": None,
        "current_node": "probe_planning",
    }


# ---------- probe_planning ----------

async def probe_planning_node(state: AgentState, config: RunnableConfig) -> dict:
    """Asks about trip planning, scores intuition + judging."""
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("probe_planning")
    user_content = (
        f"FIRST_NAME: {state.first_name or 'unknown'}\n"
        f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}"
    )
    messages = [{"role": "user", "content": user_content}]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this probe. Just send the opening question.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {"messages": state.messages, "current_node": "probe_planning"}

    probe = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=ProbeOutput,
        tool_name="probe_output",
        tool_description="Record scores and the next message.",
    )

    new_scores = dict(state.dimension_scores)
    for dim, score in probe.scores.items():
        new_scores.setdefault(dim, []).append(score)

    new_interests = list(state.interests_detected)
    for t in probe.interests_detected:
        if t not in new_interests:
            new_interests.append(t)

    await _send(state, channel, probe.next_message)
    return {
        "messages": state.messages,
        "dimension_scores": new_scores,
        "interests_detected": new_interests,
        "current_node": "probe_support",
    }


# ---------- probe_support ----------

async def probe_support_node(state: AgentState, config: RunnableConfig) -> dict:
    """Asks about supporting a friend through a breakup, scores thinking."""
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("probe_support")
    user_content = (
        f"FIRST_NAME: {state.first_name or 'unknown'}\n"
        f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}"
    )
    messages = [{"role": "user", "content": user_content}]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this probe. Just send the opening question.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {"messages": state.messages, "current_node": "probe_support"}

    probe = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=ProbeOutput,
        tool_name="probe_output",
        tool_description="Record scores and the next message.",
    )

    new_scores = dict(state.dimension_scores)
    for dim, score in probe.scores.items():
        new_scores.setdefault(dim, []).append(score)

    new_interests = list(state.interests_detected)
    for t in probe.interests_detected:
        if t not in new_interests:
            new_interests.append(t)

    await _send(state, channel, probe.next_message)
    return {
        "messages": state.messages,
        "dimension_scores": new_scores,
        "interests_detected": new_interests,
        "current_node": "probe_stress",
    }


# ---------- probe_stress (Big Five Neuroticism) ----------

async def probe_stress_node(state: AgentState, config: RunnableConfig) -> dict:
    """Asks about recent stress experience, scores Big Five Neuroticism.

    Neuroticism has no MBTI equivalent and doesn't contribute to the derived
    MBTI letter — it's a Big-Five-only axis captured to make the 'Big Five is
    the ground truth, MBTI is a derived wrapper' thesis literal.
    """
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("probe_stress")
    user_content = (
        f"FIRST_NAME: {state.first_name or 'unknown'}\n"
        f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}"
    )
    messages = [{"role": "user", "content": user_content}]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this probe. Just send the opening question.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {"messages": state.messages, "current_node": "probe_stress"}

    probe = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=ProbeOutput,
        tool_name="probe_output",
        tool_description="Record neuroticism score and the next message.",
    )

    new_scores = dict(state.dimension_scores)
    for dim, score in probe.scores.items():
        new_scores.setdefault(dim, []).append(score)

    new_interests = list(state.interests_detected)
    for t in probe.interests_detected:
        if t not in new_interests:
            new_interests.append(t)

    await _send(state, channel, probe.next_message)
    return {
        "messages": state.messages,
        "dimension_scores": new_scores,
        "interests_detected": new_interests,
        "current_node": "values_rank",
    }


# ---------- values_rank ----------

class _ValuesRankOutput(BaseModel):
    values_ranked: list[str] = Field(
        description="User's top 3 in order, each from the fixed vocabulary "
        "{ambition, family, adventure, growth, stability, creativity}. May be "
        "fewer than 3 if user gave fewer.",
    )
    next_message: str


async def values_rank_node(state: AgentState, config: RunnableConfig) -> dict:
    """Asks the user to rank 3 values. No scoring."""
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("values_rank")
    messages = [
        {
            "role": "user",
            "content": (
                f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}"
            ),
        }
    ]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this step. Just send the opening question with the list of six values.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {"messages": state.messages, "current_node": "values_rank"}

    result = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=_ValuesRankOutput,
        tool_name="values_rank_output",
        tool_description="Extract the user's top 3 values in order.",
    )

    await _send(state, channel, result.next_message)
    return {
        "messages": state.messages,
        "values_ranked": result.values_ranked[:3],
        "current_node": "ask_dealbreakers",
    }


# ---------- dealbreakers ----------

class _DealbreakersOutput(BaseModel):
    dealbreakers: list[str] = Field(
        description="List of short dealbreaker phrases extracted from the user.",
    )
    next_message: str


async def dealbreakers_node(state: AgentState, config: RunnableConfig) -> dict:
    """Final interview question. Extracts dealbreakers, transitions to synthesize."""
    channel = _get_channel(config)
    user_text = _pending_user_input(state)
    system = load("dealbreakers")
    messages = [
        {
            "role": "user",
            "content": f"USER_MESSAGE: {user_text or '(no user message yet — send the opening question)'}",
        }
    ]

    if not user_text:
        client = get_client()
        response = await client.messages.create(
            model=settings.anthropic_turn_model,
            max_tokens=200,
            system=system + "\n\nThis is your FIRST turn of this step. Just send the opening question.",
            messages=messages,
        )
        text = "".join(b.text for b in response.content if b.type == "text").strip()
        await _send(state, channel, text)
        return {"messages": state.messages, "current_node": "ask_dealbreakers"}

    result = await structured_call(
        model=settings.anthropic_turn_model,
        system=system,
        messages=messages,
        output_model=_DealbreakersOutput,
        tool_name="dealbreakers_output",
        tool_description="Extract the user's dealbreakers.",
    )

    await _send(state, channel, result.next_message)
    return {
        "messages": state.messages,
        "dealbreakers": result.dealbreakers,
        "current_node": "synthesize",
    }


# ---------- synthesize + reveal ----------

import json

from app.models.persona import Persona
from app.services.mbti import derive_mbti


class _PersonaSynthOutput(BaseModel):
    summary: str
    interests: list[Interest]
    conversation_hooks: list[str]


async def synthesize_node(state: AgentState, config: RunnableConfig) -> dict:
    """Opus call that produces the final Persona JSON. Persists to DB."""
    personality = derive_mbti(state.dimension_scores)

    transcript_lines = [f"{m.role}: {m.text}" for m in state.messages]
    interest_probed_str = (
        f"{state.interest_probed.topic} ({state.interest_probed.depth_signal}): "
        f"{state.interest_probed.specific_details}"
        if state.interest_probed
        else "(none probed in depth)"
    )

    user_payload = {
        "first_name": state.first_name,
        "demographics": state.demographics.model_dump() if state.demographics else {},
        "values_ranked": state.values_ranked,
        "dealbreakers": state.dealbreakers,
        "interests_detected": state.interests_detected,
        "interest_probed": interest_probed_str,
        "mbti": personality.mbti,
        "dimensions": personality.dimensions.model_dump(),
        "transcript": "\n".join(transcript_lines),
    }

    system = load("synthesize")
    messages = [{"role": "user", "content": json.dumps(user_payload, indent=2)}]

    synth = await structured_call(
        model=settings.anthropic_synthesis_model,
        system=system,
        messages=messages,
        output_model=_PersonaSynthOutput,
        tool_name="persona_synthesis",
        tool_description="Produce the summary, final interests, and conversation hooks.",
        max_tokens=2048,
    )

    if state.demographics is None:
        raise RuntimeError("synthesize called without demographics filled")

    persona = Persona(
        session_id=state.session_id,
        summary=synth.summary,
        demographics=state.demographics,
        personality=personality,
        values_ranked=state.values_ranked,
        interests=synth.interests,
        dealbreakers=state.dealbreakers,
        conversation_hooks=synth.conversation_hooks[:3],
        created_at=datetime.utcnow(),
    )

    # Persist to DB
    from app.db import SessionLocal
    from app.models.orm import MessageRow, ScoreRow, SessionRow

    with SessionLocal() as session:
        row = session.get(SessionRow, state.session_id)
        if row is None:
            row = SessionRow(id=state.session_id, complete=True)
            session.add(row)
        row.complete = True
        row.persona_json = persona.model_dump_json()

        # Persist transcript (only rows not yet written — simple: purge and rewrite)
        session.query(MessageRow).filter_by(session_id=state.session_id).delete()
        for m in state.messages:
            session.add(
                MessageRow(
                    session_id=state.session_id,
                    role=m.role,
                    text=m.text,
                    created_at=m.created_at,
                )
            )

        # Persist per-dimension scores (purge + rewrite for idempotency on retries)
        session.query(ScoreRow).filter_by(session_id=state.session_id).delete()
        for dim, score_list in state.dimension_scores.items():
            for score in score_list:
                session.add(
                    ScoreRow(
                        session_id=state.session_id,
                        dimension=dim,
                        score=score,
                        evidence="(aggregated at synthesis time)",
                        probe_node=dim,
                    )
                )
        session.commit()

    return {"current_node": "reveal"}


async def reveal_node(state: AgentState, config: RunnableConfig) -> dict:
    """Delivers a short reveal message. No LLM call."""
    channel = _get_channel(config)
    name = state.first_name or "you"
    msg = f"alright {name}, your twin is ready. scroll up to see what i got."
    await _send(state, channel, msg)
    return {
        "messages": state.messages,
        "complete": True,
        "current_node": "reveal",
    }
