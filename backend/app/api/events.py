"""Events feed API (EPIC G2/G3) — polling endpoint + mark-read for the bell."""

import datetime
import uuid
from typing import Annotated

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import OptionalPrincipal
from app.db import get_db
from app.models.events import Event
from app.models.users import User
from app.schemas.events import EventOut, EventsOut, MarkReadOut

router = APIRouter(prefix="/events", tags=["events"])

DbDep = Annotated[Session, Depends(get_db)]

# Case/patient-level event types — hidden from a curator, who is scoped to
# aggregates (docs/13 §3; adversarial review #6). Curators still see import /
# threshold / source-update events.
_CASE_LEVEL_TYPES = (
    "finding_excluded", "finding_dismissed", "finding_restored", "rules_run_finished",
    "objection_filed",
)


def _scoped(stmt, principal: OptionalPrincipal):
    if principal is not None and principal.is_curator:
        return stmt.where(Event.type.not_in(_CASE_LEVEL_TYPES))
    return stmt


def _unread_count(db: Session, principal: OptionalPrincipal) -> int:
    """Events newer than the user's read cursor, excluding the user's own actions."""
    if principal is None or principal.user_id is None:
        return 0
    read_at = db.execute(
        sa.select(User.notifications_read_at).where(User.id == uuid.UUID(principal.user_id))
    ).scalar_one_or_none()
    stmt = _scoped(
        sa.select(sa.func.count()).select_from(Event).where(
            Event.actor_username.is_distinct_from(principal.username)
        ),
        principal,
    )
    if read_at is not None:
        stmt = stmt.where(Event.ts > read_at)
    return int(db.execute(stmt).scalar_one())


@router.get("", response_model=EventsOut)
def list_events(
    db: DbDep,
    principal: OptionalPrincipal,
    since: Annotated[datetime.datetime | None, Query(description="ISO ts cursor")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> EventsOut:
    """Recent events (newest first) + unread badge + a cursor watermark.

    With ``since``, returns only events strictly newer than the cursor (the
    poll delta); otherwise the latest ``limit`` events.
    """
    stmt = _scoped(sa.select(Event).order_by(Event.ts.desc(), Event.id.desc()), principal)
    if since is not None:
        stmt = stmt.where(Event.ts > since)
    rows = list(db.execute(stmt.limit(limit)).scalars())
    newest = db.execute(
        _scoped(sa.select(sa.func.max(Event.ts)), principal)
    ).scalar_one_or_none()
    return EventsOut(
        items=[EventOut.model_validate(e) for e in rows],
        unread=_unread_count(db, principal),
        cursor=newest,
    )


@router.post("/read", response_model=MarkReadOut)
def mark_all_read(db: DbDep, principal: OptionalPrincipal) -> MarkReadOut:
    """«Барлығын оқылды деп белгілеу» — advance the user's read cursor to now."""
    now = datetime.datetime.now(datetime.UTC)
    if principal is not None and principal.user_id is not None:
        db.execute(
            sa.update(User)
            .where(User.id == uuid.UUID(principal.user_id))
            .values(notifications_read_at=now)
        )
        db.commit()
    return MarkReadOut(read_at=now, unread=0)
