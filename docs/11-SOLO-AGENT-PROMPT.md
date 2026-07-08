# 11 — NEXT AGENT PROMPT (SOLO MODE)

> Paste everything below this line into the coding agent as its next instruction.

---

You are the engineering agent for **IGERIM** — Task 07 (OSMS/GOBMP contract execution monitoring), Health AI Hackathon Astana 2026, repo `github.com/k4ssymzhomart/alemai`. The hackathon is live. Read `docs/00-INDEX.md` → `docs/08-EXECUTION.md` → `docs/QA-CHECKLIST.md` first; the doc pack (00–10) remains the source of truth for WHAT to build. This prompt overrides it on WHO builds and in WHAT ORDER.

## 0. Context delta — SOLO MODE

The two juniors (folrwix, rasssppberrry) are **out**. The team is now: Kassymzhomart (lead/human) + you (+ your subagents). Consequences, effective immediately:

1. **All 11 fenced junior tasks (#3–#8, #10, #50–#53) are absorbed by you.** Their outputs are still required — the validators and CI gates you built now referee YOUR work.
2. **All management overhead is dead.** No branch protection, no ownership-fence, no kickoff comments, no labels/assignees backfill, no PAT-permission waiting. Do not spend one more minute on GitHub API management. Issues stay as a passive backlog reference; the live plan is this prompt.
3. **Process simplification:** work on short-lived branches, self-merge when CI is green; small commits; `main` always demoable (unchanged law). PR ceremony only where CI needs a PR to run — otherwise commit directly.
4. **#54 QA runner is you.** After every merge that touches the golden path, self-run `docs/QA-CHECKLIST.md` (or the automated equivalent you'll build in P3) and record pass/fail in the commit/PR description.
5. The human's time is now the scarcest resource. Batch everything you need from him; interrupt only for the four inputs in §6.
6. **No MedHub data is coming — organizers provided none.** SYNTHETIC mode is FINAL: datagen IS the dataset, and realism is our job. A parallel Claude Cowork research session (tasked via `docs/12-RESEARCH-PROMPT.md`) is filling `docs/research/` with real-world formats and reference data (ЕКД codes, счёт-реестр structure, tariffs, 2026 package mapping, МИС export shapes). Integration points are marked in §3; never block on research — build from docs/06 specs, upgrade when files land.
7. **LLM provider changed: no Anthropic key.** The copilot runs on the lead's RapidAPI GPT-4o-mini subscription — P8 is redesigned around it. The key lives ONLY in local `.env` as `RAPIDAPI_KEY` (lead pastes it himself); it must never appear in any tracked file, log, issue, or commit.

## 1. Standing laws (unchanged — from the doc pack)

- Golden path (docs/04 §8) is the only definition of progress. Every packet below names the demo beat it unlocks.
- No number reaches the UI that the system didn't compute; synthetic data labeled «демо-данные» in the footer.
- `shared/glossary.csv` is terminology law for UI, copilot, and documents. No hardcoded UI strings — i18n keys only (kk default / ru / en).
- Explainability everywhere: every forecast ships its explanation sentence; every rule finding ships its bilingual message and evidence.
- Neutral language on doctor analytics («требует проверки», never accusations).
- Conventional commits referencing story IDs (e.g., `feat(D3): burn-out date`).

## 2. Housekeeping (hard cap: 30 minutes, then stop)

1. Remove the `ownership-fence` CI job (no non-lead authors exist anymore). Keep `data-gates` (all five validators) and lint/test/build jobs exactly as they are.
2. Add a `SOLO MODE` note to README + CONTRIBUTING: one paragraph, link to this file.
3. Create `docs/SOLO-BACKLOG.md`: the single ordered queue = packets P1–P10 below, each with its checkbox list. This file replaces issue-based tracking; update it as you go.
4. If (and only if) the GitHub token happens to allow it, batch-close #3–#10, #50–#54 with the one-line comment "absorbed into docs/SOLO-BACKLOG.md (solo mode)". If it 403s, skip forever — do not debug the token.

## 3. Build order — work packets

Execute strictly in order unless a packet is blocked; then start the next one and return. Each packet ends with: run the named acceptance commands, paste their real output into the status report, tick the SOLO-BACKLOG boxes. Parallelize inside packets with subagents (as you did for the scaffold), but integration to `main` is serialized. If stuck >15 min on one approach, switch approach or descope and note it.

**Research pack protocol (`docs/research/`):** check for new/updated files at every packet boundary (`git pull` + `ls docs/research/`). Consume: `schet_reestr_format.md` + `damumed_export_format.md` → datagen columns & import adapters (P3); `ekd_codes.csv`, `tarifikator_sample.csv`, `package_mapping_2026.csv` → rules reference data (P4); `regs/` → RAG corpus (P8); `hackathon_intel.md` → DEMO AT + judging (replan per docs/08 §8); `calibration_stats.md` → datagen amounts. Every consumed file: keep the `source:` provenance column so draft vs confirmed data stays distinguishable.

### P1 — Data spine (unlocks everything)
Wire the DB for real: alembic migration for all 21 tables; `make seed` = datagen → Postgres loader (idempotent, <5 min); build `mv_line_execution` materialized view + refresh hook after imports/seed; implement real `/metrics/overview`, `/metrics/lines`, `/metrics/line/{key}/monthly` reading the view.
**AC:** `docker compose up && make seed` from clean state succeeds; `curl /api/v1/metrics/overview` returns totals equal to datagen's control sums (write `scripts/assert_seed_integrity.py` that proves it); smoke tests extended and green.

### P2 — Beat 1 clickable
Overview C1 + drill-down C2 wired to live metrics; kk locale rendering by default; traffic-light risk badges may stub thresholds until P6.
**AC:** golden beat 1 works in browser; screenshot in report; `next build` zero type errors.

### P3 — The 7 planted storylines + QA automation (the demo's spine)
Implement storylines in datagen with EXACT numbers the QA checklist expects: (1) МРТ line at 118% from 2026-03 → burn-out **14.10.2026**, recoverable **12.4 млн ₸**; (2) стоматология at 71% → year-end gap **9.8 млн ₸**; (3) "creative doctor" — template-identical packages, ~30% weekend services, 80+ visits day spikes at month-end; (4) 2 patients with death_date + **3 claims after death**; (5) November registry: **31 маммография male + 12 underage screenings**, total pre-billing verdict **«143 позиции, 8.4 млн ₸»** (pad with minor findings to hit exactly 143/8.4); (6) недовыставление **260 cases ≈ 4.2 млн ₸**; (7) **180 diabetes claims Jan–Feb 2026 billed to ГОБМП** that map to ОСМС post-reform.
Also: `scripts/assert_storylines.py` — asserts every planted number after seed (this becomes the automated half of QA-CHECKLIST).
When `docs/research/schet_reestr_format.md` / `damumed_export_format.md` land: align datagen export columns and the import adapters to the real field names/shapes, so the demo line «система принимает стандартные выгрузки» is literally true against realistic files.
**AC:** assert_storylines passes; numbers match docs/QA-CHECKLIST.md to the digit.

### P4 — Rules engine + full catalog (beat 4 backend)
Rules engine core E1 (YAML → evaluator, persisted findings, runs) + transcribe all 25 rules from docs/06 §7 (absorbs junior #4) + golden tests: each storyline caught by its intended rule (absorbs #51); reference data the rules need: mini-тарификатор (~40 услуг, prices per docs/06 §4), ICD-10 sets, sex/age gates, package_mapping with 2026 effective dates (absorbs #5, #6, #7 — generate from the docs specs; mark `package_mapping` rows with `source: draft-needs-mentor-check`). When `docs/research/` delivers `ekd_codes.csv` / `tarifikator_sample.csv` / `package_mapping_2026.csv`, swap drafts for researched rows (`source: research-confirmed`) — rule messages should then cite real ЕКД codes, which is a jury moment.
**AC:** `pytest -m rules_golden` 7/7; 50k claims run <30s (print timing); `validate_rule_cases.py` OK.

### P5 — Reconciliation + pre-billing screens (beats 4–5 complete)
B3 three-way reconcile (4 buckets with ₸ totals, drill-down) + E3 pre-billing check screen (verdict header, findings by rule/severity, export exceptions XLSX) + reconcile screen.
**AC:** beat 4 shows «143 позиции, 8.4 млн ₸» live; beat 5 shows «4.2 млн ₸ / 260» live; QA beats 1–5 manual pass.

### P6 — Forecast & risk (beat 2)
D1 forecast (run-rate × working days × seasonality, Holt-Winters when history ≥24m, ensemble, bootstrap CI, explanation sentence kk/ru) + D2 risk classes + register + D3 burn-out date + backtest MAPE badge.
**AC:** МРТ card shows 14.10.2026 with explanation; `pytest -m forecast_backtest` MAPE ≤8% on synthetic; risk register ranks by ₸.

### P7 — Recommendations + documents (beat 3)
F2 recommendation cards (₸ + deadline per docs/06 §9) + F3 docx generation: заявка на корректировку kk+ru, monthly management report kk+ru (absorbs #53 — you draft the letter templates; flag both kk texts `NEEDS-NATIVE-REVIEW` for the lead, batch into one review request).
**AC:** beat 3 generates a filled docx in kk in <20s from the risk card; no `{{placeholder}}` leaks (add template lint test).

### P8 — Copilot (beat 6) — RapidAPI GPT-4o-mini pipeline (no Anthropic key)
LLM access = the lead's RapidAPI subscription: `POST https://gpt-4o-mini.p.rapidapi.com/chat/completions`, headers `x-rapidapi-host: gpt-4o-mini.p.rapidapi.com`, `x-rapidapi-key: ${RAPIDAPI_KEY}` (lead pastes into `.env`; add empty entry to `.env.example`). Assume the worst of the wrapper: **no function calling, no streaming, no embeddings endpoint, unknown rate limits** — and design so the model being small/weak cannot hurt us:

**Three-stage pipeline — the mini model NEVER produces numbers:**
1. **PARSE** (1 LLM call): question → strict JSON `{intent: data|regulation|report|oos, metric, filters, group_by, period, lang}`. Metric whitelist + JSON schema embedded in the prompt; response parsed with pydantic; one retry with the validation error fed back; second failure → keyword-heuristic router (build it — it must fully cover the 6 demo questions on its own).
2. **EXECUTE** server-side: semantic layer (`metrics.yaml`, ~15 metrics per docs/06 §5) builds and runs SQL. Same whitelist design as docs/05 §6 — unchanged.
3. **ANSWER**: default = **deterministic bilingual sentence templates** (kk/ru written by us from glossary.csv; numbers injected by code, LLM untouched — perfect Kazakh, zero hallucination risk). Optional POLISH call (ru only) guarded by the numbers-validator (every numeral in output must appear in tool results); validator fail → ship the template answer silently.

**Regulations Q&A without an embeddings API:** local `sentence-transformers` model `intfloat/multilingual-e5-small` (works kk/ru, offline after first download — **pre-download during P8 setup and bake into the docker image**; venue Wi-Fi is not to be trusted) → pgvector as designed. Fetch the 6 adilet documents kk+ru (docs/02 §9, or take from `docs/research/regs/` if the researcher already saved them), chunk, embed (absorbs #3). Answer path: retrieve top-k → mini model answers ONLY from chunks with `[cite:id]` per sentence → validator: uncited sentence → extractive fallback (quote the top chunk verbatim with its citation). Dry but bulletproof.

**Client (`services/llm_client.py`):** 20s timeout, 2 retries with backoff, full request/response logging, daily call counter with alarm at 150 calls (quota unknown — budget ~200/day), env kill-switch `LLM_MODE=live|canned|off`. **Canned mode stays mandatory**: cached full pipeline outputs for the 6 rehearsed demo questions, auto-engaged on network failure — demo-identical.

Also: eval set YAML of the 24 questions from docs/07 §6 (absorbs #52) + `make eval-copilot` (template answers count as valid) + copilot panel UI (no SSE needed now — single response render with citation chips and «как посчитано» trace).
**AC:** one live round-trip smoke call logged (sanitized); eval ≥22/24 in pipeline mode; canned mode identical with network off; Q1 kk answer number equals the dashboard number; `git grep -i rapidapi` in the repo returns only env-var names and docs — never a key.
**Pitch upgrade (say it louder than we planned):** «Цифры вообще не проходят через языковую модель — она только разбирает вопрос. Ответ собирает система.» A weak model made the architecture stronger; own it on stage.

### P9 — Scale & alerts (beat 7)
City panel (14 synthetic clinics, 3 risk archetypes) + alerts F1 + deadlines seed (`korrektirovka_window` etc. as configurable seed marked ⚠️verify-with-mentors, absorbs #10) + UI locales completion for all screens kk/ru/en (absorbs #50/#9 — you write them from glossary.csv; flag kk for native review in the same batch as P7).
**AC:** beat 7 renders; `validate_ui_strings.py` OK; alert feed shows storyline-driven alerts (burn-out <45d, критический риск).

### P10 — Freeze & stagecraft (starts at DEMO−3h, or after P9 if DEMO AT unknown)
`make demo-reset` (<60s, pg restore) + tag `demo-stable` + full QA checklist ×2 (once on battery/hotspot) + screen-record the full golden path as fallback video + patch docs/09 with a **solo-presenter plan**: single narrator-driver flow, copilot pre-warm script (`scripts/prewarm_copilot.sh`) run before stage, beat 7 = designated skip if over time.
**AC:** two consecutive clean QA runs <7 min; video file exists; demo-stable tag pushed.

## 4. Absorbed content tasks — quality bar

You generate what the juniors would have: rules YAML, reference CSVs, ICD-10 sets, locales, letter templates, eval set, regs corpus. Two rules: (a) everything machine-validated by the existing validators + tests — green validator = done, same standard as before; (b) everything Kazakh-language gets `NEEDS-NATIVE-REVIEW` markers and goes to the lead in **at most two batched review requests** (after P7 and after P9), each ≤30 min of his time, presented as a diff-friendly table (key | kk | ru | your confidence | question).

## 5. Reporting protocol

After each packet: ≤10-line status — packet, AC command outputs (real, pasted), QA beats now passing, next packet, blockers, batched questions. If running long/overnight sessions: end with a morning report — same format plus "decisions I made alone that you should sanity-check" (list every judgment call on domain semantics, especially anything touching ЕКД logic, package mapping, or Kazakh phrasing).

## 6. The only four things to interrupt the lead for

1. **Research pack questions** — if a `docs/research/` file contradicts docs/06 specs in a way that changes planted numbers or rule logic, flag before integrating (otherwise integrate silently at packet boundaries).
2. **RAPIDAPI_KEY into local `.env`** at P8 start (he has it; never let it into the repo).
3. **DEMO AT / FREEZE AT** — the moment known, recompute the plan against docs/08 §8 compression table and post the revised packet schedule.
4. **Kazakh native review batches** (two, per §4) — now also covering the copilot answer templates from P8.

## 7. Do NOT

- Do not touch GitHub labels/assignees/comments/branch-protection again, or debug the PAT.
- Do not redesign the schema, swap frameworks, or refactor the scaffold beyond what packets need.
- Do not add features outside the packets (icebox them in SOLO-BACKLOG with one line).
- Do not let a red `main` survive longer than the current packet.
- Do not present any unverified claim as done — AC output or it didn't happen.
- Do not write the RapidAPI key (or any credential) into any tracked file, log output, issue, or commit message — `.env` only; `.gitignore` must cover it; verify with `git grep` before every push that touches P8.
- Do not wait for research files — synthetic-from-specs first, upgrade later.

Start now with §2 housekeeping, then P1. First status report after P1.
