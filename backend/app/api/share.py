"""Shareable state links (EPIC H3) — «я смотрю на то же, что и ты».

A short code persists the exact route+state; opening /s/<code> restores it
through the opener's own permissions. Local-only (no external realtime SaaS) —
combined with the G2 event feed, this IS the collaborative mode.
"""

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.db import get_db
from app.models.events import ShareLink
from app.schemas.share import ShareCreateIn, ShareOut, ShareStateOut

router = APIRouter(prefix="/share", tags=["share"])

DbDep = Annotated[Session, Depends(get_db)]
# No ambiguous chars (0/o/1/l) — codes get read aloud / typed in the demo.
_ALPHABET = "23456789abcdefghijkmnpqrstuvwxyz"


def _new_code() -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(8))


@router.post("", response_model=ShareOut, status_code=201)
def create_share(
    body: ShareCreateIn, db: DbDep, principal: OptionalPrincipal
) -> ShareOut:
    """Mint a short code for the current route+state."""
    code = _new_code()
    for _ in range(5):  # vanishingly unlikely collision, but be safe
        if db.get(ShareLink, code) is None:
            break
        code = _new_code()
    db.add(ShareLink(
        code=code, url_state=body.url_state,
        created_by=principal.username if principal else None,
    ))
    db.commit()
    return ShareOut(code=code)


@router.get("/{code}", response_model=ShareStateOut)
def resolve_share(code: str, db: DbDep) -> ShareStateOut:
    """Resolve a share code back to its route+state (the /s/<code> resolver)."""
    link = db.get(ShareLink, code)
    if link is None:
        raise HTTPException(status_code=404, detail="ссылка не найдена")
    return ShareStateOut(code=code, url_state=link.url_state)
