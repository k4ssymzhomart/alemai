"""Auth endpoints — real login/logout/me over signed session cookies (G1)."""

from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.config import get_settings
from app.db import get_db
from app.models.users import User
from app.schemas.auth import LoginIn, MeOut
from app.services.auth import Principal, sign_session, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

DbDep = Annotated[Session, Depends(get_db)]


def _set_session_cookie(response: Response, principal: Principal) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.session_cookie,
        value=sign_session(principal),
        max_age=settings.session_max_age,
        httponly=True,
        samesite="lax",  # :3000 and :8800 are same-site (localhost) → cookie flows
        secure=False,  # HTTP localhost demo; flip to True behind TLS
        path="/",
    )


@router.post("/login", response_model=MeOut)
def login(body: LoginIn, response: Response, db: DbDep) -> MeOut:
    """Validate credentials, mint a signed session cookie, return the identity."""
    user = db.execute(
        sa.select(User).where(User.username == body.username)
    ).scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(
        body.password, user.password_hash
    ):
        raise HTTPException(status_code=401, detail="қате логин немесе құпиясөз")
    principal = Principal(
        user_id=str(user.id), username=user.username or "", name=user.name,
        role=str(user.role),
    )
    _set_session_cookie(response, principal)
    return MeOut(
        user_id=principal.user_id, username=principal.username,
        name=principal.name, role=principal.role,
    )


@router.post("/logout", status_code=204)
def logout(response: Response) -> Response:
    """Clear the session cookie."""
    response.delete_cookie(get_settings().session_cookie, path="/")
    response.status_code = 204
    return response


@router.get("/me", response_model=MeOut)
def me(principal: OptionalPrincipal) -> MeOut:
    """Current session identity; 401 when unauthenticated (drives the route guard)."""
    if principal is None:
        raise HTTPException(status_code=401, detail="сессия жоқ")
    return MeOut(
        user_id=principal.user_id, username=principal.username, name=principal.name,
        role=principal.role, is_service=principal.is_service,
    )
