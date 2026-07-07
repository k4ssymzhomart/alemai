# 04 — PRODUCT SPEC: IGERIM

Vision: **the clinic-side control loop for ГОБМП/ОСМС contracts** — see execution live, catch defects before billing, forecast risks before they become losses, act with generated documents, and speak to the data in Kazakh. One product, five pillars: SEE · GUARD · FORESEE · ACT · SPEAK.

Positioning sentence (use verbatim in pitch): «Igerim — это финансовый автопилот исполнения договора: он видит, предупреждает, считает деньги и сам готовит документы — на казахском и русском.»

---

## 1. Users & access (RBAC)

| Role | Sees | Key screens |
|---|---|---|
| Экономист (Айгерім) | everything on own clinic | Overview, Risks, Корректировка, Alerts |
| Статистик (Дана) | claims/defects | Pre-billing check, Reconciliation |
| Руководитель (Ерлан/Бақыт) | aggregates + reports | Overview, Report generator, Copilot |
| Куратор (Марат) | multi-clinic aggregates only (no patient-level) | City panel |

Hackathon: 4 hardcoded users, role switch in header (great for demo narration: "теперь я — главврач").

## 2. Screens (information architecture)

1. **Обзор договора (Overview)** — hero KPIs: % игерілуі YTD, forecast gap ₸, risk count by class, снятия MTD. Table of contract lines: plan/fact/forecast/risk badge/burn-out date. Filters: source (ГОБМП/ОСМС), care type, period. [C1, C2, C3]
2. **Тәуекелдер (Risk register)** — ranked by ₸ at stake; each row → recommendation card with [Сформировать заявку]. [D2, D5, F2, F3]
3. **Тексеру (Pre-billing check)** — upload/select registry → verdict header → findings by rule/severity → export exceptions / "исключить из счёта" toggles. [E1–E3]
4. **Салыстыру (Reconciliation)** — four discrepancy buckets with ₸ totals, drill to claim. [B3]
5. **Аномалии (Anomalies)** — doctor/day outliers, template packages, weekend services; each with plain-language explanation. [E4]
6. **Күнтізбе & ескертулер (Calendar & alerts)** — deadline calendar + alert feed. [F1]
7. **Көмекші (Copilot)** — chat panel, docked right on every screen + full-page mode; answer cards render numbers, mini-charts, citations. [G2, G3]
8. **Есептер (Reports)** — monthly management report generator (kk/ru), download docx/pdf. [G4]
9. **Қала панелі (City panel)** — 14 clinics ranked by composite risk; click → clinic overview. [C5]
10. **Админ** — data imports (A1/A2/B1/B2/B4), rule toggles [H2], reference mappings [A4].

Design language: clean, data-dense, no cartoon dashboards; dark-on-light; accent color teal/#0e7c66 (health+finance, not "startup purple"); Kazakh default locale visible in every screenshot. Numbers: `12 480 500 ₸` (space thousands, ₸ after).

## 3. Pillar specs (behavior contracts)

### SEE
- All aggregates computed from claim-level data, never hand-entered; every KPI clickable to its rows ("no dead numbers").
- Period logic: договорный год; MTD/YTD; amendments respected as of date (A2).

### GUARD
- Rules run: on import, on demand, and pre-billing; findings idempotent per (run, rule, claim).
- Severity: `block` (would be rejected/fined — exclude from registry), `warn` (review), `info`.
- Every finding message bilingual, cites rule origin ("ЕКД-логика: услуга после даты смерти").
- Anomaly ≠ accusation: UI language is "требует проверки", never "приписка" against a named doctor. Ethics + jury optics (01 §8).

### FORESEE
- Forecast per line monthly; stored with method, inputs hash, CI; recompute on data change.
- Explanation string mandatory — the UI never shows a forecast without its "почему".
- Backtest: hold out last 3 months on seed data, show MAPE per care type in a small "точность прогноза" badge. Target MAPE ≤ 8% on synthetic; honest number on real data.

### ACT
- Recommendation = {risk, action type (заявка ↑/↓ объёма, перераспределение, capacity, campaign), ₸ impact, deadline, artifact generator}.
- Document generation: docx templates with jinja placeholders; RU + KZ variants; all numbers from DB at generation time; filename convention `zayavka_korrektirovka_YYYY-MM-DD.docx`.

