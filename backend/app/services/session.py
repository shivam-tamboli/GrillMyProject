import uuid
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import InterviewSession, Message


def get_seen_bank_ids(db: Session, user_id: uuid.UUID) -> list[str]:
    """Bank question ids this user was asked in any session, oldest first.

    An id shows up once per time it was asked. The picker counts a repeat
    from its last time, so the duplicates are left in.
    """
    stmt = (
        select(Message.bank_question_id)
        .join(InterviewSession, Message.session_id == InterviewSession.id)
        .where(InterviewSession.user_id == user_id, Message.bank_question_id.is_not(None))
        .order_by(Message.created_at, Message.question_number)
    )
    return list(db.scalars(stmt))


def complete_session(db: Session, session_id: uuid.UUID) -> InterviewSession:
    """Mark the session completed with ended_at and overall_score.

    overall_score is the average of the saved answer scores, a skipped answer
    counts as 0. It stays empty when nothing was answered. A session that is
    already completed is returned as it is.
    """
    # lock the row so the timer and the end endpoint can't both complete it
    session = db.scalars(
        select(InterviewSession).where(InterviewSession.id == session_id).with_for_update()
    ).one()
    if session.status == "completed":
        return session

    average = db.scalar(
        select(func.avg(Message.score)).where(
            Message.session_id == session_id,
            Message.role == "user",
            Message.score.is_not(None),
        )
    )
    session.status = "completed"
    session.ended_at = datetime.now(timezone.utc)
    session.overall_score = Decimal(average).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) if average is not None else None
    db.commit()
    return session
