# datagen — IGERIM synthetic data generator

Deterministic (seed=42) generator for **docs/06-DATA-ANALYTICS.md §4** with a
**profile system** (docs/17 EPIC B). The default profile `gp14-real` models the
real ГКП на ПХВ «Городская поликлиника №14» акимата г. Астаны at its actual
scale: **31,000 прикреплённых**, ~20 участков + specialists, contract years
2024–2026 built backwards from a **≈1.2 млрд ₸** annual target (ПМСП подушевой
≈ КПН 1,710 ₸/чел/мес — calibrated to the real октябрь-2025 norm), and ~508k
claims over 24 months (2024-07 … 2026-06).

## Run

```bash
pip install -r datagen/requirements.txt

# DEFAULT profile gp14-real (31k, ~1.2 млрд ₸)
python datagen/generate.py                       # full run
python datagen/generate.py --sample              # quick smoke run

# city panel: 14 clinics 31k–120k, SUMMARY rows only (снятия/1000 прикреплённых)
python datagen/generate.py --profile city-composite

# custom paths
python datagen/generate.py --profile gp14-real \
    --config datagen/config.yaml --storylines datagen/storylines.yaml --out /tmp/igerim-data
```

`make seed` (`docker compose exec api python -m app.seed`) runs the default
`gp14-real` profile in-container, then COPYs into Postgres and refreshes the MV.
Default output directory: `datagen/output/` (gitignored).

## Configuration layout

| File | Role |
|---|---|
| `config.yaml` | **base** (shared): seed, period, reform switch, seasonality, population pyramid, mini-тарификатор (40 услуг), claim params, `default_profile` |
| `profiles/gp14-real.yaml` | **DEFAULT**: organization (31k), contract (1.2 млрд ₸ + splits), real №14 department mix, `execution_profile` (the calibration) |
| `profiles/city-composite.yaml` | 14-clinic city panel (light — summary rows only) |
| `storylines.yaml` | **single source of truth** for every planted number (8 storylines). `assert_storylines.py` + `gen_qa_checklist.py` read from it |

`--profile` deep-merges the chosen profile over `config.yaml`.

## Calibration (docs/17 EPIC B, the headline)

`plan_qty` is **derived** from `plan_amount ÷ representative tariff` per line, so
fact ≈ `Poisson(plan_qty × execution_profile)` makes a line execute at ≈ its
`execution_profile`. This reconciles plan-vs-fact so:

- **ПМСП runs low (~37%)** — подушевой capitation is paid in full, but the
  fee-for-service documented объём covers only ~38% of it (the big two lines).
- **fee-for-service specialities read a healthy 85–105%** (baseline lines).
- **МРТ 108%** (storyline 1 over-exec), **стоматология 71%** (storyline 2).
- mid-year (as-of 2026-06) **overview execution ≈ 61%** — verified live.

**F3 (number naturalness):** line-year plans round to 100 000 ₸, months to
1 000 ₸ (residual pushed to the largest month so 12 months sum exactly). Fact
amounts stay ragged (real qty×tariff sums).

## Outputs (CSV, schema per docs/05 §4)

`organizations`, `contracts`, `contract_versions`, `contract_lines`,
`service_group_map` (S010→МРТ, feeds the MV fact-join), `patients`, `doctors`,
`claims`, **`forecasts`** + **`risk_assessments`** (F2 precompute — one per 2026
line grain, so the Overview renders complete with no dead tiles), plus
`manifest.json` (control sums + a `storylines` block) and
`export_preset_schet_reestr.csv` / `claims_export_sample.csv` (счёт-реестр column
mapping, INFERRED columns marked — docs/17 EPIC B (f)).

All money = integer ₸; ids = uuid (deterministic); months `YYYY-MM`; dates ISO.

## Storylines (all 8 enabled)

Defined in `storylines.yaml`, planted by `plant_storyline_1..8` in `generate.py`,
and asserted post-seed by `backend/scripts/assert_storylines.py` (28 checks):

1. **mri_over_execution** — МРТ (service_group) at 118% run-rate from 2026-03; burn-out 14.10.2026; возместимо ≈5.67 млн ₸.
2. **dent_under_execution** — стоматология thinned to 71% YTD run-rate; год-конец gap ≈17.4 млн ₸.
3. **creative_doctor** — one терапевт, 80 визитов на пик-день + 30 выходных.
4. **posthumous_services** — 2 умерших + 3 услуги после смерти (patients reserved so the count stays exact).
5. **sex_age_mismatch_batch** — реестр 11.2025: 31 маммография мужчинам + 12 скринингов вне возраста.
6. **under_billing** — 260 mis_only случаев (≈2.99 млн ₸) вне счёт-реестра.
7. **reform_mis_billing** — 180 диабет-E11 на ГОБМП вместо ОСМС (ЗПДН).
8. **objection_window** — 4 потенциальных дефекта из ИСФ с окнами возражения 1/3/4/5 раб. дней (data-only, in the manifest for the DeadlineBox).

## Known simplifications (intentional)

- **Working days** = Mon–Fri; KZ public holidays ignored (also for objection-deadline math).
- **`--sample`** scales claim volume (`sample_volume_scale`) + patient count; `contract_lines` keep full plans, so a sample run is a smoke test, not a calibrated one.
- **ICD-10** are plausible hardcoded per-care-type lists (`ICD10_BY_CARE_TYPE`); diabetes E10*/E11* are excluded from base lists so base data stays clean of accidental R17 (planted only by storyline 7).
- Base data is generated **clean** of rule violations (sex/age/attachment/insurance respected) so the rules engine catches only planted findings.
