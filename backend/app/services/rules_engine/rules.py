"""Rule predicates — one evaluator per catalog code (docs/06 §7).

Each evaluator takes the scoped claim rows (already joined to patient sex / birth
year / death date / insured) plus the rule's YAML ``params`` and returns the
claims it flags with an evidence blob. Money and ЕКД sanctions are attached by
the engine (:mod:`app.services.rules_engine.engine`) — evaluators only decide
*which* claims are defects and *why*.

Evaluators are deterministic and side-effect free so golden tests can assert
exact counts against ``datagen/storylines.yaml``.
"""

from __future__ import annotations

import datetime
import uuid
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ClaimRow:
    """A claim joined to the patient attributes the rules need."""

    id: uuid.UUID
    patient_id: str
    doctor_id: uuid.UUID
    care_type: str
    funding_source: str
    service_code: str
    icd10: str | None
    date_start: datetime.date
    date_end: datetime.date | None
    qty: int
    amount: int
    referral_id: str | None
    status: str
    period: str
    sex: str
    birth_year: int
    death_date: datetime.date | None
    insured: bool


@dataclass(frozen=True, slots=True)
class RuleHit:
    """One flagged claim + why (evidence folded into the Finding details)."""

    claim: ClaimRow
    evidence: dict[str, Any] = field(default_factory=dict)


Evaluator = Callable[[list[ClaimRow], dict[str, Any]], list[RuleHit]]


def _age_on(row: ClaimRow) -> int:
    return row.date_start.year - row.birth_year


