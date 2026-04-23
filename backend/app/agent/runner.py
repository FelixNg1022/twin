"""Session runner.

LangGraph's checkpoint/interrupt_before machinery has fiddly state-merge
semantics that bit us on resume (update_state without as_node resets non-
specified fields to defaults, re-evaluating routers on stale state). The
graph object is still useful for the mermaid diagram. At runtime we dispatch
to node functions directly based on state.current_node — a plain state
machine. Sessions are held in an in-process dict keyed by session_id.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Callable
from uuid import uuid4

from app.agent.nodes import (
    adaptive_interest_node,
    dealbreakers_node,
    demographics_node,
    greeting_node,
    probe_planning_node,
    probe_support_node,
    probe_weekend_node,
    reveal_node,
    synthesize_node,
    values_rank_node,
)
from app.agent.state import AgentState
from app.channels.web import WebChannel
from app.models.message import Message

NodeFn = Callable[[AgentState, dict], Awaitable[dict]]

_NODE_MAP: dict[str, NodeFn] = {
    "greeting": greeting_node,
    "collect_demographics": demographics_node,
    "probe_weekend": probe_weekend_node,
    "adaptive_interest": adaptive_interest_node,
    "probe_planning": probe_planning_node,
    "probe_support": probe_support_node,
    "values_rank": values_rank_node,
    "ask_dealbreakers": dealbreakers_node,
    "synthesize": synthesize_node,
    "reveal": reveal_node,
}

# Nodes that need user input before running (first turn asks a question and waits).
# After one run of these, subsequent calls process user input.
_WAITS_FOR_USER: set[str] = {
    "collect_demographics",
    "probe_weekend",
    "adaptive_interest",
    "probe_planning",
    "probe_support",
    "values_rank",
    "ask_dealbreakers",
}

# In-process session store.
_sessions: dict[str, AgentState] = {}


@dataclass
class TurnResult:
    session_id: str
    agent_messages: list[str]
    complete: bool


def _apply_update(state: AgentState, update: dict) -> None:
    """Apply a node's return-dict patch to the state in place."""
    for key, value in update.items():
        if hasattr(state, key):
            setattr(state, key, value)


async def _run_until_user_input(state: AgentState, channel: WebChannel) -> None:
    """Run nodes forward until a waiting node has produced its message, or the
    interview reaches completion.

    Each node's `next_message` field is designed to include the next question
    inline — demographics's transition ends with the weekend question, weekend's
    ack ends with either a hiking follow-up or the planning question, etc. So
    we halt after any waiting node runs; we don't need to run the next waiting
    node to get its opening.

    Non-waiting nodes (synthesize, reveal) fire inline after the dealbreakers
    turn: synthesize has no user-facing message, and reveal sends the final
    reveal text before flipping complete=True.
    """
    config = {"configurable": {"channel": channel}}
    for _ in range(12):  # safety bound
        before_node = state.current_node
        node_fn = _NODE_MAP.get(before_node)
        if node_fn is None:
            raise RuntimeError(f"Unknown node: {before_node}")

        update = await node_fn(state, config)
        _apply_update(state, update)

        if state.complete:
            return
        # Halt when the NEXT node to run is waiting for user input. The node
        # that just ran has already buffered its message (which typically
        # includes the next question inline per prompt design).
        if state.current_node in _WAITS_FOR_USER:
            return
        # Otherwise continue into the next non-waiting node (synthesize → reveal).


async def start_session() -> TurnResult:
    """Create a new session and run the greeting + demographics opening question."""
    session_id = str(uuid4())
    state = AgentState(session_id=session_id)
    _sessions[session_id] = state
    channel = WebChannel()
    await _run_until_user_input(state, channel)
    return TurnResult(
        session_id=session_id,
        agent_messages=channel.messages,
        complete=state.complete,
    )


async def send_user_message(session_id: str, text: str) -> TurnResult:
    """Append user message to state, run forward until next pause or completion."""
    state = _sessions.get(session_id)
    if state is None:
        raise LookupError(f"Unknown session: {session_id}")

    state.messages.append(Message(role="user", text=text, created_at=datetime.utcnow()))
    channel = WebChannel()
    await _run_until_user_input(state, channel)
    return TurnResult(
        session_id=session_id,
        agent_messages=channel.messages,
        complete=state.complete,
    )


def reset_sessions() -> None:
    """Test helper."""
    _sessions.clear()
