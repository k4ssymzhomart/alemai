"""Golden tests — every planted storyline is caught with the expected count/₸.

Truth source: ``datagen/storylines.yaml`` (loaded live, so the tests can never
drift from the planted numbers). Marker ``rules_golden``. Skips cleanly when the
database is unreachable or unseeded.

Coverage (8/8 storylines):
  S1 mri_over_execution   -> risk_assessment critical_over + burn_out (F2)
  S2 dent_under_execution -> risk_assessment critical_under + year-end gap (F2)
  S3 creative_doctor      -> R10 (burst >= 80/day) + R11 (>= 30 weekend/mo)
  S4 posthumous_services  -> R01 (ЕКД 5.1)
  S5 sex_age_mismatch     -> R02 + R03 + block-verdict (46 / 168 600 ₸)
  S6 under_billing        -> reconcile bucket 1 (mis_only)
  S7 reform_mis_billing   -> R17 (ЕКД 11.0, 2026 источник)
  S8 objection_window     -> objections API (4 defects, working-day deadlines)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import sqlalchemy as sa
import yaml
from sqlalchemy.exc import SQLAlchemyError

from app.db import get_engine, get_sessionmaker
from app.models.enums import RiskClass
from app.models.rules import Finding, RuleRun
from app.services import reconcile as recon_svc
from app.services.metrics import queries
from app.services.rules_engine import engine
from app.services.rules_engine import objections as obj_svc

pytestmark = pytest.mark.rules_golden


def _load_storylines() -> dict[str, dict]:
    for candidate in (
        os.environ.get("DATAGEN_DIR"),
        "/datagen",
        str(Path(__file__).resolve().parents[2] / "datagen"),
    ):
        if not candidate:
            continue
        path = Path(candidate) / "storylines.yaml"
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return {s["key"]: s for s in data.get("storylines", [])}
    pytest.skip("storylines.yaml not found")


@pytest.fixture(scope="module")
def stories() -> dict[str, dict]:
    return _load_storylines()


@pytest.fixture(scope="module")
def sm():
    try:
        with get_engine().connect() as conn:
            claims = conn.execute(sa.text("SELECT count(*) FROM claims")).scalar_one()
    except SQLAlchemyError as exc:
        pytest.skip(f"database unreachable: {type(exc).__name__}")
    if not claims:
        pytest.skip("claims empty — run `python -m app.seed` first")
    return get_sessionmaker()


def _agg(result: engine.RunResult, code: str) -> tuple[int, int]:
    agg = result.by_rule.get(code)
    return (agg.count, agg.amount_at_risk) if agg else (0, 0)


# --------------------------------------------------------------------------- S1
def test_storyline_1_mri_over_execution(sm, stories) -> None:
    params = stories["mri_over_execution"]["params"]
    with sm() as session:
        projections = queries.line_projections(session, 2026)
    mrt = [p for key, p in projections.items() if key[3] == "МРТ"]
    assert mrt, "no МРТ line projection seeded"
    assert all(p.risk_class == RiskClass.critical_over for p in mrt)
    assert all(str(p.burn_out_date) == params["expected_burn_out_date"] for p in mrt)


# --------------------------------------------------------------------------- S2
def test_storyline_2_dent_under_execution(sm, stories) -> None:
    params = stories["dent_under_execution"]["params"]
    with sm() as session:
        _, items = queries.lines(session, 2026, care_type="dent")
    assert items and all(i.risk_class == RiskClass.critical_under for i in items)
    gap = sum(i.forecast_gap for i in items if i.forecast_gap is not None)
    expected = params["expected_year_end_gap"]
    assert abs(gap - expected) <= expected * params["run_rate_tol"], f"{gap} vs {expected}"


# --------------------------------------------------------------------------- S3
def test_storyline_3_creative_doctor(sm, stories) -> None:
    params = stories["creative_doctor"]["params"]
    with sm() as session:
        result = engine.run(session, scope=f"period:{params['burst_month']}")
        session.rollback()
    r10_count, _ = _agg(result, "R10")
    r11_count, _ = _agg(result, "R11")
    assert r10_count >= params["peak_day_visits"], "R10 did not catch the day-burst"
    assert r11_count >= params["weekend_claims"], "R11 did not catch weekend anomaly"


# --------------------------------------------------------------------------- S4
def test_storyline_4_posthumous(sm, stories) -> None:
    params = stories["posthumous_services"]["params"]
    with sm() as session:
        result = engine.run(session, scope=f"period:{params['registry_period']}")
        session.rollback()
    count, amount = _agg(result, "R01")
    assert count == params["claims_after_death"]
    assert amount == params["expected_amount"]


# --------------------------------------------------------------------------- S5
def test_storyline_5_sex_age_and_registry_verdict(sm, stories) -> None:
    params = stories["sex_age_mismatch_batch"]["params"]
    with sm() as session:
        result = engine.run(session, scope=f"period:{params['registry_period']}")
        session.rollback()
    assert _agg(result, "R02") == (
        params["male_mammography_claims"], params["male_mammography_amount"]
    )
    assert _agg(result, "R03") == (
        params["underage_screening_claims"], params["underage_screening_amount"]
    )
    # Pre-billing verdict «N позиций / ₸ под риском» = block-severity slice.
    assert result.block_positions == params["registry_verdict_positions"]
    assert result.block_amount == params["registry_amount_at_risk"]


# --------------------------------------------------------------------------- S6
def test_storyline_6_under_billing(sm, stories) -> None:
    params = stories["under_billing"]["params"]
    with sm() as session:
        buckets = recon_svc.buckets(session)
    bucket1 = next(b for b in buckets if b.bucket_no == 1)
    assert bucket1.rows_count == params["mis_only_cases"]
    assert bucket1.total_amount == params["expected_amount"]


# --------------------------------------------------------------------------- S7
def test_storyline_7_reform_source(sm, stories) -> None:
    params = stories["reform_mis_billing"]["params"]
    with sm() as session:
        result = engine.run(session, scope="year:2026")
        session.rollback()
    count, amount = _agg(result, "R17")
    assert count == params["claims"]
    assert amount == params["expected_amount"]


# --------------------------------------------------------------------------- S8
def test_storyline_8_objections(stories) -> None:
    story = stories["objection_window"]
    params = story["params"]
    today, items = obj_svc.list_objections()
    assert str(today) == "2026-07-09"  # demo anchor (storylines.yaml demo_today)
    assert len(items) == params["defect_count"]
    assert sum(o.amount_at_stake for o in items) == params["total_amount_at_stake"]
    by_ref = {o.case_ref: o for o in items}
    for defect in story["defects"]:
        served = by_ref[defect["case_ref"]]
        assert served.ekd_code == defect["ekd_code"]
        assert served.deadline_working_days == defect["deadline_working_days"]
    # Concrete deadlines from demo_today 2026-07-09, weekends skipped.
    assert sorted(str(o.deadline_date) for o in items) == [
        "2026-07-10", "2026-07-14", "2026-07-15", "2026-07-16",
    ]


# ---------------------------------------------------------------- timing + persist
def test_50k_claim_timing(sm) -> None:
    with sm() as session:
        result = engine.run(session, scope="all", limit=50000)
        session.rollback()
    print(
        f"\n[timing] 50k-cap run: scanned={result.claims_scanned:,} "
        f"findings={result.total_findings:,} in {result.duration_ms} ms"
    )
    assert result.claims_scanned <= 50000
    assert result.duration_ms < 30000


def test_run_persists_and_findings_readback(sm) -> None:
    with sm() as session:
        result = engine.run(session, scope="period:2025-11")
        session.commit()
        run_id = result.run_id
    try:
        with sm() as session:
            persisted = session.execute(
                sa.select(sa.func.count()).select_from(Finding).where(Finding.run_id == run_id)
            ).scalar_one()
            run_row = session.get(RuleRun, run_id)
            assert run_row is not None and run_row.totals["block_positions"] == 46
        assert persisted == result.total_findings > 0
    finally:  # keep the DB clean for reseeds / other suites
        with sm() as session:
            session.execute(sa.delete(Finding).where(Finding.run_id == run_id))
            session.execute(sa.delete(RuleRun).where(RuleRun.id == run_id))
            session.commit()
