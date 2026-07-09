"""Shared text/number formatting + numeral normalization (Epic D).

Used by both the docgen templates and the copilot answer/validator layers so a
number rendered in a document and the same number extracted for the copilot's
no-hallucination validator normalize identically.

Conventions (docs/07 §5): currency «12 400 000 ₸» (space thousands), dates
ДД.ММ.ГГГГ. The validator normalizes away spaces, ₸/%/separators and treats
comma and period as the same decimal mark so "60,8%" and "60.8" compare equal.
"""

from __future__ import annotations

import datetime
import re

NBSP = " "


def fmt_tenge(amount: int | float) -> str:
    """Whole-tenge money with space thousands separators, e.g. «12 400 000 ₸»."""
    n = int(round(amount))
    return f"{n:,}".replace(",", " ") + " ₸"


def fmt_int(n: int | float) -> str:
    """Integer with space thousands separators (no currency)."""
    return f"{int(round(n)):,}".replace(",", " ")


def fmt_pct(value: float, digits: int = 1) -> str:
    """Percent with a period decimal mark to match the dashboard, e.g. «60.8%»."""
    return f"{round(value, digits):g}%"


def fmt_date(d: datetime.date | str) -> str:
    """Render a date as ДД.ММ.ГГГГ; accepts an ISO string or a date."""
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d[:10])
    return d.strftime("%d.%m.%Y")


def fmt_period(period: str) -> str:
    """YYYY-MM -> «ММ.ГГГГ» (month label for report headers)."""
    year, month = period.split("-")[:2]
    return f"{int(month):02d}.{year}"


# ---------------------------------------------------------------------------
# Numeral extraction + normalization (copilot no-hallucination validator)
# ---------------------------------------------------------------------------

# Matches integers, grouped thousands (space/NBSP), and decimals (,/.):
#   "4", "260", "2 992 000", "60,8", "14.10.2026", "300%"
_NUMBER_RE = re.compile(r"\d[\d\s .,%]*\d|\d")


def normalize_numbers(text: str) -> set[str]:
    """Return the set of normalized numeric tokens found in ``text``.

    Normalization: drop grouping spaces, split date-like tokens into their
    parts, unify comma/period decimals, strip trailing separators. A date
    "14.10.2026" contributes {"14", "10", "2026"} AND "14.10.2026" so either a
    whole-date or a part comparison validates.
    """
    out: set[str] = set()
    for raw in _NUMBER_RE.findall(text):
        token = raw.replace(" ", "").replace(NBSP, "").replace("%", "")
        if not token:
            continue
        # Date-like d.d.d or d-d-d -> keep whole + parts.
        parts = re.split(r"[.\-/]", token)
        if len(parts) >= 3 and all(p.isdigit() for p in parts):
            out.add(token)
            out.update(p.lstrip("0") or "0" for p in parts)
            continue
        # Plain grouped integer or single decimal.
        cleaned = token.rstrip(".,")
        if "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")
        # Collapse thousands "1.234" that slipped through -> keep as-is if a
        # single decimal, else strip stray separators.
        if cleaned.count(".") > 1:
            cleaned = cleaned.replace(".", "")
        try:
            val = float(cleaned)
        except ValueError:
            continue
        out.add(_canon(val))
    return out


def _canon(val: float) -> str:
    """Canonical form of a numeric value: int when whole, else 0.1-rounded."""
    if val == int(val):
        return str(int(val))
    return f"{round(val, 1):g}"


def answer_numbers(text: str) -> set[str]:
    """Numeric tokens claimed by an answer (same normalizer as evidence)."""
    return normalize_numbers(text)
