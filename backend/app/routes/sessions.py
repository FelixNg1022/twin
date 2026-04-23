from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.runner import send_user_message, start_session
from app.db import SessionLocal
from app.models.orm import SessionRow
from app.models.persona import Persona

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreateResponse(BaseModel):
    session_id: str
    agent_messages: list[str]


class MessageSendRequest(BaseModel):
    text: str


class MessageSendResponse(BaseModel):
    agent_messages: list[str]
    complete: bool


@router.post("", response_model=SessionCreateResponse, status_code=201)
async def create_session() -> SessionCreateResponse:
    result = await start_session()
    return SessionCreateResponse(
        session_id=result.session_id, agent_messages=result.agent_messages
    )


@router.post("/{session_id}/messages", response_model=MessageSendResponse)
async def send_message(
    session_id: str, body: MessageSendRequest
) -> MessageSendResponse:
    try:
        result = await send_user_message(session_id, body.text)
    except LookupError:
        raise HTTPException(status_code=404, detail=f"session {session_id} not found")
    return MessageSendResponse(
        agent_messages=result.agent_messages, complete=result.complete
    )


@router.get("/{session_id}/persona", response_model=Persona)
async def get_persona(session_id: str) -> Persona:
    with SessionLocal() as session:
        row = session.get(SessionRow, session_id)
        if row is None:
            raise HTTPException(
                status_code=404, detail=f"session {session_id} not found"
            )
        if not row.complete or not row.persona_json:
            raise HTTPException(
                status_code=409,
                detail=f"session {session_id} not complete",
            )
        return Persona.model_validate_json(row.persona_json)
