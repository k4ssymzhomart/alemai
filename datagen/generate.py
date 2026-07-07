#!/usr/bin/env python3
"""IGERIM synthetic data generator (skeleton) — docs/06-DATA-ANALYTICS.md §4.

Builds one polyclinic-like organization, contract years 2024–2026 backwards
from the annual ₸ target (monthly split = working days × seasonality, both
funding sources with the 2026 Единый пакет switch), a sex-age-pyramid
population, 120 doctors across 14 departments, and claim volumes drawn as
Poisson around plan × execution profile with tariffs from the mini-тарификатор
and plausible hardcoded ICD-10 lists per care type (until shared/ref lands).

Storylines 1–7 are configured (datagen/config.yaml, all disabled); their
planter functions raise NotImplementedError until implemented.

Conventions (docs/05 §4): money integer ₸, ids uuid (deterministic from seed),
dates ISO, months "YYYY-MM", all times UTC.

Usage:
    python datagen/generate.py [--config datagen/config.yaml]
                               [--out datagen/output] [--sample]
"""

from __future__ import annotations

import argparse
import calendar
import hashlib
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

CLAIM_COLUMNS: list[str] = [
    "id", "org_id", "patient_id", "doctor_id", "dept", "care_type",
    "funding_source", "service_code", "service_name", "icd10",
    "date_start", "date_end", "qty", "tariff", "amount",
    "referral_id", "status", "period", "source_file_id",
]

