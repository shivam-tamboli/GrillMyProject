import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from app.db.database import SessionLocal
from app.models import InterviewSession, Message, User
from app.services import auth as auth_service
from app.services.interview import after_score
from app.services.llm import LLMError
from app.services.question_bank import get_bank_question
from app.services.scoring import MAX_ANSWER_CHARS, score_answer

router = APIRouter(prefix="/api/session", tags=["interview"])


class _Rejected(Exception):
    """The answer can't be taken. The message is safe to show the client."""


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


def _parse(data) -> tuple[str, int, bool] | None:
    """(answer, question_number, skipped) from a client message, or None if it is malformed."""
    if not isinstance(data, dict):
        return None
    answer, number, skipped = data.get("answer"), data.get("question_number"), data.get("skipped", False)
    if not isinstance(answer, str) or type(number) is not int or not isinstance(skipped, bool):
        return None
    return answer, number, skipped


def _load_question(session_id: uuid.UUID, number: int) -> dict:
    """Check the answer is for the current question and return what scoring needs."""
    with SessionLocal() as db:
        session = db.get(InterviewSession, session_id)
        if session.status != "ongoing":
            raise _Rejected("this session is not ongoing")
        if number != session.current_question_number:
            raise _Rejected(f"expected an answer to question {session.current_question_number}")

        question = db.scalars(
            select(Message).where(
                Message.session_id == session_id,
                Message.role == "ai",
                Message.question_number == number,
            )
        ).one()
        bank = get_bank_question(question.bank_question_id) if question.bank_question_id else None
        return {
            "text": question.content,
            "type": question.question_type,
            "note": bank["note"] if bank else None,
            "level": session.current_level,
        }


def _score_and_save(session_id: uuid.UUID, number: int, answer: str, skipped: bool, streak: int) -> tuple[dict, int]:
    """Score one answer and save it. Returns the score message and the new streak.

    Blocking (OpenAI call and database), so the caller runs it in a worker thread.
    Nothing is written if scoring fails.
    """
    question = _load_question(session_id, number)
    answer = "" if skipped else answer[:MAX_ANSWER_CHARS]
    scored = score_answer(question["text"], answer, question["level"], question["note"])
    level, streak = after_score(question["level"], streak, scored["score"])

    with SessionLocal() as db:
        # lock the row and check again, the scoring call took a few seconds
        session = db.scalars(
            select(InterviewSession).where(InterviewSession.id == session_id).with_for_update()
        ).one()
        if session.status != "ongoing" or session.current_question_number != number:
            raise _Rejected("this question is no longer open")
        already = db.scalars(
            select(Message.id).where(
                Message.session_id == session_id,
                Message.role == "user",
                Message.question_number == number,
            )
        ).first()
        if already:
            raise _Rejected("this question is already answered")

        db.add(
            Message(
                session_id=session_id,
                role="user",
                content=answer,
                question_number=number,
                question_type=question["type"],
                score=scored["score"],
                feedback=scored["feedback"],
            )
        )
        session.current_level = level
        db.commit()

    return {"type": "score", "question_number": number, "score": scored["score"], "feedback": scored["feedback"]}, streak


def _error(message: str) -> dict:
    return {"type": "error", "message": message}


@router.websocket("/{session_id}/interview")
async def interview(ws: WebSocket, session_id: uuid.UUID):
    # same refusal for "no cookie", "not found" and "not yours" so ids can't be probed
    if not await run_in_threadpool(_can_join, ws.cookies.get("access_token"), session_id):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws.accept()
    streak = 0  # in memory, starts again if the client reconnects
    try:
        while True:
            try:
                data = await ws.receive_json()
            except ValueError:
                await ws.send_json(_error("message must be JSON"))
                continue

            parsed = _parse(data)
            if not parsed:
                await ws.send_json(_error("expected answer, question_number and optional skipped"))
                continue
            answer, number, skipped = parsed

            try:
                score_message, streak = await run_in_threadpool(
                    _score_and_save, session_id, number, answer, skipped, streak
                )
            except _Rejected as e:
                await ws.send_json(_error(str(e)))
                continue
            except LLMError:
                await ws.send_json(_error("could not score the answer, send it again"))
                continue

            await ws.send_json(score_message)
            # the next question is sent in the next tasks
    except WebSocketDisconnect:
        pass
