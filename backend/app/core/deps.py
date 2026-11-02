import uuid

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.services import auth as auth_service


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status_code=401, detail="not logged in")

    if not access_token:
        raise unauthorized
    user_id = auth_service.decode_jwt(access_token)
    if not user_id:
        raise unauthorized
    try:
        user = db.get(User, uuid.UUID(user_id))
    except ValueError:
        raise unauthorized
    if not user:
        raise unauthorized
    return user
