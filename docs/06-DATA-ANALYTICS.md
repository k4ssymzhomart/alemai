# 06 — DATA PLAN & ANALYTICS ENGINE

Covers: what data we expect, the first-hour triage protocol when MedHub data drops, the synthetic dataset that guarantees a cinematic demo regardless, metric definitions, forecast math, risk scoring, the defect rules catalog, anomaly detection, and how we prove accuracy.

---

## 1. Data sources (expected from MedHub sandbox / Polyclinic №14)

| Dataset | Grain | Must-have fields | Powers |
|---|---|---|---|
| Договор + приложения | line × month | care_type, source, month, plan_qty, plan_amount | SEE, FORESEE |
| Доп. соглашения | amendment | line deltas, effective_date | A2 versioning |
| МИС выгрузка услуг/случаев | claim | patient_hash, sex, birth_year, doctor, dept, service_code, icd10, dates, qty, tariff, amount, referral | everything |
| Портал ФСМС: статусы/снятия | claim × status | accepted/rejected/paid, defect codes, amounts | GUARD, waterfall |
| РПН (прикреплённое население) | month × sex-age | counts | подушевой analytics, R06 |
| Статус застрахованности | patient | insured flag/date | R16/R17 |
| Справочники | — | тарификатор, КЗГ, МКБ-10, услуги, ЕКД codes | rules, mapping |
| Графики смен (if lucky) | doctor × day | shifts | R10/R11 |

## 2. Hour-one data triage protocol (run the moment real data lands)

1. `wc -l` / row counts, period coverage, grain check per file → fill the **Data Reality Board** (a pinned issue): dataset × {have/missing/partial, period, quality notes}.
2. Key joins sanity: % claims with resolvable patient, doctor, service_code; % with amounts. >90% → green.
3. Compare schema vs our `claims` model → write adapter mapping YAML per file (ingest is adapter-based, 05 §3).
4. Decision within 60 min: **REAL / HYBRID / SYNTHETIC** demo data mode. Criteria: real data covers ≥2 quarters + joins green → HYBRID (real base + planted storylines on top); else SYNTHETIC. Never demo on unverified real data.
5. Ask mentors immediately: current корректировка windows, exact ЕКД code list, sample счёт-реестр format, Damumed export capabilities at №14.

**Deadline discipline: triage never exceeds 90 minutes. The demo cannot depend on data we don't control.**

## 3. Honesty rules (jury trust is the asset)

- Synthetic/hybrid data is **labeled in the UI footer**: «демо-данные, откалиброваны по открытой статистике».
- Impact numbers on slides carry "модельная оценка" tag with assumptions listed in appendix.
- Forecast accuracy shown as backtest MAPE, computed, not asserted.

## 4. Synthetic data generator (datagen/generate.py)

Parameters (config.yaml): seed=42, org=Поликлиника №14-подобная, attached=130,000 (sex-age pyramid from KZ census shape), doctors=120 across 14 depts, period=2024-07…2026-06 (24 months), locale of names: masked ids only.

**Contract:** built backwards from target ≈ **5.2 bn ₸/year**: ПМСП подушевой ~55%, КДУ ~20%, дневной стационар ~10%, стоматология ~5%, скрининги ~6%, прочее ~4%. Monthly split by working days + seasonality. Both sources: ГОБМП/ОСМС per package_mapping (pre/post 2026 reform switch on 01.01.2026 — the generator itself demonstrates reform-awareness).

**Claims:** ~500k rows/24mo. Per care type: volumes ~ Poisson around plan×execution profile; tariffs from a mini-тарификатор (40 услуг: МРТ 18 500 ₸, КТ 12 300 ₸, УЗИ 4 200 ₸, приём терапевта 2 100 ₸, ФГДС 8 900 ₸…); ICD-10 sampled from care-type-plausible sets; referrals present for 96% КДУ (rest → R07 findings); statuses: 97% accepted, 1.5% rejected with ЕКД-style codes, 1.5% pending; paid lag 1 month.

**Seasonality profiles:** ПМСП visits: winter ОРВИ peak (Dec–Feb ×1.25), August dip (×0.8); КДУ: Nov–Dec rush (×1.3) — "год закрывают"; screenings: campaign waves Mar & Sep; дневной стационар flat.

