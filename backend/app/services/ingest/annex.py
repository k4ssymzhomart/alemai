"""Contract annex import — preview-only diff (EPIC F3, docs/17).

Parses an annex XLSX (line grain: вид помощи × источник × группа услуг with a
годовой план) and diffs it against the current contract lines. NOTHING is
written — the demo stops at the «Доп. соглашение № 4 — предпросмотр» screen
(«применение — в пилоте»), answering the «а доп. соглашения?» question with a
screen instead of words.
"""

from __future__ import annotations

from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractLine
from app.services.ingest.registry import (
    FUNDING_BY_LABEL,
    RegistryParseError,
    _parse_int,
    parse_table,
)
from app.services.ingest.samples import ANNEX_HEADERS, CARE_TYPE_BY_LABEL_RU

LineKey = tuple[str, str, str]  # (care_type, funding_source, service_group)


@dataclass(slots=True)
class AnnexLineDiff:
    care_type: str
    funding_source: str
    service_group: str
    plan_current: int
    plan_annex: int
    delta: int
    status: str  # changed | unchanged | new | missing


@dataclass(slots=True)
class AnnexPreview:
    filename: str
    year: int
    lines: list[AnnexLineDiff]
    changed: int
    total_current: int
    total_annex: int
    total_delta: int


def _current_plan(session: Session, year: int) -> dict[LineKey, int]:
    rows = session.execute(
        sa.select(
            ContractLine.care_type,
            ContractLine.funding_source,
            ContractLine.service_group,
            sa.func.sum(ContractLine.plan_amount),
        )
        .join(Contract, Contract.id == ContractLine.contract_id)
        .where(Contract.year == year)
        .group_by(
            ContractLine.care_type, ContractLine.funding_source,
            ContractLine.service_group,
        )
    ).all()
    return {
        (str(ct), str(src), str(sg or "")): int(total)
        for ct, src, sg, total in rows
    }


def preview_annex(
    session: Session, filename: str, data: bytes, year: int = 2026
) -> AnnexPreview:
    """Parse the annex file and diff it against the current plan. Read-only."""
    headers, data_rows = parse_table(filename, data)
    norm = [str(h).strip().lower() for h in headers]
    try:
        idx = {name: norm.index(name.lower()) for name in ANNEX_HEADERS}
    except ValueError as exc:
        raise RegistryParseError(
            "в файле нет колонок приложения к договору: "
            + ", ".join(ANNEX_HEADERS)
        ) from exc

    annex: dict[LineKey, int] = {}
    for row in data_rows:
        care_label = str(row[idx["Вид помощи"]] or "").strip()
        source_label = str(row[idx["Источник финансирования"]] or "").strip()
        care_type = CARE_TYPE_BY_LABEL_RU.get(care_label.lower())
        source = FUNDING_BY_LABEL.get(source_label.lower())
        amount = _parse_int(row[idx["Годовой план, тенге"]])
        if care_type is None or source is None or amount is None:
            raise RegistryParseError(
                f"строка приложения не распознана: «{care_label} / {source_label}»"
            )
        service_group = str(row[idx["Группа услуг"]] or "").strip()
        annex[(care_type, source, service_group)] = amount

    current = _current_plan(session, year)
    diffs: list[AnnexLineDiff] = []
    for key in sorted(current.keys() | annex.keys()):
        care_type, source, service_group = key
        was = current.get(key)
        becomes = annex.get(key)
        if was is None:
            status = "new"
        elif becomes is None:
            status = "missing"
        elif was != becomes:
            status = "changed"
        else:
            status = "unchanged"
        diffs.append(AnnexLineDiff(
            care_type=care_type,
            funding_source=source,
            service_group=service_group,
            plan_current=was or 0,
            plan_annex=becomes if becomes is not None else (was or 0),
            delta=(becomes if becomes is not None else (was or 0)) - (was or 0),
            status=status,
        ))
    diffs.sort(key=lambda d: (d.status == "unchanged", -abs(d.delta)))

    total_current = sum(current.values())
    total_annex = sum(v for v in annex.values())
    return AnnexPreview(
        filename=filename or "annex.xlsx",
        year=year,
        lines=diffs,
        changed=sum(1 for d in diffs if d.status != "unchanged"),
        total_current=total_current,
        total_annex=total_annex,
        total_delta=total_annex - total_current,
    )