### SPEAK
- Copilot capabilities exactly three: data Q&A (text-to-SQL over semantic layer), regulations Q&A (RAG with citations), report drafting. Anything else → polite refusal with the three capabilities listed.
- Language: answer in the language of the question; UI locale sets default. Kazakh terminology from glossary enforced via system prompt (07 §5).
- Hard guardrail: no number in an answer that didn't come from a tool result. (07 §4.)

## 4. Non-functional requirements (hackathon-calibrated)

| NFR | Target | Why |
|---|---|---|
| Seeded demo dataset | ~130k patients, 18–24 mo, ~500k service rows | big enough to feel real, small enough to reseed fast |
| Dashboard load | <2s p95 on seed | pre-aggregated views/materialized tables |
| Rules run 50k claims | <30s | demo happens live |
| Copilot answer | <8s p95 | jury patience |
| Import 50k rows | <60s with progress bar | live upload during demo is a wow, but risky — pre-rehearse |
| Uptime strategy | laptop-local docker + cloud mirror + screen-recording fallback | 08 §7 contingency |
| Languages | kk (default), ru, en | the bet |
| Data safety | no real ФИО/ИИН ever; hashed ids; sandbox data stays in sandbox | jury question guaranteed |

## 5. i18n spec (this is a pillar, not a chore)

- Library-level: all UI strings in `locales/kk.json`, `ru.json`, `en.json`; keys namespaced (`risk.class.critical_under`). PR checklist blocks hardcoded strings.
- Terminology single source: 02 §10 glossary → a shared `glossary.csv` consumed by (a) UI locales build, (b) copilot system prompt, (c) docx templates. One place to fix a term.
- Kazakh pluralization/number formatting via `Intl` with `kk-KZ`; dates: `07.07.2026`.
- Demo default = Kazakh; switch to RU mid-demo once, to show it's real, then back.

## 6. Data ethics & privacy posture (say this proactively on stage)

- Input data is anonymized by MedHub; we additionally hash any patient identifier on ingest (salted SHA-256), store only sex/birth-year/status flags needed by rules.
- Death-date data used ONLY for defect prevention (R01), sourced from the sandbox dataset.
- Doctor-level analytics framed as process quality, not personal scoring; access gated by role.
- Пилот: on-prem deploy inside clinic perimeter possible (docker-compose), no data leaves the clinic; LLM can be swapped to local KazLLM — sovereignty answer ready (09 §5 Q6).

## 7. Out of scope (say "no" fast, in writing)

- Live HL7/FHIR/МИС API integration (pilot phase promise; adapters for exports now).
- Auth hardening, SSO, password reset; multi-region deploy.
- Mobile app. (Responsive web is enough; mention Telegram alerts as the mobile touchpoint.)
- Payments/бухгалтерия integration (1С) — mention as roadmap only.
- Clinical quality analytics (letality, протоколы) — different task; don't dilute.

## 8. Golden demo path (the product must make THIS flawless)

1. Kazakh UI. Ерлан's overview: «игерілуі 61%, болжам: 3 тәуекел». One red line: МРТ.
2. Click МРТ → forecast band: exhausted **14 октября**; burn-out card; explanation sentence visible.
3. Risk register → recommendation: «заявка до 15.09 → 12.4 млн ₸» → [Сформировать] → docx opens in Kazakh, numbers filled.
4. Switch role → Дана → Pre-billing check on November registry: «143 позиции, 8.4 млн ₸ под риском», incl. **3 услуги после даты смерти** and **31 скрининг не того пола** — "то, что нашёл аудит Минфина, мы ловим до счёта".
5. Reconciliation: «4.2 млн ₸ оказано, но не выставлено» — recovered money from thin air.
6. Copilot, in Kazakh, live: «Қараша айында қандай тәуекелдер бар?» → numbers + chart; follow-up: «Мониторинг қандай түрлерге бөлінеді?» → answer citing приказ ҚР ДСМ-321/2020.
7. Finale: City panel — 14 clinics, Марат's view: «а теперь — весь город». Impact slide.

Every engineering decision is judged by one question: **does it make §8 stronger?**