**Planted storylines (fixtures for demo AND golden tests):**
1. **МРТ over-execution** — КДУ/МРТ line runs at 118% of monthly plan from March 2026 → burn-out date lands ~14 Oct 2026; recoverable at корректировка ≈ 12.4 mln ₸.
2. **Стоматология under-execution** — 71% run-rate (staff attrition) → projected year-end неосвоение ≈ 9.8 mln ₸ → recommendation: перераспределение + запись campaign.
3. **"Творческий" врач** — one терапевт with template-identical service packages, 30% weekend services without shifts, day-volume spikes to 80+ visits at month-end → anomaly cluster + R10/R11/R22 findings.
4. **Услуги после смерти** — 2 patients with death_date, 3 claims after it (echoes the Minfin audit) → R01 catches 100%.
5. **Sex/age mismatch batch** — 31 маммография claims for male patients + 12 under-age screenings planted in the November registry → R02/R03/R20; pre-billing verdict shows «143 позиции, 8.4 млн ₸» (with other minor findings).
6. **Недовыставление** — 260 completed MIS cases (≈4.2 mln ₸) absent from submitted registry → reconciliation bucket 1.
7. **Reform mis-billing** — 180 diabetes-related claims in Jan–Feb 2026 still billed to ГОБМП (should be ОСМС post-reform) → R17 → "новое правило 2026 года уже встроено".

City panel: clone org with ±noise into 14 clinics, 3 risk archetypes distributed.

## 5. Metrics dictionary (semantic layer `metrics.yaml` — copilot can use ONLY these)

| Metric | Formula (per line/period unless noted) |
|---|---|
| plan_qty / plan_amount | from active contract version |
| fact_qty / fact_amount | claims accepted+paid (configurable statuses) |
| execution_pct (игерілуі) | fact_amount / plan_amount_ytd × 100 |
| billed_amount | submitted+accepted+paid |
| снято_amount | rejected amount (by rule/ЕКД group) |
| недовыставлено_amount | MIS-complete claims not in any registry |
| forecast_amount / forecast_gap | year-end forecast; forecast − annual plan |
| burn_out_date | date cumulative forecast qty ≥ annual plan qty |
| risk_class | thresholds on projected gap (D2) |
| findings_count / findings_amount | open findings by severity/rule |
| paid_lag_days | avg(paid_date − submitted_date) |
| defect_rate | снято_amount / billed_amount |
| forecast_mape | backtest accuracy per care_type |

## 6. Forecast methodology (D1) — explainable by design

For each line ℓ, month m with actuals A_1..A_k (k = current month):
1. **Base run-rate:** R = Σ recent-3-months A / Σ working_days those months → daily rate; project month m̂: R × working_days(m̂).
2. **Seasonal index** S_m: from ≥24m history via classical decomposition; else default per-care-type profile (§4); final projection F_m̂ = R × wd(m̂) × S_m̂ / S̄_recent.
3. **Holt-Winters** (statsmodels, additive) when history ≥24m and non-degenerate; **ensemble** = 0.5·runrate + 0.5·HW; else run-rate only.
4. **CI:** residual bootstrap on backtest errors → p10/p90 band.
5. **Year-end:** F_year = ΣA + Σ F_remaining. Every stored forecast carries `explanation` (auto-built sentence, kk/ru) + `inputs_hash`.
6. **Backtest:** hold out last 3 known months, forecast them, MAPE per care_type shown in UI badge. Target ≤8% synthetic; report honestly on real.
Edge cases: new line mid-year → plan-proportional prior; zero-plan lines excluded; amendment changes plan → risk recomputed, forecast unchanged (forecast models demand, not plan).

## 7. Defect rules catalog (rules/*.yaml; severity: B=block, W=warn, I=info)

Origin tags: [ЕКД] classifier logic, [АУДИТ] Dec-2025 Minfin findings, [СВЕРКА] reconciliation, [2026] reform.