# Plausible ICD-10 stubs per care type; replaced by shared/ref CSVs later.
ICD10_BY_CARE_TYPE: dict[str, list[str]] = {
    "pmsp": ["J06.9", "J20.9", "I10", "E11.9", "K29.7", "M54.5",
             "J45.0", "N30.0", "H66.9", "L20.8", "Z00.0"],
    "kdu": ["I25.1", "G43.9", "K21.0", "E04.1", "M42.1", "I67.8",
            "K80.2", "N20.0", "H52.1", "J31.0", "E11.9", "I11.9"],
    "day_hosp": ["I11.9", "E11.7", "K29.5", "G54.1", "N11.1", "M51.1", "I67.8"],
    "dent": ["K02.1", "K04.5", "K05.1", "K08.1", "K04.0"],
    "screening": ["Z12.3", "Z12.4", "Z12.1", "Z13.1", "Z13.6"],
    "ambulance": ["R10.4", "R51", "I20.0", "J06.9", "T14.9", "R07.4"],
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def care_key(care_type: str) -> str:
    """Canonical care_type value → config key (e.g. 'ambulance' → 'other')."""
    return CARE_KEY_BY_TYPE.get(care_type, care_type)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


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
    """One contract per calendar year covered by the period.

    Returns the contracts frame and {year: (contract_id, base_version_id)}.
    Base version = "без доп. соглашений"; amendments (A2) come later.
    """
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


def build_contract_lines(
    cfg: dict[str, Any],
    year_map: dict[int, tuple[str, str]],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Full-calendar-year monthly lines per care type × funding source.

    plan_amount: annual ₸ target × care-type share × month weight × source share.
    plan_qty:    annual claims-volume target × row share, split the same way —
                 so that Poisson claim volumes are anchored to the plan.
    Lines cover all 12 months of each contract year (claims cover the period
    only) so year-end forecasting has a full plan to burn against.
    """
    contract_cfg = cfg["contract"]
    claims_cfg = cfg["claims"]
    seasonality = cfg["seasonality"]
    switch_year = parse_month(cfg["reform"]["unified_package_switch_date"][:7])[0]

    period_months = month_seq(cfg["period"]["start"], cfg["period"]["end"])
    annual_rows_target = claims_cfg["target_rows"] / len(period_months) * 12

    rows = []
    for year in sorted(year_map):
        contract_id, version_id = year_map[year]
        era = "post_2026" if year >= switch_year else "pre_2026"
        source_split = contract_cfg["funding_source_split"][era]
        for ct_key, amount_share in contract_cfg["care_type_split"].items():
            care_type = CARE_TYPE_ALIASES.get(ct_key, ct_key)
            weights = month_weights(year, ct_key, seasonality)
            annual_amount = float(contract_cfg["annual_target_amount"]) * float(amount_share)
            annual_qty = annual_rows_target * float(claims_cfg["care_type_row_share"][ct_key])
            for mi in range(12):
                for source in FUNDING_SOURCES:
                    s_share = float(source_split[ct_key].get(source, 0.0))
                    if s_share <= 0.0:
                        continue  # zero-plan lines excluded (docs/06 §6)
                    rows.append({
                        "id": det_uuid(rng),
                        "contract_id": contract_id,
                        "care_type": care_type,
                        "funding_source": source,
                        "service_group": None,
                        "month": month_key(year, mi + 1),
                        "plan_qty": int(round(annual_qty * weights[mi] * s_share)),
                        "plan_amount": int(round(annual_amount * weights[mi] * s_share)),
                        "version_id": version_id,
                    })
    return pd.DataFrame(rows)


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
    n = int(org["sample_population"] if sample else org["attached_population"])
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
    """Claim volumes ~ Poisson(plan_qty × execution profile), per line-month."""
    claims_cfg = cfg["claims"]
    months = month_seq(cfg["period"]["start"], cfg["period"]["end"])
    period_keys = {month_key(y, m) for y, m in months}
    last_idx = month_index(*months[-1])
    paid_lag = int(claims_cfg["paid_lag_months"])
    weekend_weight = float(claims_cfg["weekend_visit_weight"])
    referral_coverage = float(claims_cfg["referral_coverage_kdu"])

    volume_scale = (
        float(claims_cfg["sample_target_rows"]) / float(claims_cfg["target_rows"])
        if sample else 1.0
    )
    exec_profile = claims_cfg["execution_profile"]

    status_dist: dict[str, float] = claims_cfg["status_distribution"]
    status_names = list(status_dist.keys())
    status_p = np.array([status_dist[s] for s in status_names], dtype=float)
    status_p = status_p / status_p.sum()

    # service catalog per canonical care type
    services_by_ct: dict[str, list[dict[str, Any]]] = {}
    for svc in cfg["tariffs"]:
        ct = CARE_TYPE_ALIASES.get(svc["care_type"], svc["care_type"])
        services_by_ct.setdefault(ct, []).append(svc)
    svc_p_by_ct = {
        ct: (lambda w: w / w.sum())(np.array([float(s.get("weight", 1)) for s in svcs]))
        for ct, svcs in services_by_ct.items()
    }

    # doctor pools per canonical care type
    dept_care_types = {d["name"]: set(d["care_types"]) for d in cfg["departments"]}
    doctor_pool: dict[str, np.ndarray] = {}
    dept_arr = doctors["dept"].to_numpy()
    for ct in services_by_ct:
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

    source_file_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "igerim://datagen/claims"))
    cols: dict[str, list[Any]] = {name: [] for name in CLAIM_COLUMNS}
    skipped_empty_pool = 0

    lines_in_period = contract_lines[contract_lines["month"].isin(period_keys)]
    for line in lines_in_period.itertuples(index=False):
        ct = line.care_type
        svcs = services_by_ct.get(ct)
        if not svcs or doctor_pool[ct].size == 0:
            continue
        lam = float(line.plan_qty) * float(exec_profile[care_key(ct)]) * volume_scale
        n = int(rng.poisson(lam))
        if n <= 0:
            continue
        year, month = parse_month(line.month)
        is_paid_month = (last_idx - month_index(year, month)) >= paid_lag
        svc_choice = rng.choice(len(svcs), size=n, p=svc_p_by_ct[ct])

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
# storylines (docs/06 §4) — stubs; disabled in config until implemented.
# Each planter mutates `tables` (dict of DataFrames) in place.
# ---------------------------------------------------------------------------

def plant_storyline_1(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """МРТ over-execution: КДУ/МРТ at 118% of monthly plan from 2026-03,
    burn-out ≈ 2026-10-14, recoverable ≈ 12.4 mln ₸ at корректировка."""
    raise NotImplementedError("storyline 1 (mri_over_execution) not implemented yet")


def plant_storyline_2(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """Стоматология under-execution: 71% run-rate → year-end gap ≈ 9.8 mln ₸."""
    raise NotImplementedError("storyline 2 (dent_under_execution) not implemented yet")


def plant_storyline_3(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """«Творческий» врач: template-identical packages, 30% weekend services,
    80+ visits/day at month-end → R10/R11/R22 + anomaly cluster."""
    raise NotImplementedError("storyline 3 (creative_doctor) not implemented yet")


def plant_storyline_4(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """Услуги после смерти: 2 patients with death_date, 3 claims after it → R01."""
    raise NotImplementedError("storyline 4 (posthumous_services) not implemented yet")


def plant_storyline_5(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """Sex/age mismatch batch: 31 male mammographies + 12 under-age screenings
    in the 2025-11 registry → R02/R03/R20."""
    raise NotImplementedError("storyline 5 (sex_age_mismatch_batch) not implemented yet")


def plant_storyline_6(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """Недовыставление: 260 MIS-complete cases (≈4.2 mln ₸) absent from the
    submitted registry (status mis_only) → reconciliation bucket 1."""
    raise NotImplementedError("storyline 6 (under_billing) not implemented yet")


def plant_storyline_7(tables: dict[str, pd.DataFrame], params: dict[str, Any],
                      rng: np.random.Generator) -> None:
    """Reform mis-billing: 180 diabetes claims in Jan–Feb 2026 billed to ГОБМП
    instead of ОСМС → R17."""
    raise NotImplementedError("storyline 7 (reform_mis_billing) not implemented yet")


STORYLINE_PLANTERS = {
    "mri_over_execution": plant_storyline_1,
    "dent_under_execution": plant_storyline_2,
    "creative_doctor": plant_storyline_3,
    "posthumous_services": plant_storyline_4,
    "sex_age_mismatch_batch": plant_storyline_5,
    "under_billing": plant_storyline_6,
    "reform_mis_billing": plant_storyline_7,
}


def apply_storylines(tables: dict[str, pd.DataFrame], cfg: dict[str, Any],
                     rng: np.random.Generator) -> None:
    for entry in cfg.get("storylines", []):
        key = entry["key"]
        if key not in STORYLINE_PLANTERS:
            raise KeyError(f"unknown storyline key in config: {key!r}")
        if entry.get("enabled", False):
            STORYLINE_PLANTERS[key](tables, entry.get("params", {}), rng)
        else:
            print(f"storyline {key}: disabled, skipped")


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def write_outputs(tables: dict[str, pd.DataFrame], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"wrote {path}: {len(df):,} rows")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, default=here / "config.yaml",
                        help="path to config.yaml (default: datagen/config.yaml)")
    parser.add_argument("--out", type=Path, default=here / "output",
                        help="output directory for CSVs (default: datagen/output)")
    parser.add_argument("--sample", action="store_true",
                        help="quick run: ~1k claims, small patient sample")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    rng = np.random.default_rng(int(cfg["seed"]))
    mode = "sample" if args.sample else "full"
    print(f"igerim datagen: seed={cfg['seed']} mode={mode} period="
          f"{cfg['period']['start']}..{cfg['period']['end']}")

    organizations = build_organizations(cfg, rng)
    org_id = str(organizations.iloc[0]["id"])
    contracts, year_map = build_contracts(cfg, org_id, rng)
    contract_lines = build_contract_lines(cfg, year_map, rng)
    doctors = build_doctors(cfg, org_id, rng)
    patients = build_patients(cfg, rng, args.sample)
    claims = build_claims(cfg, contract_lines, doctors, patients, org_id, rng, args.sample)

    tables: dict[str, pd.DataFrame] = {
        "organizations": organizations,
        "contracts": contracts,
        "contract_lines": contract_lines,
        "patients": patients,
        "doctors": doctors,
        "claims": claims,
    }
    apply_storylines(tables, cfg, rng)

    # plan sanity: annual contract totals (rounding drift expected to be tiny)
    plan_by_year = (
        contract_lines.merge(contracts[["id", "year"]], left_on="contract_id", right_on="id")
        .groupby("year")["plan_amount"].sum()
    )
    for year, total in plan_by_year.items():
        print(f"contract year {year}: plan {total:,} ₸")

    write_outputs(tables, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
