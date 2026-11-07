import uuid

from sqlalchemy import select
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
