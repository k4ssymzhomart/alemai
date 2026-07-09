"""Events API schemas (EPIC G2/G3)."""

import datetime
import uuid
from typing import Any

from app.schemas.common import APIModel


class EventOut(APIModel):
    id: uuid.UUID
    ts: datetime.datetime
    type: str
    severity: str
    actor: str
    role: str | None = None
    entity_ref: str | None = None
    link: str | None = None
    title_kk: str
    title_ru: str
    payload: dict[str, Any] | None = None


class EventsOut(APIModel):
    """The polling payload: recent events + unread badge + a server cursor."""

    items: list[EventOut]
    unread: int
    cursor: datetime.datetime | None = None  # ts of the newest event (client watermark)


class MarkReadOut(APIModel):
    read_at: datetime.datetime
    unread: int = 0