| Code | Rule | Logic sketch | Sev |
|---|---|---|---|
| R01 | Услуга после даты смерти [АУДИТ] | claim.date_start > patient.death_date | B |
| R02 | Услуга не соответствует полу [АУДИТ] | service_code ∈ sex_gated ∧ patient.sex ≠ required | B |
| R03 | Услуга не соответствует возрасту | age(claim) ∉ service.age_range | B |
| R04 | Дубликат услуги | same patient+service+date (or key set) count>1 | B |
| R05 | Пересечение эпизодов | overlapping inpatient/day-hosp episodes; амбул. услуги во время стационара в другой орг. | W |
| R06 | Пациент не прикреплён (ПМСП) | care_type=pmsp ∧ ¬attached | B |
| R07 | КДУ без направления | care_type=kdu ∧ referral required ∧ referral_id null | B |
| R08 | Диагноз↔услуга несовместимы | (icd10, service) ∉ compatibility matrix | W |
| R09 | Диагноз↔специальность врача | icd10 chapter ∉ doctor.specialty scope | W |
| R10 | Невозможный объём врача/день [АУДИТ] | Σ visits(doctor,day) > threshold (default 60) ∨ Σ норма-минуты > смена×1.5 | W |
| R11 | Услуги вне графика/выходные | claim.date ∉ doctor shifts (if shifts data) else weekend ∧ dept non-24/7 | W |
| R12 | Врач неактивен/без профиля | doctor terminated ∨ specialty mismatch service | W |
| R13 | Повторная госпитализация < N дней | same patient, same КЗГ group, <30д | W |
| R14 | Незавершённый случай выставлен | status incomplete ∧ in registry | B |
| R15 | Тариф ≠ тарификатор | \|claim.tariff − ref.tariff\| > 0 | B |
| R16 | Пациент не застрахован (ОСМС-услуга) [2026] | source=osms ∧ ¬insured(date) | B |
| R17 | Неверный источник финансирования [2026] | package_mapping(icd10/service, date) ≠ claim.source | B |
| R18 | Превышена кратность услуги | count(patient, service, window) > limit | W |
| R19 | Назначения детям вне возрастных норм [АУДИТ] | drug/service ∧ age < min_age | B |
| R20 | Скрининг вне целевой группы/периодичности | screening ∧ (age∉target ∨ last_screening < interval) | B |
| R21 | Услуга умершему врачу приписана / stale справочник | doctor.status=archived | I |
| R22 | Шаблонные пакеты услуг [АУДИТ] | ≥N patients of one doctor with identical service sets same day | W |
| R23 | Геонесовместимость визитов | same patient, >1 org, same timeslot | I |
| R24 | Аномальный всплеск в конце периода | last-3-days volume > μ+3σ of daily | I |
| R25 | «Пустая ЭМК» | billed claim with no clinical records linked (if MIS export has them) | W |

Reconciliation checks (not "defects", money finders) [СВЕРКА]: X1 rendered-not-billed; X2 billed-not-in-MIS; X3 accepted-not-paid aging >45д; X4 amount mismatch MIS vs portal.

YAML shape:
```yaml
- code: R02
  severity: block
  scope: claim
  origin: АУДИТ-2025
  params: {sex_gated: {mammography: F, psa: M, cervical: F}}
  message_ru: "Услуга {service} несовместима с полом пациента"
  message_kk: "{service} қызметі пациенттің жынысына сәйкес келмейді"
```

## 8. Anomaly detection (E4) — explainability first

- Per-doctor daily volume z-score (robust, median/MAD) → flag >3.5.
- Template detection: jaccard similarity of service sets across a doctor's same-day patients; flag clusters ≥0.9 sim, ≥5 patients.
- Weekend/off-hours share per dept vs peers.
- IsolationForest over doctor-month feature vectors (volume, avg amount, weekend %, duplicate rate, distinct services) → top-k "требует проверки" list.
- Output language: neutral («требует проверки», reasons listed), never accusatory. Every flag carries its raw evidence rows.

## 9. Recommendation logic (F2/D5)

Mapping risk→action (rule-based, transparent):
- critical over-execution → «заявка на увеличение объёма» + ₸=projected unpaid overage; deadline = next корректировка window − 3 days.
- critical under-execution → «заявка на уменьшение/перераспределение» (protect from clawback + next-year cut) + capacity/campaign suggestions per care type (screenings → outreach campaign; КДУ → slot expansion).
- X1 недовыставление → «довыставить в следующий реестр», ₸ = bucket total.
- findings block-level → «исключить из счёта до исправления», ₸ = amount at risk (fine avoided).
Reallocation proposal (D5): greedy match under-exec donors → over-exec recipients within same funding source; output table for заявка docx.

## 10. Evaluation before demo (gate in 08 §6)

- Golden tests: every planted storyline caught by its intended rule/module (7/7).
- Backtest MAPE per care type ≤ 8% (synthetic).
- Reconciliation buckets exactly match planted numbers (4.2 mln ₸ etc.).
- Copilot eval set (07 §6) ≥ 22/24 pass.
- Demo-reset → golden path click-through < 7 min, zero errors, twice in a row.
