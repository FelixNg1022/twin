from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.agent.graph import build_graph
from app.agent.state import AgentState
from app.channels.web import WebChannel
from app.models.message import Message

# One global compiled graph; MemorySaver keeps state keyed by thread_id.
_graph = build_graph()


@dataclass
class TurnResult:
    session_id: str
    agent_messages: list[str]
    complete: bool


def _config(session_id: str, channel: WebChannel) -> dict:
    return {"configurable": {"thread_id": session_id, "channel": channel}}


async def start_session() -> TurnResult:
    """Create a new session and run until first interrupt. Returns agent's opening messages."""
    session_id = str(uuid4())
    channel = WebChannel()
    initial = AgentState(session_id=session_id)
    config = _config(session_id, channel)

    async for _ in _graph.astream(initial, config=config):
        pass

    snapshot = _graph.get_state(config)
    return TurnResult(
        session_id=session_id,
        agent_messages=channel.messages,
        complete=bool(snapshot.values.get("complete", False)),
    )


async def send_user_message(session_id: str, text: str) -> TurnResult:
    """Add user message to state, resume graph until next interrupt."""
    channel = WebChannel()
    config = _config(session_id, channel)

    snapshot = _graph.get_state(config)
    if snapshot is None or snapshot.values == {}:
        raise LookupError(f"Unknown session: {session_id}")

    current_messages = list(snapshot.values.get("messages", []))
    current_messages.append(Message(role="user", text=text, created_at=datetime.utcnow()))
    _graph.update_state(config, {"messages": current_messages})

    async for _ in _graph.astream(None, config=config):
        pass

    new_snapshot = _graph.get_state(config)
    return TurnResult(
        session_id=session_id,
        agent_messages=channel.messages,
        complete=bool(new_snapshot.values.get("complete", False)),
    )
