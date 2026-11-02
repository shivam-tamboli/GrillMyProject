import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/github/login")
def github_login():
    state = auth_service.new_state()
    response = RedirectResponse(auth_service.build_authorize_url(state))
    response.set_cookie("oauth_state", state, max_age=600, httponly=True, samesite="lax")
    return response


@router.get("/github/callback")
def github_callback(
    code: str,
    state: str,
    response: Response,
    oauth_state: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not oauth_state or not secrets.compare_digest(oauth_state, state):
        raise HTTPException(status_code=400, detail="invalid state")

    try:
        access_token = auth_service.exchange_code(code)
        profile = auth_service.fetch_profile(access_token)
    except auth_service.GitHubAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user, is_new_user = auth_service.get_or_create_user(db, profile)

    token = auth_service.create_jwt(user.id)
    max_age = auth_service.JWT_EXPIRE_DAYS * 24 * 3600
    # secure=True once we are on https
    response.set_cookie("access_token", token, max_age=max_age, httponly=True, samesite="lax")
    response.delete_cookie("oauth_state")
    return {"user_id": str(user.id), "is_new_user": is_new_user}
