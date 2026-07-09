"""Regulatory corpus reader (EPIC I1) — «Нормативка» in-app document viewer.

Serves the legal texts under ``backend/regs/*.{ru,kk}.txt`` (Правила
мониторинга/оплаты/закупа, Закон №206-VIII, and extracts) as a browsable
document: a parsed TOC (глава/статья/параграф), windowed content with per-line
anchors, and an in-document search that anchors hits to their пункт.

Everything is derived from the files themselves (title, «ред. от» redaction date
and the official adilet source URL are read from each file's header) — no DB and
no coupling to the radar. Parsing is cached per (doc_id, lang); the corpus is
static and baked into the image.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# Corpus location + friendly titles
# ---------------------------------------------------------------------------

REGS_DIR = Path(__file__).resolve().parents[2] / "regs"  # backend/regs

# Curated short bilingual titles keyed by doc_id (filename base without lang).
# kk titles: NEEDS-NATIVE-REVIEW (glossary is the law) — flagged in the report.
_TITLES: dict[str, dict[str, str]] = {
    "pravila_monitoringa": {
        "ru": "Правила мониторинга",
        "kk": "Мониторинг жүргізу қағидалары",
    },
    "pravila_oplaty": {"ru": "Правила оплаты", "kk": "Төлеу қағидалары"},
    "pravila_zakupa": {"ru": "Правила закупа", "kk": "Сатып алу қағидалары"},
    "zakon_206_viii": {
        "ru": "Закон №206-VIII (Единый пакет, с 01.01.2026)",
        "kk": "№206-VIII Заң (Бірыңғай пакет)",
    },
    "monitoring_amendment_2025": {
        "ru": "Мониторинг — изменения 2025 (приказ №68)",
        "kk": "Мониторинг — 2025 өзгерістері",
    },
    "kodeks_zdorovie_extract": {
        "ru": "Кодекс «О здоровье» (извлечение)",
        "kk": "«Халық денсаулығы» кодексі (үзінді)",
    },
}

# Stable presentation order (most demo-relevant first).
_ORDER = [
    "pravila_monitoringa",
    "pravila_zakupa",
    "pravila_oplaty",
    "zakon_206_viii",
    "monitoring_amendment_2025",
    "kodeks_zdorovie_extract",
]

# ---------------------------------------------------------------------------
# Line grammar (bilingual). Anchors: chapter g-N · article st-N · paragraph
# s-<line> · пункт p-N (N may be "53-1").
# ---------------------------------------------------------------------------

_RE_CHAPTER = re.compile(r"^(?:Глава\s+(\d+)|(\d+)-тарау)\.\s*(.*)$")
_RE_ARTICLE = re.compile(r"^(?:Статья\s+(\d+)|(\d+)-бап)\.\s*(.*)$")
_RE_PARAGRAPH = re.compile(r"^(?:Параграф\s+(\d+)|(\d+)-параграф)\.?\s*(.*)$")
_RE_PUNKT = re.compile(r"^(\d+(?:-\d+)?)\.\s+(\S.*)$")
_RE_NOTE = re.compile(r"^(?:Сноска|Ескерту)\.")
_RE_DATE = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
_RE_URL = re.compile(r"https?://[^\s()]+")


@dataclass(frozen=True, slots=True)
class RegLine:
    n: int  # 1-based line number
    text: str
    kind: str  # chapter | article | paragraph | punkt | text
    num: str | None = None
    anchor: str | None = None


@dataclass(frozen=True, slots=True)
class TocNode:
    kind: str
    num: str
    title: str
    anchor: str
    line: int
    children: list["TocNode"] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ParsedDoc:
    doc_id: str
    lang: str
    title: str
    redaction: str | None
    source_url: str | None
    lines: list[RegLine]
    toc: list[TocNode]
    punkt_line: dict[str, int]  # пункт num -> 1-based line (body only)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def _scan() -> dict[str, set[str]]:
    """Map doc_id -> available langs from ``<doc_id>.<lang>.txt`` files."""
    out: dict[str, set[str]] = {}
    if not REGS_DIR.is_dir():
        return out
    for p in REGS_DIR.glob("*.txt"):
        parts = p.name.split(".")
        if len(parts) < 3 or parts[-1] != "txt":
            continue
        doc_id, lang = ".".join(parts[:-2]), parts[-2]
        if lang not in ("ru", "kk"):
            continue
        out.setdefault(doc_id, set()).add(lang)
    return out


def _title(doc_id: str, lang: str, first_line: str) -> str:
    entry = _TITLES.get(doc_id, {})
    return entry.get(lang) or entry.get("ru") or (first_line[:80] if first_line else doc_id)


def _header_meta(lines: list[str]) -> tuple[str | None, str | None]:
    """(redaction date DD.MM.YYYY, official source URL) from the file header."""
    redaction: str | None = None
    url: str | None = None
    for raw in lines[:15]:
        low = raw.lower()
        if redaction is None and ("изменениями" in low or "жаңартылған" in low):
            m = _RE_DATE.search(raw)
            if m:
                redaction = m.group(1)
        if url is None and ("источник" in low or "дереккөз" in low):
            m = _RE_URL.search(raw)
            if m:
                url = m.group(0)
    return redaction, url


# ---------------------------------------------------------------------------
# Parsing (cached)
# ---------------------------------------------------------------------------


def _classify(text: str) -> tuple[str, str | None, str | None, str]:
    """Return (kind, num, anchor, display_title) for a raw line."""
    if _RE_NOTE.match(text):
        return "text", None, None, ""
    m = _RE_CHAPTER.match(text)
    if m:
        num = m.group(1) or m.group(2)
        return "chapter", num, f"g-{num}", (m.group(3) or "").strip()
    m = _RE_ARTICLE.match(text)
    if m:
        num = m.group(1) or m.group(2)
        return "article", num, f"st-{num}", (m.group(3) or "").strip()
    m = _RE_PARAGRAPH.match(text)
    if m:
        num = m.group(1) or m.group(2)
        return "paragraph", num, None, (m.group(3) or "").strip()
    m = _RE_PUNKT.match(text)
    if m:
        return "punkt", m.group(1), f"p-{m.group(1)}", ""
    return "text", None, None, ""


@lru_cache(maxsize=64)
def load(doc_id: str, lang: str) -> ParsedDoc | None:
    langs = _scan().get(doc_id)
    if not langs:
        return None
    use_lang = lang if lang in langs else next(iter(sorted(langs)))
    path = REGS_DIR / f"{doc_id}.{use_lang}.txt"
    if not path.is_file():
        return None
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    redaction, url = _header_meta(raw_lines)
    title = _title(doc_id, use_lang, raw_lines[0] if raw_lines else "")

    lines: list[RegLine] = []
    toc: list[TocNode] = []
    punkt_line: dict[str, int] = {}
    seen_top = False  # first chapter/article => body has started
    current_top: TocNode | None = None

    for i, raw in enumerate(raw_lines, start=1):
        text = raw.rstrip()
        kind, num, anchor, heading = _classify(text)
        if kind in ("chapter", "article"):
            seen_top = True
            node = TocNode(kind=kind, num=num, title=heading, anchor=anchor, line=i)
            toc.append(node)
            current_top = node
        elif kind == "paragraph":
            anchor = f"s-{i}"
            node = TocNode(kind="paragraph", num=num, title=heading, anchor=anchor, line=i)
            if current_top is not None:
                current_top.children.append(node)
            else:
                toc.append(node)
        elif kind == "punkt" and seen_top and num not in punkt_line:
            punkt_line[num] = i
        lines.append(RegLine(n=i, text=text, kind=kind, num=num, anchor=anchor))

    return ParsedDoc(
        doc_id=doc_id,
        lang=use_lang,
        title=title,
        redaction=redaction,
        source_url=url,
        lines=lines,
        toc=toc,
        punkt_line=punkt_line,
    )


# ---------------------------------------------------------------------------
# Public API used by the router
# ---------------------------------------------------------------------------


def list_docs() -> list[dict]:
    """Registry rows: id, title, langs, redaction date, source url, line count."""
    scan = _scan()
    ordered = [d for d in _ORDER if d in scan] + sorted(set(scan) - set(_ORDER))
    out: list[dict] = []
    for doc_id in ordered:
        langs = sorted(scan[doc_id], key=lambda x: (x != "ru", x))  # ru first
        doc = load(doc_id, "ru")
        if doc is None:
            continue
        out.append(
            {
                "id": doc_id,
                "title": _title(doc_id, "ru", doc.title),
                "title_kk": _TITLES.get(doc_id, {}).get("kk"),
                "langs": langs,
                "redaction": doc.redaction,
                "source_url": doc.source_url,
                "lines": len(doc.lines),
            }
        )
    return out


def _punkt_at(doc: ParsedDoc, line_no: int) -> str | None:
    """The пункт number whose anchor covers ``line_no`` (nearest above)."""
    best: str | None = None
    best_line = 0
    for num, ln in doc.punkt_line.items():
        if best_line < ln <= line_no:
            best, best_line = num, ln
    return best


def search(doc: ParsedDoc, query: str, limit: int = 50) -> list[dict]:
    q = query.strip().lower()
    hits: list[dict] = []
    if not q:
        return hits
    for line in doc.lines:
        if q in line.text.lower():
            punkt = line.num if line.kind == "punkt" else _punkt_at(doc, line.n)
            hits.append(
                {
                    "line": line.n,
                    "punkt": punkt,
                    "anchor": f"p-{punkt}" if punkt else None,
                    "snippet": line.text[:240],
                }
            )
            if len(hits) >= limit:
                break
    return hits
