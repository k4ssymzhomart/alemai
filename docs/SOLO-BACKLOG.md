# SOLO BACKLOG — the single ordered queue (EPICS A–E)

Per [11-SOLO-AGENT-PROMPT.md](11-SOLO-AGENT-PROMPT.md) laws + [17-NEXT-DIRECTIVE.md](17-NEXT-DIRECTIVE.md) compression plan (§5), restructured into gated epics for the ≤24h demo runway. Epics **A** and **D** end in a HARD STOP for the lead's review; **B** and **C** auto-continue when all AC are green. Research pack (`docs/research/`) consumed via the [16-RESEARCH-INTEGRATION.md](16-RESEARCH-INTEGRATION.md) §5 index.

**Status legend:** `[ ]` todo · `[~]` in progress · `[x]` done (AC output exists)

## Done before the epics (previous sessions)

### P1 — Data spine ✅ (2026-07-08)
- [x] Alembic migration 0001 for all 21 tables (+pgvector, composite indexes); `mv_line_execution` MV + refresh hook
- [x] `make seed` COPY loader: 497,917 claims ~15s, idempotent, manifest-verified; real `/metrics/*` endpoints
- [x] `scripts/assert_seed_integrity.py` — 81 checks PASS; CI backend job runs pgvector + seed + integrity
- Note: host ports remapped (db 55432, api 8800) — 5432/8000 belong to mova

### P2 — Beat 1 clickable ✅ (2026-07-08)
- [x] Overview C1 + drill-down C2 on live metrics, kk default; `next build` clean; NEXT_PUBLIC_API_MOCK=1 contingency

---

## EPIC A — Absorb + Reskin (≈4h) → **HARD STOP: lead approves the look**

- [x] §2 reading done (docs 17→16→15→14/13, skims of 11/QA/backlog); docs 13–18 landed into the repo
- [x] SOLO-BACKLOG restructured to epics A–E (this file); README SOLO note verified present
- [x] PD1 «Ведомость» per docs/15: Tailwind palette stripped to ink/paper (violations impossible), radius 0 global
- [x] Fonts Unbounded / Inter Tight / IBM Plex Mono via next/font (cyrillic-ext); KZ glyph gate PASSES for all faces incl. ₸ — Unbounded keeps display role
- [x] ECharts `vedomost` theme: black + decal patterns, dashed plan, hard-shadow tooltips
- [x] Restyle Overview + drill screens; live Marquee ticker (live metrics + cited regulation constants)
- [x] Components: VerdictBlock, ExecutionBar (hatch), DeadlineBox, CodeChip, StampMark (+ /design specimens page)
- [x] Logo slot (`/public/brand/logo.svg` → fallback wordmark IGERIM▮); print stylesheet (A4, chrome hidden)
- [x] AC: grep gates PASS (zero rounded-*, zero hex in app/components); glyph-gate screenshot; before/after screenshots; `npm run build` zero errors; beat 1 in new skin

## EPIC B — Data truth: rescale + manifest (≈3h) → auto-continue if green

- [x] (a) Datagen profile system: `gp14-real` DEFAULT (31,000 прикреплённых, 20 участков, ~1.2 bn ₸/yr, КПН 1,710 ₸/чел/мес, отделения per research/clinic14_facts.md §4) + `city-composite` (14 clinics 31k–120k, summary rows)
- [x] (b) `datagen/storylines.yaml` = single source of all planted numbers — 7 storylines rescaled to gp14 (kept burn-out 14.10.2026; recomputed all ₸) + storyline 8: возражения (4 потенциальных дефекта, deadlines 1/3/4/5 раб. дней)
- [x] (c) `backend/scripts/assert_storylines.py` asserts every storyline number post-seed (28 checks PASS)
- [x] (d) Regenerate docs/QA-CHECKLIST.md from the manifest by script (`gen_qa_checklist.py`; old 143/8.4/12.4 numbers dead)
- [x] (e) Export columns aligned to research/schet_reestr_columns.csv + damumed format (INFERRED marked in `export_preset_schet_reestr.csv`)
- [x] F3 (number naturalness): plan line-year → 100k, month → 1k, sum exact. F2: forecasts + risk_assessments seeded (no dead tiles).
- [x] AC: `make seed` (gp14-real) + assert_storylines PASS; QA-CHECKLIST regenerated; overview 60.8% mid-year; assert_seed_integrity 86/86

## EPIC C — GUARD: the demo's teeth (≈5h) → auto-continue if green

Original AC:
- [x] P4′ rules engine: 13-rule ЕКД catalog, real codes + edition-by-date (№68/№19), sanction math, «yellow» 2.0/7.0 (0₸), R17 from package_mapping
- [x] Golden tests: 8/8 (10 pytest) storylines caught; 50k run = 110 ms
- [x] P5′ pre-billing screen (verdict «46/168 600 ₸», findings by rule, CodeChips, StampMark on blocks, XLSX export button)
- [x] P5′ reconciliation 4 buckets (bucket 1 = 260/2 992 000 ₸, drill-down); DF-лента возражений, DeadlineBox timers 1/3/4/5 (API-authoritative), ≤2→inverted black, «молчание = автоснятие (п. 27)»
- [x] PD2 Passport on line passport (5 blocks) + pre-billing (verdict/findings structure); reconcile bucket-focused

