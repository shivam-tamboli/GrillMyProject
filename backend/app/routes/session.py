import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models import InterviewSession, Message, Project, Resume, User
from app.services.question_bank import pick_questions
from app.services.session import get_seen_bank_ids

router = APIRouter(prefix="/api/session", tags=["session"])

SESSION_MINUTES = 45


class StartBody(BaseModel):
    resume_id: uuid.UUID
    project_id: uuid.UUID | None = None


@router.post("/start")
def start_session(
    body: StartBody,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # same 404 for "not found" and "not yours" so ids can't be probed
    resume = db.get(Resume, body.resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="resume not found")

    if body.project_id:
        project = db.get(Project, body.project_id)
        if not project or project.user_id != user.id:
            raise HTTPException(status_code=404, detail="project not found")

    if not resume.confirmed_level:
        raise HTTPException(status_code=409, detail="confirm the resume level first")

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=SESSION_MINUTES)
    ongoing = db.scalars(
        select(InterviewSession)
        .where(
            InterviewSession.user_id == user.id,
            InterviewSession.status == "ongoing",
            InterviewSession.started_at > cutoff,
        )
        .order_by(InterviewSession.started_at.desc())
    ).first()
    if ongoing:
        raise HTTPException(
            status_code=409,
            detail={"error": "you already have an ongoing session", "session_id": str(ongoing.id)},
        )

    questions = pick_questions(resume.confirmed_level, get_seen_bank_ids(db, user.id))
    first = questions[0]

    session = InterviewSession(
        user_id=user.id,
        resume_id=resume.id,
        project_id=body.project_id,
        current_level=resume.confirmed_level,
        bank_question_ids=[q["id"] for q in questions],
    )
    db.add(session)
    db.flush()
    db.add(
        Message(
            session_id=session.id,
            role="ai",
            content=first["text"],
            question_number=1,
            question_type="resume",
            bank_question_id=first["id"],
        )
    )
    db.commit()
    return {"session_id": str(session.id), "first_question": first["text"]}
