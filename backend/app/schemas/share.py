"""Shareable-state-link schemas (EPIC H3)."""

from typing import Any

from app.schemas.common import APIModel


class ShareCreateIn(APIModel):
    url_state: dict[str, Any]  # {path, query, locale}


class ShareOut(APIModel):
    code: str


class ShareStateOut(APIModel):
    code: str
    url_state: dict[str, Any]
