# datagen — IGERIM synthetic data generator

Skeleton implementation of **docs/06-DATA-ANALYTICS.md §4**: a deterministic
(seed=42) generator for a Поликлиника №14-like organization with 130k attached
patients, 120 doctors across 14 departments, contract years 2024–2026 built
backwards from the ≈5.2 bn ₸ annual target, and ~500k claims over 24 months
(2024-07 … 2026-06).

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r datagen/requirements.txt

# quick smoke run: ~1k claims, 5k patients
python datagen/generate.py --sample

# full run: ~500k claims, 130k patients (takes a bit longer)
python datagen/generate.py

# custom config / output dir
python datagen/generate.py --config datagen/config.yaml --out /tmp/igerim-data
```

Default output directory: `datagen/output/` (gitignored).

## Outputs (CSV, schema per docs/05 §4)

| File | Contents |
|---|---|
| `organizations.csv` | 1 org (id, name_kk, name_ru, type, attached_population) |
| `contracts.csv` | 1 contract per calendar year (2024, 2025, 2026) |
| `contract_lines.csv` | care_type × funding_source × month plan lines, full 12 months per contract year; monthly split = working days × seasonality profile |
| `patients.csv` | sex-age pyramid population; ids = salted SHA-256 hashes |
| `doctors.csv` | 120 doctors, masked names, 14 departments |
| `claims.csv` | claim volumes ~ Poisson(plan_qty × execution profile); tariffs from the 40-service mini-тарификатор; statuses 97/1.5/1.5; paid lag 1 month; 96% КДУ referral coverage |

All money values are integer ₸; ids are uuid (deterministic from the seed);
months are `YYYY-MM`; dates are ISO `YYYY-MM-DD` (UTC).

## Config (`config.yaml`)

Everything tunable lives there: seed, period, annual contract target and
care-type split (ПМСП 55% / КДУ 20% / дн. стационар 10% / стоматология 5% /
скрининги 6% / прочее 4%), funding-source splits pre/post the 2026 Единый
пакет switch (01.01.2026), seasonality profiles, claim volume targets,
status distribution, referral coverage, the mini-тарификатор and the
7 planted storylines.

## Storylines (disabled)

The 7 demo/golden-test storylines from docs/06 §4 are configured in
`config.yaml` under `storylines:` with `enabled: false`. Their planter
functions (`plant_storyline_1..7` in `generate.py`) currently raise
`NotImplementedError`; flipping a storyline to `enabled: true` before they
are implemented fails loudly by design. Implementation lands separately
(`storylines.py` per docs/05 §3 or directly in the planters).

## Known skeleton simplifications (intentional, documented)

- **Working days** = Mon–Fri; KZ public holidays are ignored for now.
- **`--sample` mode** scales only the claims volume (and patient count);
  `contract_lines` keep full-scale plans, so plan-vs-fact ratios in a sample
  run are not meaningful — it is a smoke run.
- **ICD-10 codes** are plausible hardcoded per-care-type lists in
  `generate.py` (`ICD10_BY_CARE_TYPE`) until reference CSVs land in
  `shared/ref/`.
- **ПМСП money semantics**: ПМСП is paid per capita; claim `amount` values
  for ПМСП visits are notional service prices, and ₸-level reconciliation of
  fact vs plan is a later calibration pass, not a skeleton guarantee.
- **Rejected claims** carry no ЕКД defect codes yet — those arrive with the
  fund-statement generation / storylines work.
- Base data is generated **clean** of rule violations (sex/age constraints,
  attachment, insurance are respected while sampling patients) so golden
  tests catch only planted findings.
