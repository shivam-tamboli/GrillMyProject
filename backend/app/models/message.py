import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (Index("ix_messages_session_id_question_number", "session_id", "question_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    question_number: Mapped[int] = mapped_column(Integer)
    question_type: Mapped[str] = mapped_column(String)
    bank_question_id: Mapped[str | None] = mapped_column(String, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
