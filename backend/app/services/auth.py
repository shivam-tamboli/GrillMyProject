import secrets
from urllib.parse import urlencode

from app.core.config import settings

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"


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
