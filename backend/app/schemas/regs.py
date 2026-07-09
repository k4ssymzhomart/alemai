"""Pydantic schemas for the regulatory viewer (EPIC I1, /regs)."""

from __future__ import annotations

from pydantic import BaseModel


class RegDocOut(BaseModel):
    id: str
    title: str
    title_kk: str | None = None
    langs: list[str]
    redaction: str | None = None
    source_url: str | None = None
    lines: int


class TocNodeOut(BaseModel):
    kind: str
    num: str
    title: str
    anchor: str
    line: int
    children: list["TocNodeOut"] = []


class RegLineOut(BaseModel):
    n: int
    text: str
    kind: str
    num: str | None = None
    anchor: str | None = None


class RegTocOut(BaseModel):
    doc_id: str
    lang: str
    title: str
    redaction: str | None = None
    source_url: str | None = None
    langs: list[str]
    total_lines: int
    toc: list[TocNodeOut]


class RegContentOut(BaseModel):
    doc_id: str
    lang: str
    from_: int
    to: int
    total_lines: int
    lines: list[RegLineOut]


class RegHitOut(BaseModel):
    line: int
    punkt: str | None = None
    anchor: str | None = None
    snippet: str


class RegSearchOut(BaseModel):
    doc_id: str
    lang: str
    q: str
    count: int
    hits: list[RegHitOut]