def r01_posthumous(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    hits: list[RuleHit] = []
    for r in rows:
        if r.death_date is not None and r.date_start > r.death_date:
            hits.append(RuleHit(r, {
                "death_date": r.death_date.isoformat(),
                "service_date": r.date_start.isoformat(),
                "days_after_death": (r.date_start - r.death_date).days,
            }))
    return hits


def r02_sex_mismatch(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    sex_by_code: dict[str, str] = params.get("sex_by_code", {})
    hits: list[RuleHit] = []
    for r in rows:
        required = sex_by_code.get(r.service_code)
        if required is not None and r.sex != required:
            hits.append(RuleHit(r, {
                "service_code": r.service_code,
                "patient_sex": r.sex,
                "required_sex": required,
            }))
    return hits


def r03_age_mismatch(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    age_by_code: dict[str, list[int]] = params.get("age_by_code", {})
    hits: list[RuleHit] = []
    for r in rows:
        if r.care_type != "screening":
            continue
        band = age_by_code.get(r.service_code)
        if not band:
            continue
        age = _age_on(r)
        if age < band[0] or age > band[1]:
            hits.append(RuleHit(r, {
                "service_code": r.service_code,
                "patient_age": age,
                "target_min": band[0],
                "target_max": band[1],
            }))
    return hits


def _group_extras(
    rows: Iterable[ClaimRow], key: Callable[[ClaimRow], tuple[Any, ...]]
) -> list[tuple[ClaimRow, int]]:
    """Return (claim, group_size) for every claim in a >1 group except the first."""
    groups: dict[tuple[Any, ...], list[ClaimRow]] = defaultdict(list)
    for r in rows:
        groups[key(r)].append(r)
    extras: list[tuple[ClaimRow, int]] = []
    for members in groups.values():
        if len(members) > 1:
            for extra in sorted(members, key=lambda c: str(c.id))[1:]:
                extras.append((extra, len(members)))
    return extras


def r04_duplicate(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    extras = _group_extras(
        rows, lambda r: (r.patient_id, r.service_code, r.date_start.isoformat())
    )
    return [
        RuleHit(r, {
            "service_code": r.service_code,
            "service_date": r.date_start.isoformat(),
            "duplicates_in_group": size,
        })
        for r, size in extras
    ]


def r07_kdu_no_referral(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    return [
        RuleHit(r, {"service_code": r.service_code})
        for r in rows
        if r.care_type == "kdu" and not r.referral_id
    ]


def r10_impossible_volume(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    threshold = int(params.get("max_per_day", 80))
    by_doc_day: dict[tuple[uuid.UUID, str], list[ClaimRow]] = defaultdict(list)
    for r in rows:
        by_doc_day[(r.doctor_id, r.date_start.isoformat())].append(r)
    hits: list[RuleHit] = []
    for (doctor_id, day), members in by_doc_day.items():
        if len(members) >= threshold:
            for r in members:
                hits.append(RuleHit(r, {
                    "doctor_id": str(doctor_id),
                    "service_date": day,
                    "day_count": len(members),
                    "threshold": threshold,
                }))
    return hits


def r11_weekend_anomaly(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    """Anomalous number of weekend services by one doctor in one month.

    Grouped per (doctor, period) so the signal is scope-independent — a
    ratio would dilute for a high-volume doctor, so we use an absolute
    monthly weekend count (the population ceiling on this seed is ~26/mo).
    """
    min_weekend = int(params.get("min_weekend_per_month", 30))
    by_doc_month: dict[tuple[uuid.UUID, str], list[ClaimRow]] = defaultdict(list)
    for r in rows:
        if r.date_start.weekday() >= 5:  # Sat/Sun
            by_doc_month[(r.doctor_id, r.period)].append(r)
    hits: list[RuleHit] = []
    for (doctor_id, period), weekend_claims in by_doc_month.items():
        if len(weekend_claims) >= min_weekend:
            for r in weekend_claims:
                hits.append(RuleHit(r, {
                    "doctor_id": str(doctor_id),
                    "period": period,
                    "weekend_claims_in_month": len(weekend_claims),
                    "threshold": min_weekend,
                }))
    return hits


def r13_readmission(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    window = int(params.get("window_days", 30))
    inpatient = [r for r in rows if r.care_type in ("day_hosp", "hosp")]
    by_patient: dict[str, list[ClaimRow]] = defaultdict(list)
    for r in inpatient:
        by_patient[r.patient_id].append(r)
    hits: list[RuleHit] = []
    for members in by_patient.values():
        ordered = sorted(members, key=lambda c: c.date_start)
        for prev, cur in zip(ordered, ordered[1:], strict=False):
            prev_end = prev.date_end or prev.date_start
            gap = (cur.date_start - prev_end).days
            if 0 <= gap <= window:
                hits.append(RuleHit(cur, {
                    "previous_end": prev_end.isoformat(),
                    "readmission_start": cur.date_start.isoformat(),
                    "gap_days": gap,
                }))
    return hits


def r16_uninsured_osms(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    return [
        RuleHit(r, {"funding_source": r.funding_source, "insured": r.insured})
        for r in rows
        if r.funding_source == "osms" and not r.insured
    ]


def r17_reform_source(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    prefixes = tuple(params.get("icd_prefixes", []))
    wrong_source = params.get("wrong_source", "gobmp")
    correct_source = params.get("correct_source", "osms")
    effective_from = datetime.date.fromisoformat(params["effective_from"])
    hits: list[RuleHit] = []
    for r in rows:
        if (
            r.funding_source == wrong_source
            and r.icd10 is not None
            and r.icd10.startswith(prefixes)
            and r.date_start >= effective_from
        ):
            hits.append(RuleHit(r, {
                "icd10": r.icd10,
                "billed_source": r.funding_source,
                "correct_source": correct_source,
            }))
    return hits


def r18_frequency(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    limits: dict[str, int] = params.get("max_per_month_by_code", {})
    groups: dict[tuple[str, str, str], list[ClaimRow]] = defaultdict(list)
    for r in rows:
        if r.service_code in limits:
            groups[(r.patient_id, r.service_code, r.period)].append(r)
    hits: list[RuleHit] = []
    for (_, code, period), members in groups.items():
        limit = limits[code]
        if len(members) > limit:
            for extra in sorted(members, key=lambda c: str(c.id))[limit:]:
                hits.append(RuleHit(extra, {
                    "service_code": code,
                    "period": period,
                    "count": len(members),
                    "limit": limit,
                }))
    return hits


def r20_screening_repeat(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    screening = [r for r in rows if r.care_type == "screening"]
    extras = _group_extras(
        screening, lambda r: (r.patient_id, r.service_code, r.period)
    )
    return [
        RuleHit(r, {"service_code": r.service_code, "period": r.period, "count": size})
        for r, size in extras
    ]


def r25_empty_emr(rows: list[ClaimRow], params: dict[str, Any]) -> list[RuleHit]:
    return [RuleHit(r, {"icd10": None}) for r in rows if not r.icd10]


EVALUATORS: dict[str, Evaluator] = {
    "R01": r01_posthumous,
    "R02": r02_sex_mismatch,
    "R03": r03_age_mismatch,
    "R04": r04_duplicate,
    "R07": r07_kdu_no_referral,
    "R10": r10_impossible_volume,
    "R11": r11_weekend_anomaly,
    "R13": r13_readmission,
    "R16": r16_uninsured_osms,
    "R17": r17_reform_source,
    "R18": r18_frequency,
    "R20": r20_screening_repeat,
    "R25": r25_empty_emr,
}
