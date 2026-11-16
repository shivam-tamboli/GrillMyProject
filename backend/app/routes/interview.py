import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool

from app.db.database import SessionLocal
from app.models import InterviewSession, User
from app.services import auth as auth_service

router = APIRouter(prefix="/api/session", tags=["interview"])


def _can_join(access_token: str | None, session_id: uuid.UUID) -> bool:
    """True when the cookie is valid and the session is this user's and still ongoing."""
    user_id = auth_service.decode_jwt(access_token) if access_token else None
    if not user_id:
        return False
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return False

    # short session, not held open for the whole interview
    with SessionLocal() as db:
        user = db.get(User, user_uuid)
        session = db.get(InterviewSession, session_id)
        return bool(user and session and session.user_id == user.id and session.status == "ongoing")


@router.websocket("/{session_id}/interview")
async def interview(ws: WebSocket, session_id: uuid.UUID):
    # same refusal for "no cookie", "not found" and "not yours" so ids can't be probed
    if not await run_in_threadpool(_can_join, ws.cookies.get("access_token"), session_id):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws.accept()
    try:
        while True:
            await ws.receive_json()  # answers are handled in the next tasks
    except WebSocketDisconnect:
        pass
