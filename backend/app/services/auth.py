"""Auth core — password hashing, signed session cookies, demo users (EPIC G1).

Local-only, no external identity provider (venue wi-fi is hostile — everything
runs offline). Passwords hash with stdlib PBKDF2 (no native bcrypt build in the
slim image); the session is a signed, timestamped cookie via itsdangerous —
stateless, so no server-side session store to keep in sync.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid
from dataclasses import dataclass

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import get_settings
from app.models.enums import UserRole

# uuid5 namespace so the 5 demo users get STABLE ids across reseeds (a session
# cookie minted before a demo-reset keeps resolving to the same user row).
_USER_NS = uuid.UUID("d9b2d63d-a233-4123-847a-016a5f7f0000")
_PBKDF2_ROUNDS = 120_000
_SESSION_SALT = "qalam.session.v1"


@dataclass(frozen=True, slots=True)
class SeedUser:
    username: str
    name: str
    role: UserRole
    title_ru: str  # spoken role label for the login card

    @property
    def id(self) -> uuid.UUID:
        return uuid.uuid5(_USER_NS, self.username)


# The five живых user types the lead asked for (G1). Password = qalam2026 (demo).
SEED_USERS: tuple[SeedUser, ...] = (
    SeedUser("director", "Ерлан", UserRole.chief, "директор"),
    SeedUser("economist", "Айгерім", UserRole.economist, "экономист"),
    SeedUser("statistician", "Дана", UserRole.statistician, "статистик"),
    SeedUser("curator", "Марат", UserRole.curator, "куратор УОЗ"),
    SeedUser("admin", "Админ", UserRole.admin, "IT-администратор"),
)
DEMO_PASSWORD = "qalam2026"


# ---------------------------------------------------------------------------
# password hashing (PBKDF2-HMAC-SHA256, stdlib)
# ---------------------------------------------------------------------------

def hash_password(password: str, *, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ROUNDS)
    return (
        f"pbkdf2_sha256${_PBKDF2_ROUNDS}$"
        f"{base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, rounds_s, salt_b64, hash_b64 = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds_s))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(dk, expected)


# ---------------------------------------------------------------------------
# session cookie
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class Principal:
    """Who is making the request — from a session cookie or a service token."""

    user_id: str | None
    username: str
    name: str
    role: str
    is_service: bool = False

    @property
    def is_curator(self) -> bool:
        return self.role == UserRole.curator.value


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().secret_key, salt=_SESSION_SALT)


def sign_session(principal: Principal) -> str:
    return _serializer().dumps({
        "uid": principal.user_id,
        "username": principal.username,
        "name": principal.name,
        "role": principal.role,
    })


def load_session(token: str) -> Principal | None:
    try:
        data = _serializer().loads(token, max_age=get_settings().session_max_age)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict) or "role" not in data:
        return None
    return Principal(
        user_id=data.get("uid"),
        username=str(data.get("username", "")),
        name=str(data.get("name", "")),
        role=str(data["role"]),
    )
