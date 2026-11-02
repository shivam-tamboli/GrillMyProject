import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7


class GitHubAuthError(Exception):
    pass


def new_state() -> str:
    return secrets.token_urlsafe(32)


def build_authorize_url(state: str) -> str:
    # login scope only. repo access is a separate flow later.
    params = {
        "client_id": settings.github_client_id,
        "scope": "read:user user:email",
        "state": state,
    }
    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code(code: str) -> str:
    resp = httpx.post(
        GITHUB_TOKEN_URL,
        data={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
        },
        headers={"Accept": "application/json"},
        timeout=10,
    )
    token = resp.json().get("access_token")
    if not token:
        raise GitHubAuthError("github did not return an access token")
    return token


def fetch_profile(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/vnd.github+json"}
    user = httpx.get(f"{GITHUB_API_URL}/user", headers=headers, timeout=10).json()

    email = user.get("email")
    if not email:
        # email can be private, so ask for the primary verified one
        emails = httpx.get(f"{GITHUB_API_URL}/user/emails", headers=headers, timeout=10).json()
        email = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
    if not email:
        raise GitHubAuthError("no verified email on this github account")

    return {
        "github_id": str(user["id"]),
        "name": user.get("name") or user["login"],
        "email": email,
    }


def get_or_create_user(db: Session, profile: dict) -> tuple[User, bool]:
    user = db.scalar(select(User).where(User.github_oauth_id == profile["github_id"]))
    if user:
        return user, False
    user = User(name=profile["name"], email=profile["email"], github_oauth_id=profile["github_id"])
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, True


def create_jwt(user_id) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)
