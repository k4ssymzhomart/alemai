#!/usr/bin/env python3
"""IGERIM synthetic data generator — docs/06-DATA-ANALYTICS.md §4 + docs/17 EPIC B.

Profiles (``--profile``, DEFAULT ``gp14-real``) set the scale; ``config.yaml`` is
the shared base merged under the profile. Every planted number lives in
``datagen/storylines.yaml`` (single source of truth). Money = integer ₸.

Calibration (docs/17 EPIC B headline AC): ``plan_qty`` is DERIVED from
``plan_amount ÷ representative tariff`` per line, so a line executes at ≈ its
``execution_profile`` (fact ≈ Poisson(plan_qty × profile)). ПМСП подушевой runs
low (fee-for-service объём ≈ 38% of the capitation plan), fee-for-service
specialities read a healthy 85–105%, and the mid-year (as-of 2026-06) overview
lands ≈61% execution.

Storylines 1–7 mutate the tables (planters); storyline 8 (возражения / DF-timers)
is emitted as data in the manifest for the API/frontend DeadlineBox.

Conventions (docs/05 §4): money integer ₸, ids uuid (deterministic from seed),
dates ISO, months "YYYY-MM", all times UTC.

Usage:
    python datagen/generate.py [--profile gp14-real|city-composite]
                               [--config datagen/config.yaml]
                               [--storylines datagen/storylines.yaml]
                               [--out datagen/output] [--sample]
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import uuid
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

# Config care-type keys → canonical care_type enum values (docs/05 §4).
# "other" (прочее) is generated as неотложная помощь at PHC level.
CARE_TYPE_ALIASES: dict[str, str] = {"other": "ambulance"}
CARE_KEY_BY_TYPE: dict[str, str] = {v: k for k, v in CARE_TYPE_ALIASES.items()}

FUNDING_SOURCES: tuple[str, str] = ("gobmp", "osms")

# service_code → service_group (contract C2). МРТ (S010) is carved into its own
# КДУ service_group so storyline 1 renders as a distinct drill-down line. This
# drives both the contract_lines split and the service_group_map fact join.
SERVICE_GROUP_BY_CODE: dict[str, str] = {"S010": "МРТ"}

CLAIM_COLUMNS: list[str] = [
    "id", "org_id", "patient_id", "doctor_id", "dept", "care_type",
    "funding_source", "service_code", "service_name", "icd10",
    "date_start", "date_end", "qty", "tariff", "amount",
    "referral_id", "status", "period", "source_file_id",
]

# Plausible ICD-10 stubs per care type; replaced by shared/ref CSVs later.
# Diabetes ЗПДН codes (E10*/E11*) are intentionally EXCLUDED from base lists so
# the base data stays clean of accidental R17 (reform mis-billing) findings —
# E11.9 is planted only by storyline 7.
ICD10_BY_CARE_TYPE: dict[str, list[str]] = {
    "pmsp": ["J06.9", "J20.9", "I10", "K21.9", "K29.7", "M54.5",
             "J45.0", "N30.0", "H66.9", "L20.8", "Z00.0"],
    "kdu": ["I25.1", "G43.9", "K21.0", "E04.1", "M42.1", "I67.8",
            "K80.2", "N20.0", "H52.1", "J31.0", "D64.9", "I11.9"],
    "day_hosp": ["I11.9", "K52.9", "K29.5", "G54.1", "N11.1", "M51.1", "I67.8"],
    "dent": ["K02.1", "K04.5", "K05.1", "K08.1", "K04.0"],
    "screening": ["Z12.3", "Z12.4", "Z12.1", "Z13.1", "Z13.6"],
    "ambulance": ["R10.4", "R51", "I20.0", "J06.9", "T14.9", "R07.4"],
}

# Datagen claim column → официальная форма счёт-реестра АПП (приказ ҚР ДСМ-86,
# V2100024058) / Damumed «реестр оказанных услуг» (docs/research/*). confidence:
# CONFIRMED = column exists in the official form; INFERRED = our column, no
# direct official field. (docs/17 EPIC B (f), lower priority — mapping preset.)
SCHET_REESTR_EXPORT_MAP: list[tuple[str, str, str]] = [
    ("service_code",   "service_full_code",  "CONFIRMED"),
    ("service_name",   "service_name",       "CONFIRMED"),
    ("qty",            "service_quantity",   "CONFIRMED"),
    ("tariff",         "service_unit_price", "CONFIRMED"),
    ("amount",         "service_amount",     "CONFIRMED"),
    ("funding_source", "funding_source",     "CONFIRMED"),
    ("date_start",     "service_date",       "LIKELY"),
    ("icd10",          "diagnosis_icd10",    "LIKELY"),
    ("patient_id",     "patient_iin",        "INFERRED"),  # we store a salted hash, never raw ИИН
    ("doctor_id",      "doctor_code",        "INFERRED"),
    ("referral_id",    "referral_number",    "INFERRED"),
    ("dept",           "site_number",        "INFERRED"),
    ("care_type",      "line_name",          "INFERRED"),
    ("status",         "eps_case_status",    "INFERRED"),
    ("period",         "registry_period",    "INFERRED"),
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def care_key(care_type: str) -> str:
    """Canonical care_type value → config key (e.g. 'ambulance' → 'other')."""
    return CARE_KEY_BY_TYPE.get(care_type, care_type)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` onto ``base`` (override wins; dicts merge)."""
    out = dict(base)
    for key, value in override.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(config_path: Path, profile: str, storylines_path: Path) -> dict[str, Any]:
    """Base config + profile override + storylines.yaml, merged into one cfg."""
    base = load_yaml(config_path)
    profile_path = config_path.parent / "profiles" / f"{profile}.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(f"unknown profile {profile!r}: {profile_path} not found")
    cfg = deep_merge(base, load_yaml(profile_path))
    cfg["_profile"] = profile
    stories = load_yaml(storylines_path)
    cfg["storylines"] = stories.get("storylines", [])
    cfg["demo_today"] = stories.get("demo_today")
    return cfg


def parse_month(value: str) -> tuple[int, int]:
    year, month = value.split("-")
    return int(year), int(month)


def month_key(year: int, month: int) -> str:
    return f"{year}-{month:02d}"


def month_index(year: int, month: int) -> int:
    return year * 12 + (month - 1)


def month_seq(start: str, end: str) -> list[tuple[int, int]]:
    """Inclusive sequence of (year, month) between two 'YYYY-MM' strings."""
    y, m = parse_month(start)
    ye, me = parse_month(end)
    out: list[tuple[int, int]] = []
    while (y, m) <= (ye, me):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def working_days(year: int, month: int) -> int:
    """Mon–Fri count. KZ public holidays intentionally ignored (skeleton)."""
    _, ndays = calendar.monthrange(year, month)
    return sum(1 for d in range(1, ndays + 1) if date(year, month, d).weekday() < 5)


def last_working_day(year: int, month: int) -> date:
    """Last Mon–Fri date of the month."""
    _, ndays = calendar.monthrange(year, month)
    d = date(year, month, ndays)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def add_working_days(start: date, n: int) -> date:
    """Date ``n`` working days after ``start`` (skip Sat/Sun; holidays ignored)."""
    d = start
    remaining = n
    while remaining > 0:
        d += timedelta(days=1)
        if d.weekday() < 5:
            remaining -= 1
    return d


