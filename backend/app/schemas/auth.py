"""Auth API schemas (EPIC G1)."""

from app.schemas.common import APIModel


class LoginIn(APIModel):
    username: str
    password: str


class MeOut(APIModel):
    """The session identity — what the frontend hydrates role + header from."""

    user_id: str | None = None
    username: str
    name: str
    role: str
    is_service: bool = False
