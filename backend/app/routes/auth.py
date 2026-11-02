from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/github/login")
def github_login():
    state = auth_service.new_state()
    response = RedirectResponse(auth_service.build_authorize_url(state))
    response.set_cookie("oauth_state", state, max_age=600, httponly=True, samesite="lax")
    return response