def weekend_dates(year: int, month: int) -> list[date]:
    _, ndays = calendar.monthrange(year, month)
    return [date(year, month, d) for d in range(1, ndays + 1)
            if date(year, month, d).weekday() >= 5]


def det_uuid(rng: np.random.Generator) -> str:
    """uuid4-shaped id drawn from the seeded generator (reproducible)."""
    return str(uuid.UUID(bytes=rng.bytes(16), version=4))


def det_uuids(rng: np.random.Generator, n: int) -> list[str]:
    raw = rng.bytes(16 * n)
    return [str(uuid.UUID(bytes=raw[i * 16:(i + 1) * 16], version=4)) for i in range(n)]


def month_weights(year: int, ct_key: str, seasonality: dict[str, list[float]]) -> np.ndarray:
    """Normalized monthly weights for one contract year: working days × seasonality."""
    profile = seasonality[ct_key]
    raw = np.array(
        [working_days(year, m) * profile[m - 1] for m in range(1, 13)], dtype=float
    )
    return raw / raw.sum()


def sample_dates(
    rng: np.random.Generator, year: int, month: int, n: int, weekend_weight: float
) -> list[date]:
    """Sample n service dates inside a month, weekdays strongly preferred."""
    _, ndays = calendar.monthrange(year, month)
    days = np.arange(1, ndays + 1)
    w = np.array(
        [1.0 if date(year, month, int(d)).weekday() < 5 else weekend_weight for d in days],
        dtype=float,
    )
    w = w / w.sum()
    picked = rng.choice(days, size=n, p=w)
    return [date(year, month, int(d)) for d in picked]


def avg_tariff(services: list[dict[str, Any]]) -> float:
    """Weighted average tariff over a service subset (weight = sampling weight)."""
    w = np.array([float(s.get("weight", 1)) for s in services], dtype=float)
    t = np.array([float(s["tariff"]) for s in services], dtype=float)
    return float((w * t).sum() / w.sum()) if w.sum() else float(t.mean())


def service_group_of(code: str) -> str:
    return SERVICE_GROUP_BY_CODE.get(code, "")


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------

def build_organizations(cfg: dict[str, Any], rng: np.random.Generator) -> pd.DataFrame:
    org = cfg["organization"]
    return pd.DataFrame(
        [{
            "id": det_uuid(rng),
            "name_kk": org["name_kk"],
            "name_ru": org["name_ru"],
            "type": org["type"],
            "attached_population": int(org["attached_population"]),
        }]
    )


def build_contracts(
    cfg: dict[str, Any], org_id: str, rng: np.random.Generator
) -> tuple[pd.DataFrame, dict[int, tuple[str, str]]]:
    """One contract per calendar year covered by the period."""
    years = sorted({y for y, _ in month_seq(cfg["period"]["start"], cfg["period"]["end"])})
    rows = []
    year_map: dict[int, tuple[str, str]] = {}
    for year in years:
        contract_id = det_uuid(rng)
        version_id = det_uuid(rng)
        year_map[year] = (contract_id, version_id)
        rows.append({
            "id": contract_id,
            "org_id": org_id,
            "year": year,
            "number": f"Д-{year}-014",
            "status": "active",
        })
    return pd.DataFrame(rows), year_map


def build_contract_versions(year_map: dict[int, tuple[str, str]]) -> pd.DataFrame:
    rows = [
        {
            "id": version_id,
            "contract_id": contract_id,
            "amendment_no": 0,
            "effective_date": f"{year}-01-01",
            "note": "initial annex",
        }
        for year, (contract_id, version_id) in sorted(year_map.items())
    ]
    return pd.DataFrame(rows)


def care_type_service_groups(cfg: dict[str, Any]) -> dict[str, list[tuple[str, float, list[dict]]]]:
    """Per care_type, the (service_group, amount_share_within_ct, services) splits.

    kdu splits into ('МРТ', mrt_share, [S010]) and ('', 1-mrt_share, [rest]);
    every other care type is a single ('', 1.0, [all its services]).
    """
    mrt_share = float(cfg["contract"].get("mrt_service_group_share", 0.15))
    by_ct: dict[str, list[dict]] = {}
    for svc in cfg["tariffs"]:
        ct = CARE_TYPE_ALIASES.get(svc["care_type"], svc["care_type"])
        by_ct.setdefault(ct, []).append(svc)

    out: dict[str, list[tuple[str, float, list[dict]]]] = {}
    for ct, svcs in by_ct.items():
        groups = sorted({service_group_of(s["code"]) for s in svcs})
        if groups == [""]:
            out[ct] = [("", 1.0, svcs)]
            continue
        splits: list[tuple[str, float, list[dict]]] = []
        for sg in groups:
            sg_svcs = [s for s in svcs if service_group_of(s["code"]) == sg]
            share = mrt_share if sg == "МРТ" else (1.0 - mrt_share)
            splits.append((sg, share, sg_svcs))
        out[ct] = splits
    return out


# F3 (number naturalness): annual line plans read like negotiated contract sums,
# not machine residues. Round the line-year total to 100 000 ₸ and each month to
# 1 000 ₸, pushing the (1 000-multiple) residual into the largest-plan month so
# the 12 months sum EXACTLY to the rounded line-year total. Fact amounts stay
# ragged (real qty×tariff sums). docs/17 EPIC B F3.
LINE_YEAR_ROUND = 100_000
MONTH_ROUND = 1_000


