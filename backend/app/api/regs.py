"""Regulatory viewer endpoints (EPIC I1) — «Нормативка» in-app reader.

Read-only, no auth scoping (public legal texts): document list, parsed TOC,
windowed content, and in-document search anchored to пункт. Backs the two-pane
reader and the copilot/finding «[источник]» → internal-viewer jump.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas.regs import (
    RegContentOut,
    RegDocOut,
    RegLineOut,
    RegSearchOut,
    RegTocOut,
    TocNodeOut,
)
from app.services import regs as regs_svc

router = APIRouter(prefix="/regs", tags=["regs"])

LangQuery = Annotated[str, Query(pattern="^(ru|kk)$", description="ru|kk")]


def _to_toc_node(node: regs_svc.TocNode) -> TocNodeOut:
    return TocNodeOut(
        kind=node.kind,
        num=node.num,
        title=node.title,
        anchor=node.anchor,
        line=node.line,
        children=[_to_toc_node(c) for c in node.children],
    )


@router.get("", response_model=list[RegDocOut])
def list_regs() -> list[RegDocOut]:
    """Corpus registry: id, title, langs, «ред. от» date, official source URL."""
    return [RegDocOut(**d) for d in regs_svc.list_docs()]


@router.get("/{doc_id}/toc", response_model=RegTocOut)
def reg_toc(doc_id: str, lang: LangQuery = "ru") -> RegTocOut:
    """Parsed structure (глава/статья/параграф) + header metadata."""
    doc = regs_svc.load(doc_id, lang)
    if doc is None:
        raise HTTPException(status_code=404, detail="документ не найден")
    langs = sorted(regs_svc._scan().get(doc_id, set()), key=lambda x: (x != "ru", x))
    return RegTocOut(
        doc_id=doc.doc_id,
        lang=doc.lang,
        title=doc.title,
        redaction=doc.redaction,
        source_url=doc.source_url,
        langs=langs,
        total_lines=len(doc.lines),
        toc=[_to_toc_node(n) for n in doc.toc],
    )


@router.get("/{doc_id}/content", response_model=RegContentOut)
def reg_content(
    doc_id: str,
    lang: LangQuery = "ru",
    from_: Annotated[int, Query(alias="from", ge=1)] = 1,
    to: Annotated[int | None, Query(ge=1)] = None,
) -> RegContentOut:
    """Windowed lines [from, to] (1-based, inclusive). Whole doc when unbounded."""
    doc = regs_svc.load(doc_id, lang)
    if doc is None:
        raise HTTPException(status_code=404, detail="документ не найден")
    total = len(doc.lines)
    start = max(1, from_)
    end = min(total, to) if to is not None else total
    window = doc.lines[start - 1 : end] if start <= end else []
    return RegContentOut(
        doc_id=doc.doc_id,
        lang=doc.lang,
        from_=start,
        to=end,
        total_lines=total,
        lines=[
            RegLineOut(n=li.n, text=li.text, kind=li.kind, num=li.num, anchor=li.anchor)
            for li in window
        ],
    )


@router.get("/{doc_id}/search", response_model=RegSearchOut)
def reg_search(
    doc_id: str,
    q: Annotated[str, Query(min_length=2, description="query, ≥2 chars")],
    lang: LangQuery = "ru",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> RegSearchOut:
    """In-document search; each hit carries the пункт anchor it lands under."""
    doc = regs_svc.load(doc_id, lang)
    if doc is None:
        raise HTTPException(status_code=404, detail="документ не найден")
    hits = regs_svc.search(doc, q, limit=limit)
    return RegSearchOut(doc_id=doc.doc_id, lang=doc.lang, q=q, count=len(hits), hits=hits)