Overview findings folded in (lead's screenshot review):
- [x] **F1** YTD-% primary + «жылдық» annual secondary; ▽/△ removed (severity → ТӘУЕКЕЛ column, server risk_class)
- [x] **F2** API read-side wired: forecast_gap 70.06M, risk_count 4, risk_class/burn_out_date/explanation/recommendation non-null → no dead tiles
- [x] **F4** ledger grouped by care type with full human names + funding child rows
- [x] **F5** 6px bar: ink/10 track, fact fill, YTD-expected tick, forecast hatch extension
- [x] **F6** kk default + fmtPct comma-decimal verified (hero + cells)
- [x] **F7** ticker rotates burn-out + nearest объection (1 day) + reconcile (260) alerts
- [x] AC: golden 8/8; timing; beats 1/2/4/5 screenshots; ≤2-day timer inverted; economist's-squint Overview shipped. (Beat 3 risk→заявка docgen = Epic D)

## EPIC D — ACT + SPEAK (≈4h) → **HARD STOP: native review + freeze GO**

- [ ] P7′ docgen: «Обращение в Фонд о размещении доп. объёмов (пп. 25)/26) п. 19 Правил закупа)» docx ru+kk with авто-расчёт остатка; возражение template; monthly report kk; all kk flagged NEEDS-NATIVE-REVIEW
- [ ] P8-lite copilot: canned mode mandatory (6 demo Q&A incl. Q13 «екі түрі» + возражение-timer), receipt-style dock UI with citation chips; live RapidAPI mode ONLY if RAPIDAPI_KEY in .env (3-stage pipeline, number-validator)
- [ ] PD3-lite: role switcher (Директор / Экономист / Статистик / Куратор УОЗ) changing nav + data scope; Settings with пороги + «О системе» (справочник versions: «ЕКД ред. №19 от 27.02.2026»); footer «демо-деректер» badge everywhere
- [ ] AC: обращение.docx both langs attached; copilot beat with network OFF; role-switch screenshots; NEEDS-NATIVE-REVIEW batch as table (key | kk | ru | confidence | question)

## EPIC E — Freeze & stagecraft (≈2h)

- [ ] `make demo-reset` <60s (pg restore); tag `demo-stable`
- [ ] Two full QA runs (one on battery + phone hotspot); screen-record full golden path as fallback video
- [ ] Print pack: Line Passport A4 + kk monthly report; pitch asset cards from 16 §3 (Qalqan answer, «38 млрд ₸ оспорено», «п. 24/п. 15», 3.4 трлн)
- [ ] Update docs/09 demo-script numbers from the manifest
- [ ] AC: two QA run logs; reset timing; video file path; asset cards committed; `git grep -i rapidapi` clean

## EPIC F — Ingest & exchange (DONE 2026-07-09, branch claude/qalam-file-exchange-c2d920)

- [x] F1 import МИС-реестра: POST /imports/mis-registry (XLSX/CSV, пресет «Damumed: реестр услуг», карантин с причинами, идемпотентный upsert по natural key, авто-запуск правил); экран «Импорт» (dropzone → Файл танылды → Маппинг → Нәтиже → «Тексеруді іске қосу»); демо-файлы генерируются из живой БД (GET /imports/samples/*) — нулевой дрейф с сидом
- [x] F2 exports (openpyxl): исключения пре-биллинга / bucket сверки / план-факт Overview / карантин; qalam_<screen>_<date>.xlsx, числа числами; read-back скрипт scripts→backend/scripts/verify_xlsx_exports.py 16/16
- [x] F3 доп. соглашение: POST /imports/contract-annex?preview=1 — диф «было → станет, Δ₸», без записи («қолдану — пилотта»); annex_2026.xlsx: МРТ +5,7 млн (объёмы из beat-3 обращения), стоматология −8,7 млн
- [x] F4 demo assets: qa_golden 16→30 checks (round-trip + идемпотентность + неизменность golden); QA-CHECKLIST beat-4-prelude; слайд 7 «[Загружает XLSX из Damumed]…»; crib-карта «Как данные попадают в систему?»
- [x] AC: demo-reset + qa_golden 30/30 ×2; pytest 50/50 (3 новых integration); npm build green; скриншот-сет kk; санитарные grep'ы чистые

## Deferred to post-demo (from the old P-queue, if time never allows)

P6 full forecast engine (manifest-precomputed forecasts cover the demo) · P8 live RAG/eval ≥22/24 · P9 city panel full + alerts engine · PD3 full 12-role matrix · adapter round-trip demo.

## Icebox

(New ideas land here as one-liners. Zero discussion until golden path is done.)

## Interrupt-the-lead queue (batched)

1. Exact pitch slot/format when known → recompute cuts if <18h (drop order: city panel, live copilot, kk-полировка; never beats 2/4/6-canned).
2. ~~RAPIDAPI_KEY into local `.env`~~ — done (key stored locally, untracked; verified `git check-ignore`).
3. Review gates: Epic A look approval; Epic D kk native review + freeze GO.