def build_contract_lines(
    cfg: dict[str, Any],
    year_map: dict[int, tuple[str, str]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Full-calendar-year monthly lines per care_type × service_group × source.

    plan_amount (line-year) = annual ₸ target × care-type share × sg share ×
                  source share, ROUNDED to 100 000 ₸ (F3); months rounded to
                  1 000 ₸ and sum exactly to it.
    plan_qty    = plan_amount ÷ representative tariff of the line's services —
                  so fact ≈ Poisson(plan_qty × execution_profile) makes the line
                  execute at ≈ its execution_profile (the EPIC B calibration).
    """
    contract_cfg = cfg["contract"]
    seasonality = cfg["seasonality"]
    switch_year = parse_month(cfg["reform"]["unified_package_switch_date"][:7])[0]
    splits = care_type_service_groups(cfg)

    rows = []
    for year in sorted(year_map):
        contract_id, version_id = year_map[year]
        era = "post_2026" if year >= switch_year else "pre_2026"
        source_split = contract_cfg["funding_source_split"][era]
        for ct_key, amount_share in contract_cfg["care_type_split"].items():
            care_type = CARE_TYPE_ALIASES.get(ct_key, ct_key)
            weights = month_weights(year, ct_key, seasonality)
            ct_annual = float(contract_cfg["annual_target_amount"]) * float(amount_share)
            for sg, sg_share, sg_svcs in splits[care_type]:
                rep_tariff = avg_tariff(sg_svcs)
                for source in FUNDING_SOURCES:
                    s_share = float(source_split[ct_key].get(source, 0.0))
                    if s_share <= 0.0:
                        continue  # zero-plan lines excluded (docs/06 §6)
                    line_year = int(round(ct_annual * sg_share * s_share / LINE_YEAR_ROUND)) \
                        * LINE_YEAR_ROUND
                    if line_year <= 0:
                        continue
                    raw = weights * line_year
                    monthly = np.round(raw / MONTH_ROUND).astype(np.int64) * MONTH_ROUND
                    residual = int(line_year - int(monthly.sum()))
                    monthly[int(np.argmax(raw))] += residual  # residual is a 1 000-multiple
                    for mi in range(12):
                        plan_amount = int(monthly[mi])
                        rows.append({
                            "id": det_uuid(rng),
                            "contract_id": contract_id,
                            "care_type": care_type,
                            "funding_source": source,
                            "service_group": sg,
                            "month": month_key(year, mi + 1),
                            "plan_qty": int(round(plan_amount / rep_tariff)),
                            "plan_amount": plan_amount,
                            "version_id": version_id,
                        })
    return pd.DataFrame(rows)


def build_service_group_map() -> pd.DataFrame:
    """Reference: service_code → service_group (fact-side join in mv_line_execution)."""
    return pd.DataFrame(
        [{"service_code": code, "service_group": sg}
         for code, sg in sorted(SERVICE_GROUP_BY_CODE.items())]
    )


def build_doctors(cfg: dict[str, Any], org_id: str, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    idx = 1
    for dept in cfg["departments"]:
        for _ in range(int(dept["count"])):
            rows.append({
                "id": det_uuid(rng),
                "org_id": org_id,
                "full_name_masked": f"Дәрігер-{idx:03d}",
                "specialty": dept["specialty"],
                "dept": dept["name"],
                "schedule_ref": None,
            })
            idx += 1
    return pd.DataFrame(rows)


def build_patients(cfg: dict[str, Any], rng: np.random.Generator, sample: bool) -> pd.DataFrame:
    """Sex-age pyramid approximation (KZ census shape); ids are salted hashes."""
    pop_cfg = cfg["population"]
    org = cfg["organization"]
    n = int(cfg["claims"]["sample_population"] if sample else org["attached_population"])
    ref_year, _ = parse_month(cfg["period"]["start"])

    bands = pop_cfg["age_bands"]
    weights = np.array([b["weight"] for b in bands], dtype=float)
    weights = weights / weights.sum()
    mins = np.array([b["age_min"] for b in bands])
    maxs = np.array([b["age_max"] for b in bands])

    band_idx = rng.choice(len(bands), size=n, p=weights)
    spans = maxs[band_idx] - mins[band_idx] + 1
    ages = mins[band_idx] + np.floor(rng.random(n) * spans).astype(int)

    ids = [
        hashlib.sha256(f"igerim-demo-patient-{i:07d}".encode("utf-8")).hexdigest()
        for i in range(n)
    ]
    return pd.DataFrame({
        "id": ids,
        "sex": np.where(rng.random(n) < float(pop_cfg["female_share"]), "F", "M"),
        "birth_year": ref_year - ages,
        "attached": rng.random(n) < float(pop_cfg["attached_share"]),
        "insured": rng.random(n) < float(pop_cfg["insured_share"]),
        "death_date": None,  # deaths are planted only by storyline 4
    })


def build_claims(
    cfg: dict[str, Any],
    contract_lines: pd.DataFrame,
    doctors: pd.DataFrame,
    patients: pd.DataFrame,
    org_id: str,
    rng: np.random.Generator,
    sample: bool,
) -> pd.DataFrame:
    """Claim volumes ~ Poisson(plan_qty × execution_profile), per line-month.

    Services are drawn only from the line's service_group so МРТ (S010) claims
    land in the МРТ line and every other КДУ service in the '' line.
    """
    claims_cfg = cfg["claims"]
    exec_profile = cfg["execution_profile"]
    months = month_seq(cfg["period"]["start"], cfg["period"]["end"])
    period_keys = {month_key(y, m) for y, m in months}
    last_idx = month_index(*months[-1])
    paid_lag = int(claims_cfg["paid_lag_months"])
    weekend_weight = float(claims_cfg["weekend_visit_weight"])
    referral_coverage = float(claims_cfg["referral_coverage_kdu"])

    volume_scale = float(claims_cfg["sample_volume_scale"]) if sample else 1.0

    status_dist: dict[str, float] = claims_cfg["status_distribution"]
    status_names = list(status_dist.keys())
    status_p = np.array([status_dist[s] for s in status_names], dtype=float)
    status_p = status_p / status_p.sum()

    # service catalog keyed by (canonical care_type, service_group)
    services_by_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for svc in cfg["tariffs"]:
        ct = CARE_TYPE_ALIASES.get(svc["care_type"], svc["care_type"])
        services_by_group.setdefault((ct, service_group_of(svc["code"])), []).append(svc)
    svc_p_by_group = {
        key: (lambda w: w / w.sum())(np.array([float(s.get("weight", 1)) for s in svcs]))
        for key, svcs in services_by_group.items()
    }

    # doctor pools per canonical care type
    dept_care_types = {d["name"]: set(d["care_types"]) for d in cfg["departments"]}
    doctor_pool: dict[str, np.ndarray] = {}
    dept_arr = doctors["dept"].to_numpy()
    care_types = {ct for ct, _ in services_by_group}
    for ct in care_types:
        pool = [i for i, dept in enumerate(dept_arr) if ct in dept_care_types[dept]]
        doctor_pool[ct] = np.array(pool, dtype=int)
    doctor_ids = doctors["id"].to_numpy()

    # patient arrays + eligibility pool cache
    patient_ids = patients["id"].to_numpy()
    sex_arr = patients["sex"].to_numpy()
    birth_year = patients["birth_year"].to_numpy()
    attached = patients["attached"].to_numpy()
    insured = patients["insured"].to_numpy()
    pool_cache: dict[tuple[str, str, str, int], np.ndarray] = {}

    def eligible_pool(svc: dict[str, Any], ct: str, source: str, year: int) -> np.ndarray:
        key = (svc["code"], ct, source, year)
        if key not in pool_cache:
            mask = np.ones(len(patient_ids), dtype=bool)
            if "sex" in svc:
                mask &= sex_arr == svc["sex"]
            age = year - birth_year
            if "age_min" in svc:
                mask &= age >= int(svc["age_min"])
            if "age_max" in svc:
                mask &= age <= int(svc["age_max"])
            if ct == "pmsp":
                mask &= attached  # keep base data clean of accidental R06
            if source == "osms":
                mask &= insured   # keep base data clean of accidental R16
            pool_cache[key] = np.flatnonzero(mask)
        return pool_cache[key]

    source_file_id = None
    cols: dict[str, list[Any]] = {name: [] for name in CLAIM_COLUMNS}
    skipped_empty_pool = 0

    lines_in_period = contract_lines[contract_lines["month"].isin(period_keys)]
    for line in lines_in_period.itertuples(index=False):
        ct = line.care_type
        group_key = (ct, line.service_group or "")
        svcs = services_by_group.get(group_key)
        if not svcs or doctor_pool.get(ct) is None or doctor_pool[ct].size == 0:
            continue
        lam = float(line.plan_qty) * float(exec_profile[care_key(ct)]) * volume_scale
        n = int(rng.poisson(lam))
        if n <= 0:
            continue
        year, month = parse_month(line.month)
        is_paid_month = (last_idx - month_index(year, month)) >= paid_lag
        svc_choice = rng.choice(len(svcs), size=n, p=svc_p_by_group[group_key])

        for si in np.unique(svc_choice):
            svc = svcs[int(si)]
            k = int((svc_choice == si).sum())
            pool = eligible_pool(svc, ct, line.funding_source, year)
            if pool.size == 0:
                skipped_empty_pool += k
                continue

            pat_idx = rng.choice(pool, size=k)
            doc_idx = doctor_pool[ct][rng.integers(0, doctor_pool[ct].size, size=k)]
            starts = sample_dates(rng, year, month, k, weekend_weight)
            if ct == "day_hosp":
                stays = rng.integers(5, 11, size=k)
                ends = [d + timedelta(days=int(s)) for d, s in zip(starts, stays)]
            else:
                ends = starts

            statuses = [status_names[j] for j in rng.choice(len(status_names), size=k, p=status_p)]
            if is_paid_month:
                statuses = ["paid" if s == "accepted" else s for s in statuses]

            if ct == "kdu":
                has_ref = rng.random(k) < referral_coverage
                ref_uuids = iter(det_uuids(rng, int(has_ref.sum())))
                referrals = [next(ref_uuids) if flag else None for flag in has_ref]
            else:
                referrals = [None] * k

            icds = ICD10_BY_CARE_TYPE[ct]
            icd_pick = [icds[j] for j in rng.integers(0, len(icds), size=k)]
            tariff = int(svc["tariff"])

            cols["id"].extend(det_uuids(rng, k))
            cols["org_id"].extend([org_id] * k)
            cols["patient_id"].extend(patient_ids[pat_idx])
            cols["doctor_id"].extend(doctor_ids[doc_idx])
            cols["dept"].extend(dept_arr[doc_idx])
            cols["care_type"].extend([ct] * k)
            cols["funding_source"].extend([line.funding_source] * k)
            cols["service_code"].extend([svc["code"]] * k)
            cols["service_name"].extend([svc["name_ru"]] * k)
            cols["icd10"].extend(icd_pick)
            cols["date_start"].extend(d.isoformat() for d in starts)
            cols["date_end"].extend(d.isoformat() for d in ends)
            cols["qty"].extend([1] * k)
            cols["tariff"].extend([tariff] * k)
            cols["amount"].extend([tariff] * k)  # amount = qty × tariff, qty = 1
            cols["referral_id"].extend(referrals)
            cols["status"].extend(statuses)
            cols["period"].extend([line.month] * k)
            cols["source_file_id"].extend([source_file_id] * k)

    if skipped_empty_pool:
        print(f"note: skipped {skipped_empty_pool} claims with no eligible patient pool")
    return pd.DataFrame(cols, columns=CLAIM_COLUMNS)


# ---------------------------------------------------------------------------
# storyline planting context + helpers
# ---------------------------------------------------------------------------

class PlantContext:
    """Shared handles the planters mutate against (deterministic via rng)."""

    def __init__(self, cfg: dict[str, Any], org_id: str,
                 tables: dict[str, pd.DataFrame], rng: np.random.Generator) -> None:
        self.cfg = cfg
        self.org_id = org_id
        self.tables = tables
        self.rng = rng
        self.svc_by_code = {s["code"]: s for s in cfg["tariffs"]}
        months = month_seq(cfg["period"]["start"], cfg["period"]["end"])
        self.last_idx = month_index(*months[-1])
        self.paid_lag = int(cfg["claims"]["paid_lag_months"])
        doctors = tables["doctors"]
        self.dept_care_types = {d["name"]: set(d["care_types"]) for d in cfg["departments"]}
        self._doc_dept = doctors["dept"].to_numpy()
        self._doc_id = doctors["id"].to_numpy()
        self._doc_spec = doctors["specialty"].to_numpy()
        # patients reserved by a storyline (e.g. the deceased) — excluded from
        # every other planter's random pool so their planted counts stay exact.
        self.reserved: set[str] = set()

    def status_for_month(self, period: str) -> str:
        year, month = parse_month(period)
        return "paid" if (self.last_idx - month_index(year, month)) >= self.paid_lag else "accepted"

    def doctor_for(self, care_type: str) -> tuple[str, str]:
        pool = [i for i, dept in enumerate(self._doc_dept)
                if care_type in self.dept_care_types.get(dept, set())]
        i = int(self.rng.choice(pool))
        return str(self._doc_id[i]), str(self._doc_dept[i])

    def doctor_by_specialty(self, needle: str) -> tuple[str, str]:
        for i, spec in enumerate(self._doc_spec):
            if needle in spec:
                return str(self._doc_id[i]), str(self._doc_dept[i])
        return self.doctor_for("pmsp")


def make_claim(ctx: PlantContext, *, patient_id: str, doctor_id: str, dept: str,
               care_type: str, funding_source: str, code: str, icd10: str,
               day: date, status: str, referral_id: str | None = None) -> dict[str, Any]:
    svc = ctx.svc_by_code[code]
    tariff = int(svc["tariff"])
    return {
        "id": det_uuid(ctx.rng), "org_id": ctx.org_id, "patient_id": patient_id,
        "doctor_id": doctor_id, "dept": dept, "care_type": care_type,
        "funding_source": funding_source, "service_code": code,
        "service_name": svc["name_ru"], "icd10": icd10,
        "date_start": day.isoformat(), "date_end": day.isoformat(), "qty": 1,
        "tariff": tariff, "amount": tariff, "referral_id": referral_id,
        "status": status, "period": month_key(day.year, day.month),
        "source_file_id": None,
    }


def append_claims(ctx: PlantContext, rows: list[dict[str, Any]]) -> None:
    if rows:
        ctx.tables["claims"] = pd.concat(
            [ctx.tables["claims"], pd.DataFrame(rows, columns=CLAIM_COLUMNS)],
            ignore_index=True,
        )


def _patient_pool(ctx: PlantContext, *, sex: str | None = None,
                  age_min: int | None = None, age_max: int | None = None,
                  ref_year: int = 2025) -> np.ndarray:
    p = ctx.tables["patients"]
    mask = np.ones(len(p), dtype=bool)
    if sex is not None:
        mask &= p["sex"].to_numpy() == sex
    age = ref_year - p["birth_year"].to_numpy()
    if age_min is not None:
        mask &= age >= age_min
    if age_max is not None:
        mask &= age <= age_max
    ids = p["id"].to_numpy()[np.flatnonzero(mask)]
    if ctx.reserved:
        ids = ids[~np.isin(ids, np.array(sorted(ctx.reserved)))]
    return ids


# ---------------------------------------------------------------------------
# storylines (docs/06 §4, datagen/storylines.yaml) — planters mutate tables.
# Each returns a dict of computed numbers folded into the manifest.
# ---------------------------------------------------------------------------

def plant_storyline_1(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """МРТ over-execution: top up S010 (service_group МРТ) to 118% of monthly plan
    from 2026-03. Recoverable ₸ = projected 2026 over-plan spend."""
    run_rate = float(params["monthly_run_rate"])
    start_y, start_m = parse_month(params["start_month"])
    factor = float(params["recoverable_factor"])
    claims = ctx.tables["claims"]
    lines = ctx.tables["contract_lines"]

    period_end = ctx.cfg["period"]["end"]  # only boost months that carry base claims
    mrt_lines = lines[(lines["service_group"] == "МРТ") & (lines["month"].str[:4] == "2026")]
    boost_months = [mk for mk in sorted(mrt_lines["month"].unique())
                    if month_index(start_y, start_m) <= month_index(*parse_month(mk))
                    and mk <= period_end]

    rows: list[dict[str, Any]] = []
    for mk in boost_months:
        year, month = parse_month(mk)
        for src in FUNDING_SOURCES:
            sub = mrt_lines[(mrt_lines["month"] == mk) & (mrt_lines["funding_source"] == src)]
            if sub.empty:
                continue
            plan_qty = int(sub["plan_qty"].iloc[0])
            target = int(round(run_rate * plan_qty))
            existing = int(((claims["service_code"] == "S010")
                            & (claims["period"] == mk)
                            & (claims["funding_source"] == src)).sum())
            add = max(0, target - existing)
            if add == 0:
                continue
            doc_id, dept = ctx.doctor_for("kdu")
            pool = _patient_pool(ctx)
            status = ctx.status_for_month(mk)
            days = sample_dates(ctx.rng, year, month, add, 0.02)
            pats = ctx.rng.choice(pool, size=add)
            for pid, day in zip(pats, days):
                rows.append(make_claim(
                    ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                    care_type="kdu", funding_source=src, code="S010",
                    icd10="G43.9", day=day, status=status,
                    referral_id=det_uuid(ctx.rng),
                ))
    append_claims(ctx, rows)

    mrt_annual_plan = int(mrt_lines["plan_amount"].sum())
    recoverable = int(round(mrt_annual_plan * factor))
    print(f"storyline 1 (mri_over_execution): +{len(rows)} МРТ claims; "
          f"recoverable≈{recoverable:,} ₸")
    return {
        "mrt_claims_added": len(rows),
        "mrt_2026_annual_plan": mrt_annual_plan,
        "recoverable_amount": recoverable,
        "burn_out_date": params["expected_burn_out_date"],
    }


def plant_storyline_2(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """Стоматология under-execution: thin 2026 dent claims so YTD fact/plan ≈ 0.71."""
    run_rate = float(params["run_rate"])
    claims = ctx.tables["claims"]
    lines = ctx.tables["contract_lines"]

    dent_plan_ytd = int(lines[(lines["care_type"] == "dent")
                              & (lines["month"] >= "2026-01")
                              & (lines["month"] <= "2026-06")]["plan_amount"].sum())
    dent_2026 = claims[(claims["care_type"] == "dent") & (claims["period"].str[:4] == "2026")]
    fact_mask = dent_2026["status"].isin(["accepted", "paid"])
    fact_idx = dent_2026[fact_mask].index.to_numpy()
    fact_amt = ctx.tables["claims"].loc[fact_idx, "amount"].to_numpy()
    current_fact = int(fact_amt.sum())
    target_fact = int(round(run_rate * dent_plan_ytd))

    removed_ids: list[int] = []
    if current_fact > target_fact:
        # remove fact-bearing dent-2026 claims from the tail until we hit target
        running = current_fact
        for idx, amt in zip(fact_idx[::-1], fact_amt[::-1]):
            if running <= target_fact:
                break
            removed_ids.append(int(idx))
            running -= int(amt)
    if removed_ids:
        ctx.tables["claims"] = ctx.tables["claims"].drop(index=removed_ids).reset_index(drop=True)

    dent_annual_plan = int(lines[(lines["care_type"] == "dent")
                                 & (lines["month"].str[:4] == "2026")]["plan_amount"].sum())
    gap = int(round(dent_annual_plan * (1.0 - run_rate)))
    print(f"storyline 2 (dent_under_execution): -{len(removed_ids)} dent claims; "
          f"YTD run-rate→{run_rate}; year-end gap≈{gap:,} ₸")
    return {
        "dent_claims_removed": len(removed_ids),
        "dent_2026_annual_plan": dent_annual_plan,
        "expected_year_end_gap": gap,
    }


def plant_storyline_3(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """«Творческий» врач: template-identical пакеты, month-end burst, weekend services."""
    peak = int(params["peak_day_visits"])
    weekend_n = int(params["weekend_claims"])
    total = int(params["template_claims_total"])
    year, month = parse_month(params["burst_month"])
    doc_id, dept = ctx.doctor_by_specialty(params["specialty"])
    pool = _patient_pool(ctx, ref_year=year)

    rows: list[dict[str, Any]] = []
    status = ctx.status_for_month(params["burst_month"])
    burst_day = last_working_day(year, month)
    for pid in ctx.rng.choice(pool, size=peak):
        rows.append(make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                               care_type="pmsp", funding_source="osms", code="S001",
                               icd10="Z00.0", day=burst_day, status=status))
    wk_days = weekend_dates(year, month)
    for j, pid in enumerate(ctx.rng.choice(pool, size=weekend_n)):
        rows.append(make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                               care_type="pmsp", funding_source="osms", code="S001",
                               icd10="Z00.0", day=wk_days[j % len(wk_days)], status=status))
    spread = max(0, total - peak - weekend_n)
    for day in sample_dates(ctx.rng, year, month, spread, 0.0):
        pid = str(ctx.rng.choice(pool))
        rows.append(make_claim(ctx, patient_id=pid, doctor_id=doc_id, dept=dept,
                               care_type="pmsp", funding_source="osms", code="S001",
                               icd10="Z00.0", day=day, status=status))
    append_claims(ctx, rows)
    print(f"storyline 3 (creative_doctor): +{len(rows)} claims for one терапевт "
          f"(peak {peak}/day, {weekend_n} weekend)")
    return {"doctor_id": doc_id, "claims_added": len(rows),
            "peak_day_visits": peak, "weekend_claims": weekend_n}


def plant_storyline_4(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """Услуги после смерти: 2 patients with death_date, 3 claims dated after it (R01)."""
    n_patients = int(params["patients_with_death_date"])
    n_claims = int(params["claims_after_death"])
    reg_y, reg_m = parse_month(params["registry_period"])
    code = params["service_code"]
    death_day = date(2025, 10, 15)

    patients = ctx.tables["patients"]
    # pick patients from a stable slice (adults) so ids are reproducible, then
    # RESERVE them so no later planter adds a claim to a deceased patient (which
    # would inflate the "claims after death" count beyond the planted 3).
    pool = _patient_pool(ctx, age_min=45, age_max=80, ref_year=2025)
    chosen = [str(x) for x in ctx.rng.choice(pool, size=n_patients, replace=False)]
    ctx.reserved.update(chosen)

    pid_col = patients["id"].to_numpy()
    for pid in chosen:
        patients.loc[pid_col == pid, "death_date"] = death_day.isoformat()

    # remove any base claims for these patients dated after death → exactly n_claims after
    claims = ctx.tables["claims"]
    after_mask = claims["patient_id"].isin(chosen) & (claims["date_start"] > death_day.isoformat())
    if after_mask.any():
        ctx.tables["claims"] = claims[~after_mask].reset_index(drop=True)

    doc_id, dept = ctx.doctor_for("pmsp")
    status = ctx.status_for_month(params["registry_period"])
    rows: list[dict[str, Any]] = []
    for j in range(n_claims):
        pid = chosen[j % n_patients]
        day = date(reg_y, reg_m, 10 + j * 3)
        rows.append(make_claim(ctx, patient_id=pid, doctor_id=doc_id, dept=dept,
                               care_type="pmsp", funding_source="osms", code=code,
                               icd10="I10", day=day, status=status))
    append_claims(ctx, rows)
    print(f"storyline 4 (posthumous_services): {n_patients} deaths, +{n_claims} post-death claims")
    return {"patients_with_death_date": n_patients, "claims_after_death": n_claims,
            "expected_amount": int(params["expected_amount"])}


def plant_storyline_5(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """Sex/age mismatch batch in the 2025-11 registry: male mammography + underage screening."""
    reg = params["registry_period"]
    reg_y, reg_m = parse_month(reg)
    n_male = int(params["male_mammography_claims"])
    n_young = int(params["underage_screening_claims"])
    mam_code = params["male_mammography_code"]
    young_code = params["underage_screening_code"]

    doc_id, dept = ctx.doctor_for("screening")
    status = ctx.status_for_month(reg)
    rows: list[dict[str, Any]] = []

    male_pool = _patient_pool(ctx, sex="M", age_min=40, age_max=70, ref_year=reg_y)
    for j, pid in enumerate(ctx.rng.choice(male_pool, size=n_male, replace=False)):
        day = date(reg_y, reg_m, 1 + (j % 27))
        rows.append(make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                               care_type="screening", funding_source="gobmp", code=mam_code,
                               icd10="Z12.3", day=day, status=status))
    young_pool = _patient_pool(ctx, age_min=25, age_max=35, ref_year=reg_y)
    for j, pid in enumerate(ctx.rng.choice(young_pool, size=n_young, replace=False)):
        day = date(reg_y, reg_m, 2 + (j % 26))
        rows.append(make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                               care_type="screening", funding_source="gobmp", code=young_code,
                               icd10="Z12.1", day=day, status=status))
    append_claims(ctx, rows)
    print(f"storyline 5 (sex_age_mismatch_batch): +{n_male} male mammography, "
          f"+{n_young} underage screening in {reg}")
    return {"male_mammography_claims": n_male, "underage_screening_claims": n_young,
            "registry_verdict_positions": int(params["registry_verdict_positions"]),
            "registry_amount_at_risk": int(params["registry_amount_at_risk"])}


def plant_storyline_6(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """Недовыставление: 260 MIS-complete cases (status mis_only) absent from the счёт-реестр."""
    n = int(params["mis_only_cases"])
    # deterministic mix reproducing expected_amount: 240×ФГДС(8900) + 20×day_hosp neuro(42800)
    mix = [("S013", "kdu", 240), ("S039", "day_hosp", 20)]
    reg = "2026-05"
    reg_y, reg_m = parse_month(reg)
    pool = _patient_pool(ctx, ref_year=reg_y)
    rows: list[dict[str, Any]] = []
    total_amt = 0
    for code, ct, count in mix:
        doc_id, dept = ctx.doctor_for(ct)
        icd = "K29.5" if ct == "kdu" else "G54.1"
        for j, pid in enumerate(ctx.rng.choice(pool, size=count)):
            day = date(reg_y, reg_m, 1 + (j % 27))
            row = make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                             care_type=ct, funding_source="osms", code=code,
                             icd10=icd, day=day, status="mis_only")
            total_amt += int(row["amount"])
            rows.append(row)
    append_claims(ctx, rows)
    assert len(rows) == n, f"storyline 6 planted {len(rows)} != {n}"
    print(f"storyline 6 (under_billing): +{n} mis_only cases, {total_amt:,} ₸")
    return {"mis_only_cases": n, "expected_amount": total_amt}


def plant_storyline_7(ctx: PlantContext, params: dict[str, Any]) -> dict[str, Any]:
    """Reform mis-billing: 180 diabetes (E11) claims Jan–Feb 2026 billed to ГОБМП (should be ОСМС)."""
    n = int(params["claims"])
    months = params["months"]
    code = params["service_code"]
    icd = params["icd10"]
    src = params["billed_source"]
    per_month = n // len(months)
    counts = [per_month] * len(months)
    counts[-1] += n - per_month * len(months)

    rows: list[dict[str, Any]] = []
    total_amt = 0
    for reg, count in zip(months, counts):
        reg_y, reg_m = parse_month(reg)
        doc_id, dept = ctx.doctor_for("kdu")
        pool = _patient_pool(ctx, age_min=40, age_max=85, ref_year=reg_y)
        status = ctx.status_for_month(reg)
        for j, pid in enumerate(ctx.rng.choice(pool, size=count)):
            day = date(reg_y, reg_m, 1 + (j % 27))
            row = make_claim(ctx, patient_id=str(pid), doctor_id=doc_id, dept=dept,
                             care_type="kdu", funding_source=src, code=code,
                             icd10=icd, day=day, status=status, referral_id=det_uuid(ctx.rng))
            total_amt += int(row["amount"])
            rows.append(row)
    append_claims(ctx, rows)
    print(f"storyline 7 (reform_mis_billing): +{n} E11 claims on {src}, {total_amt:,} ₸")
    return {"claims": n, "expected_amount": total_amt,
            "billed_source": src, "correct_source": params["correct_source"]}


def plant_storyline_8(ctx: PlantContext, params: dict[str, Any],
                      defects: list[dict[str, Any]], demo_today: str) -> dict[str, Any]:
    """Возражения / DF-timers: 4 potential defects with 1/3/4/5 working-day deadlines.

    Data-only (no DB rows) — resolved deadline dates computed from demo_today so
    the frontend DeadlineBox / API can serve concrete or relative-day markers.
    """
    today = date.fromisoformat(demo_today)
    resolved = []
    for d in defects:
        deadline = add_working_days(today, int(d["deadline_working_days"]))
        resolved.append({
            "case_ref": d["case_ref"],
            "ekd_code": d["ekd_code"],
            "ekd_name_ru": d["ekd_name_ru"],
            "amount_at_stake": int(d["amount_at_stake"]),
            "deadline_working_days": int(d["deadline_working_days"]),
            "deadline_date": deadline.isoformat(),
        })
    total = sum(d["amount_at_stake"] for d in resolved)
    print(f"storyline 8 (objection_window): {len(resolved)} defects, "
          f"deadlines {[d['deadline_date'] for d in resolved]}")
    return {"demo_today": demo_today, "defect_count": len(resolved),
            "total_amount_at_stake": total, "defects": resolved}


def apply_storylines(tables: dict[str, pd.DataFrame], cfg: dict[str, Any],
                     org_id: str, rng: np.random.Generator) -> dict[str, Any]:
    ctx = PlantContext(cfg, org_id, tables, rng)
    report: dict[str, Any] = {}
    story_by_key = {s["key"]: s for s in cfg.get("storylines", [])}
    # posthumous_services runs FIRST so it can reserve its 2 deceased patients
    # before any other planter draws from the patient pool.
    order = ["posthumous_services"] + [k for k in story_by_key if k != "posthumous_services"]
    for key in order:
        entry = story_by_key[key]
        if not entry.get("enabled", False):
            print(f"storyline {key}: disabled, skipped")
            continue
        params = entry.get("params", {})
        if key == "mri_over_execution":
            report[key] = plant_storyline_1(ctx, params)
        elif key == "dent_under_execution":
            report[key] = plant_storyline_2(ctx, params)
        elif key == "creative_doctor":
            report[key] = plant_storyline_3(ctx, params)
        elif key == "posthumous_services":
            report[key] = plant_storyline_4(ctx, params)
        elif key == "sex_age_mismatch_batch":
            report[key] = plant_storyline_5(ctx, params)
        elif key == "under_billing":
            report[key] = plant_storyline_6(ctx, params)
        elif key == "reform_mis_billing":
            report[key] = plant_storyline_7(ctx, params)
        elif key == "objection_window":
            report[key] = plant_storyline_8(ctx, params, entry.get("defects", []),
                                            cfg.get("demo_today"))
        else:
            raise KeyError(f"unknown storyline key in storylines.yaml: {key!r}")
    return report


# ---------------------------------------------------------------------------
# F2: forecast / risk precompute — seed the analytics tables so the Overview
# renders COMPLETE at demo time (no «есептелуде…» / dashed tiles). docs/17 F2.
# Storyline lines use the planted projections; baseline lines a run-rate one.
# ---------------------------------------------------------------------------

FORECAST_YEAR = 2026
FORECAST_AS_OF = date(2026, 6, 30)
MONTHS_ELAPSED = 6  # Jan..Jun 2026


def _explain(ru: str, kk: str) -> str:
    return json.dumps({"ru": ru, "kk": kk}, ensure_ascii=False)


def _grain_rep_tariff(cfg: dict[str, Any]) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for ct, splits in care_type_service_groups(cfg).items():
        for sg, _share, svcs in splits:
            out[(ct, sg)] = avg_tariff(svcs)
    return out


def _risk_class(gap_pct: float, forced: str | None) -> str:
    if forced:
        return forced
    if gap_pct > 0.10:
        return "critical_under"
    if gap_pct > 0.05:
        return "under_risk"
    if gap_pct < -0.10:
        return "critical_over"
    if gap_pct < -0.05:
        return "over_risk"
    return "on_track"


def build_forecasts_and_risk(
    cfg: dict[str, Any], contract_lines: pd.DataFrame, claims: pd.DataFrame,
    year_map: dict[int, tuple[str, str]], storyline_report: dict[str, Any],
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One forecast + one risk_assessment per 2026 line grain (contract, care_type,
    funding_source, service_group). Storyline lines carry planted numbers."""
    contract_id = year_map[FORECAST_YEAR][0]
    rep_tariff = _grain_rep_tariff(cfg)
    burn_out = storyline_report.get("mri_over_execution", {}).get("burn_out_date")

    lines = contract_lines[contract_lines["month"].str[:4] == str(FORECAST_YEAR)]
    plan_year = (lines.groupby(["care_type", "funding_source", "service_group"])["plan_amount"]
                 .sum().astype("int64"))

    # fact YTD (accepted+paid) per grain — claims mapped to service_group by code
    cl = claims[claims["period"].str[:4] == str(FORECAST_YEAR)].copy()
    cl = cl[cl["status"].isin(["accepted", "paid"])]
    cl["service_group"] = cl["service_code"].map(service_group_of).fillna("")
    fact_ytd = (cl.groupby(["care_type", "funding_source", "service_group"])["amount"]
                .sum().astype("int64"))

    f_rows: list[dict[str, Any]] = []
    r_rows: list[dict[str, Any]] = []
    for (ct, src, sg), py in plan_year.items():
        py = int(py)
        fy = int(fact_ytd.get((ct, src, sg), 0))
        rep = rep_tariff.get((ct, sg), 1.0) or 1.0

        forced = None
        if sg == "МРТ":
            forecast = int(round(py * 1.15))          # overshoot toward burn-out
            method, forced = "ensemble", "critical_over"
            f_ru = "МРТ идёт с превышением плана; при текущем темпе годовой объём будет исчерпан ≈14.10.2026."
            f_kk = "МРТ жоспардан асып орындалуда; ағымдағы қарқында жылдық көлем ≈14.10.2026 таусылады."
            rec_ru = "Разместить доп. объёмы по пп. 25)/26) п. 19 Правил закупа (обращение в Фонд)."
            rec_kk = "Сатып алу қағидаларының 19-т. 25)/26) тармақшалары бойынша қосымша көлем орналастыру."
        elif ct == "dent":
            forecast = int(round(py * 0.71))          # storyline 2 run-rate
            method, forced = "ensemble", "critical_under"
            f_ru = "Стоматология исполняется на 71% темпа — риск недоосвоения к концу года."
            f_kk = "Стоматология қарқынның 71%-ымен орындалуда — жыл соңына игерілмеу қаупі."
            rec_ru = "Проверить кадровый дефицит; риск недоосвоения по договору."
            rec_kk = "Кадр тапшылығын тексеру; шарт бойынша игерілмеу қаупі."
        elif ct == "pmsp":
            forecast = py                              # capitation — paid in full
            method, forced = "runrate", "on_track"
            f_ru = "ПМСП оплачивается по подушевому нормативу; освоение в графике."
            f_kk = "МСАК жан басына шаққандағы норматив бойынша төленеді; игеру кестеде."
            rec_ru = "Действий не требуется."
            rec_kk = "Әрекет қажет емес."
        else:
            forecast = int(round(fy / MONTHS_ELAPSED * 12)) if fy else int(round(py * 0.9))
            method, forced = "runrate", "on_track"
            f_ru = "Прогноз по текущему темпу (run-rate); линия в графике."
            f_kk = "Ағымдағы қарқын бойынша болжам (run-rate); желі кестеде."
            rec_ru = "Действий не требуется."
            rec_kk = "Әрекет қажет емес."

        gap = py - forecast
        gap_pct = gap / py if py else 0.0
        risk_class = _risk_class(gap_pct, forced)
        line_burn = burn_out if sg == "МРТ" else None
        ihash = hashlib.sha256(f"{contract_id}|{ct}|{src}|{sg}|{FORECAST_AS_OF}".encode()).hexdigest()

        f_rows.append({
            "id": det_uuid(rng), "contract_id": contract_id, "care_type": ct,
            "funding_source": src, "service_group": sg or None,
            "as_of": FORECAST_AS_OF.isoformat(), "horizon_month": "2026-12",
            "method": method, "value_qty": int(round(forecast / rep)),
            "value_amount": int(forecast), "ci_low": int(round(forecast * 0.92)),
            "ci_high": int(round(forecast * 1.08)),
            "explanation": _explain(f_ru, f_kk), "inputs_hash": ihash,
        })
        r_rows.append({
            "id": det_uuid(rng), "contract_id": contract_id, "care_type": ct,
            "funding_source": src, "service_group": sg or None,
            "as_of": FORECAST_AS_OF.isoformat(), "class": risk_class,
            "gap_amount": int(gap), "burn_out_date": line_burn,
            "recommendation": _explain(rec_ru, rec_kk),
        })

    forecasts = pd.DataFrame(f_rows, columns=[
        "id", "contract_id", "care_type", "funding_source", "service_group",
        "as_of", "horizon_month", "method", "value_qty", "value_amount",
        "ci_low", "ci_high", "explanation", "inputs_hash"])
    risks = pd.DataFrame(r_rows, columns=[
        "id", "contract_id", "care_type", "funding_source", "service_group",
        "as_of", "class", "gap_amount", "burn_out_date", "recommendation"])
    print(f"F2: seeded {len(forecasts)} forecasts, {len(risks)} risk_assessments "
          f"({(risks['class'] != 'on_track').sum()} flagged)")
    return forecasts, risks


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

# Statuses in fixed order so the manifest is byte-stable for a given seed+mode.
MANIFEST_STATUS_ORDER: tuple[str, ...] = ("paid", "accepted", "submitted", "rejected", "mis_only")


def build_manifest(tables: dict[str, pd.DataFrame], cfg: dict[str, Any], mode: str,
                   storyline_report: dict[str, Any]) -> dict:
    """Control sums for the seed loader / integrity script (shared contract C3)."""
    claims = tables["claims"]
    lines = tables["contract_lines"]

    by_status: dict[str, dict[str, int]] = {}
    for status in MANIFEST_STATUS_ORDER:
        sub = claims[claims["status"] == status]
        if len(sub):
            by_status[status] = {"count": int(len(sub)), "amount": int(sub["amount"].sum())}

    claim_year = claims["period"].str[:4]
    line_year = lines["month"].str[:4]
    return {
        "seed": int(cfg["seed"]),
        "profile": cfg.get("_profile"),
        "mode": mode,
        "rows": {name: int(len(df)) for name, df in tables.items()},
        "claims": {
            "count": int(len(claims)),
            "total_amount": int(claims["amount"].sum()),
            "by_status": by_status,
            "by_care_type_amount": {
                str(k): int(v) for k, v in claims.groupby("care_type")["amount"].sum().items()
            },
            "by_funding_source_amount": {
                str(k): int(v)
                for k, v in claims.groupby("funding_source")["amount"].sum().items()
            },
            "by_year_amount": {
                str(k): int(v) for k, v in claims.groupby(claim_year)["amount"].sum().items()
            },
        },
        "plan": {
            "by_year_amount": {
                str(k): int(v) for k, v in lines.groupby(line_year)["plan_amount"].sum().items()
            },
            "by_year_qty": {
                str(k): int(v) for k, v in lines.groupby(line_year)["plan_qty"].sum().items()
            },
        },
        "storylines": storyline_report,
    }


def write_export_preset(out_dir: Path, claims: pd.DataFrame) -> None:
    """Emit the счёт-реестр column mapping preset + a small aligned sample (docs/17 (f))."""
    mapping = pd.DataFrame(SCHET_REESTR_EXPORT_MAP,
                           columns=["datagen_column", "schet_reestr_field", "confidence"])
    mapping.to_csv(out_dir / "export_preset_schet_reestr.csv", index=False)
    rename = {src: dst for src, dst, _ in SCHET_REESTR_EXPORT_MAP}
    sample = claims.head(200)[[src for src, _, _ in SCHET_REESTR_EXPORT_MAP]].rename(columns=rename)
    sample.to_csv(out_dir / "claims_export_sample.csv", index=False)


def write_outputs(tables: dict[str, pd.DataFrame], manifest: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"wrote {path}: {len(df):,} rows")
    if "claims" in tables:
        write_export_preset(out_dir, tables["claims"])
    manifest_path = out_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"wrote {manifest_path}")


# ---------------------------------------------------------------------------
# city-composite (light profile — summary rows only, docs/17 P3′a)
# ---------------------------------------------------------------------------

def build_city_composite(cfg: dict[str, Any], out_dir: Path) -> int:
    """14 clinics, per-clinic NORMALIZED metrics only (снятия/1000 прикреплённых).

    Marked demo aggregate — this profile does NOT generate full claim sets.
    """
    city = cfg["city"]
    rng = np.random.default_rng(int(cfg["seed"]))
    per_capita = int(city["per_capita_annual"])
    base_snyatiya = float(city["base_snyatiya_per_1000"])
    base_underbill = float(city["base_underbilling_pct"])

    rows = []
    for clinic in city["clinics"]:
        attached = int(clinic["attached"])
        jitter_s = 1.0 + float(rng.uniform(-0.35, 0.55))
        jitter_u = 1.0 + float(rng.uniform(-0.30, 0.60))
        contract = attached * per_capita
        snyatiya_per_1000 = round(base_snyatiya * jitter_s, 1)
        snyatiya_amount = int(round(snyatiya_per_1000 * attached / 1000 * 1000))
        underbilling_amount = int(round(contract * base_underbill * jitter_u))
        rows.append({
            "name_ru": clinic["name_ru"],
            "attached_population": attached,
            "contract_amount_year": contract,
            "snyatiya_per_1000": snyatiya_per_1000,
            "snyatiya_amount_year": snyatiya_amount,
            "underbilling_amount_year": underbilling_amount,
            "underbilling_pct": round(base_underbill * jitter_u * 100, 3),
            "is_demo_aggregate": True,
        })
    df = pd.DataFrame(rows).sort_values("snyatiya_per_1000", ascending=False).reset_index(drop=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "city_clinics.csv", index=False)
    manifest = {
        "seed": int(cfg["seed"]),
        "profile": cfg.get("_profile"),
        "mode": "city_composite",
        "note": "AGGREGATE demo data — normalized per-clinic city-panel metrics, no raw claims.",
        "rows": {"city_clinics": int(len(df))},
        "city": {
            "clinic_count": int(len(df)),
            "attached_total": int(df["attached_population"].sum()),
            "contract_total": int(df["contract_amount_year"].sum()),
        },
    }
    with (out_dir / "manifest.json").open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"city-composite: wrote {len(df)} clinics → {out_dir / 'city_clinics.csv'}")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    base_cfg = load_yaml(here / "config.yaml")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", default=base_cfg.get("default_profile", "gp14-real"),
                        help="datagen profile (default: gp14-real)")
    parser.add_argument("--config", type=Path, default=here / "config.yaml",
                        help="path to base config.yaml")
    parser.add_argument("--storylines", type=Path, default=here / "storylines.yaml",
                        help="path to storylines.yaml (single source of truth)")
    parser.add_argument("--out", type=Path, default=here / "output",
                        help="output directory for CSVs (default: datagen/output)")
    parser.add_argument("--sample", action="store_true",
                        help="quick run: small patient sample, scaled claim volume")
    args = parser.parse_args(argv)

    cfg = load_config(args.config, args.profile, args.storylines)
    mode = "sample" if args.sample else "full"
    print(f"igerim datagen: profile={args.profile} seed={cfg['seed']} mode={mode} "
          f"period={cfg['period']['start']}..{cfg['period']['end']}")

    if cfg.get("mode") == "city_composite":
        return build_city_composite(cfg, args.out)

    rng = np.random.default_rng(int(cfg["seed"]))
    organizations = build_organizations(cfg, rng)
    org_id = str(organizations.iloc[0]["id"])
    contracts, year_map = build_contracts(cfg, org_id, rng)
    contract_versions = build_contract_versions(year_map)
    contract_lines = build_contract_lines(cfg, year_map, rng)
    service_group_map = build_service_group_map()
    doctors = build_doctors(cfg, org_id, rng)
    patients = build_patients(cfg, rng, args.sample)
    claims = build_claims(cfg, contract_lines, doctors, patients, org_id, rng, args.sample)

    tables: dict[str, pd.DataFrame] = {
        "organizations": organizations,
        "contracts": contracts,
        "contract_versions": contract_versions,
        "contract_lines": contract_lines,
        "service_group_map": service_group_map,
        "patients": patients,
        "doctors": doctors,
        "claims": claims,
    }
    storyline_report = apply_storylines(tables, cfg, org_id, rng)

    forecasts, risks = build_forecasts_and_risk(
        cfg, tables["contract_lines"], tables["claims"], year_map, storyline_report, rng)
    tables["forecasts"] = forecasts
    tables["risk_assessments"] = risks

    plan_by_year = (
        contract_lines.merge(contracts[["id", "year"]], left_on="contract_id", right_on="id")
        .groupby("year")["plan_amount"].sum()
    )
    for year, total in plan_by_year.items():
        print(f"contract year {year}: plan {total:,} ₸")

    write_outputs(tables, build_manifest(tables, cfg, mode, storyline_report), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
