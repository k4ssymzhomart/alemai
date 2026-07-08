# SOLO BACKLOG — the single ordered queue

Per [11-SOLO-AGENT-PROMPT.md](11-SOLO-AGENT-PROMPT.md). This file replaces issue-based tracking. Packets execute strictly in order; each packet ends with its acceptance commands run and real output pasted into the status report. Research pack (`docs/research/`) checked at every packet boundary.

**Status legend:** `[ ]` todo · `[~]` in progress · `[x]` done (AC output exists)

## P1 — Data spine
- [ ] Alembic wired; initial migration for all 21 tables (+pgvector extension)
- [ ] `mv_line_execution` materialized view + refresh hook after seed/imports
- [ ] `make seed` = datagen → Postgres loader, idempotent, <5 min, writes control-sums manifest
- [ ] Real `/metrics/overview`, `/metrics/lines`, `/metrics/line/{key}/monthly` from the view
- [ ] `scripts/assert_seed_integrity.py` green (API totals == datagen control sums)
- [ ] Smoke tests extended; CI green with Postgres service

## P2 — Beat 1 clickable
- [ ] Overview C1 on live metrics (hero KPIs + lines table, kk default)
- [ ] Drill-down C2 (monthly bars, cumulative)
- [ ] Traffic-light risk badges (stub thresholds until P6)
- [ ] `next build` zero type errors; beat-1 screenshot in report

## P3 — 7 storylines + QA automation
- [ ] Storyline 1: МРТ 118% from 2026-03 → burn-out 14.10.2026, 12.4 млн ₸
- [ ] Storyline 2: стоматология 71% → gap 9.8 млн ₸
- [ ] Storyline 3: creative doctor (templates, ~30% weekend, 80+ day spikes)
- [ ] Storyline 4: 2 deceased patients, 3 claims after death
- [ ] Storyline 5: Nov registry — 31 male mammography + 12 underage → «143 позиции, 8.4 млн ₸»
- [ ] Storyline 6: недовыставление 260 cases ≈ 4.2 млн ₸
- [ ] Storyline 7: 180 diabetes claims Jan–Feb 2026 on ГОБМП (post-reform mis-billing)
- [ ] `scripts/assert_storylines.py` green (automated half of QA-CHECKLIST)
- [ ] Research integration: schet_reestr/damumed formats → datagen columns + adapters (when files land)

## P4 — Rules engine + full catalog
- [ ] E1 engine core (YAML → evaluator, persisted findings, runs, toggles)
- [ ] 25 rules transcribed (absorbs #4); `validate_rules.py` OK
- [ ] Reference data: тарификатор ~40 услуг, ICD-10 sets, sex/age gates, package_mapping (source: draft-needs-mentor-check) (absorbs #5 #6 #7)
- [ ] Golden tests: `pytest -m rules_golden` 7/7 (absorbs #51); `validate_rule_cases.py` OK
- [ ] 50k claims < 30s (timing printed)
- [ ] Research integration: ekd_codes/tarifikator/package_mapping swap-in (when files land)

## P5 — Reconciliation + pre-billing screens
- [ ] B3 three-way reconcile: 4 buckets ₸ + drill-down (API + screen)
- [ ] E3 pre-billing check screen: verdict header, findings by rule/severity, XLSX export
- [ ] Beat 4 shows «143 позиции, 8.4 млн ₸» live; beat 5 shows «4.2 млн ₸ / 260» live
- [ ] QA beats 1–5 manual pass

## P6 — Forecast & risk
- [ ] D1 forecast: run-rate × wd × seasonality; HW ≥24m; ensemble; bootstrap CI; explanation kk/ru
- [ ] D2 risk classes + register (ranked by ₸); D3 burn-out date
- [ ] Backtest MAPE badge; `pytest -m forecast_backtest` ≤8% synthetic
- [ ] МРТ card: 14.10.2026 + explanation visible

## P7 — Recommendations + documents
- [ ] F2 recommendation cards (₸ + deadline, docs/06 §9)
- [ ] F3 docx: заявка kk+ru, monthly report kk+ru (absorbs #53; kk flagged NEEDS-NATIVE-REVIEW)
- [ ] Template lint test (no {{}} leaks); beat 3 docx in <20s
- [ ] **Kazakh native-review batch 1 → lead** (letters + any kk to date)

## P8 — Copilot (RapidAPI GPT-4o-mini pipeline)
- [ ] `services/llm_client.py`: timeout 20s, 2 retries, logging, call counter (alarm 150), LLM_MODE=live|canned|off
- [ ] PARSE→EXECUTE→ANSWER pipeline; keyword-heuristic fallback router covering 6 demo questions
- [ ] Deterministic bilingual answer templates (numbers injected by code); optional ru POLISH behind numbers-validator
- [ ] RAG: multilingual-e5-small local embeddings (pre-downloaded, baked into image) + pgvector; adilet corpus kk+ru fetched/chunked (absorbs #3)
- [ ] Citation enforcement: uncited sentence → extractive fallback
- [ ] Canned mode: cached outputs for 6 demo questions, auto-engage on network fail
- [ ] Eval set YAML 24q (absorbs #52) + `make eval-copilot` ≥22/24
- [ ] Copilot panel UI (single response, citation chips, «как посчитано»)
- [ ] `git grep -i rapidapi` → env names/docs only; RAPIDAPI_KEY in `.env` only (lead pastes)

## P9 — Scale & alerts
- [ ] City panel: 14 clinics, 3 archetypes (beat 7)
- [ ] F1 alerts + deadlines seed (⚠️verify-with-mentors flags) (absorbs #10)
- [ ] Full UI locales kk/ru/en all screens (absorbs #50/#9); `validate_ui_strings.py` OK
- [ ] **Kazakh native-review batch 2 → lead** (locales + copilot templates)

## P10 — Freeze & stagecraft (DEMO−3h, or after P9)
- [ ] `make demo-reset` <60s (pg restore); tag `demo-stable`
- [ ] QA checklist ×2 clean, <7 min (one on battery/hotspot)
- [ ] Golden-path fallback video recorded
- [ ] docs/09 patched: solo-presenter plan + `scripts/prewarm_copilot.sh`

## Icebox

(New ideas land here as one-liners. Zero discussion until golden path is done.)

## Interrupt-the-lead queue (batched)

1. RAPIDAPI_KEY into local `.env` — needed at P8 start.
2. DEMO AT / FREEZE AT — the moment known.
3. Kazakh native-review batches: after P7 and after P9.
4. Research-pack contradictions with docs/06 specs — only if they change planted numbers/rule logic.
