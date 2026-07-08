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
- [ ] P4′ rules engine: ≥12 rules covering all storylines (R01–R04, R07, R10, R11, R16, R17, R20 + as needed), real ЕКД code + sanction columns (ekd_notes.md §4); ЕКД version by claim date (ред. №68 → ред. №19, код 1.3 archived); «жёлтые» severity 2.0/7.0 (0 ₸); R17 from package_mapping_2026.csv
- [ ] Golden tests: 8/8 storylines caught; 50k claims timing printed
- [ ] P5′ pre-billing screen (verdict header, findings by rule, CodeChips, StampMark on block rows, export exceptions XLSX)
- [ ] P5′ reconciliation 4 buckets; DF-лента возражений with DeadlineBox timers (5/3/3 раб. дней, working-day aware, «молчание = автоснятие (п. 27)», ≤2 days → inverted black box)
- [ ] PD2 Passport pattern on line passport, pre-billing, reconcile: Кто я → Вердикт → Почему → Что делать → Данные(collapsed); breadcrumbs; «как посчитано» popovers; designed empty states

Overview findings folded in (lead's screenshot review, now Epic C AC):
- [ ] **F1** execution semantics: primary % = fact_ytd/plan_ytd (verify API already does this); annual as secondary 11px «жылдық: X%»; replace ambiguous ▽/△ glyphs with the §4 severity chip system (soft hatch/outline)
- [ ] **F2** no dead tiles: wire the API read-side to surface the seeded `forecasts`/`risk_assessments` (forecast_gap, risk_count, burn_out_date, risk_class non-null) → Overview renders COMPLETE, no «есептелуде…»/dashes at demo
- [ ] **F4** group ledger by care type: group header row («МСАК / ПМСП», hairline) → source rows with ТМККК/МӘМС chips; full human line names (13px secondary service group); acronyms die in kk/ru, en keeps short
- [ ] **F5** progress bar: 6px track ink/10 = annual plan; solid fill = fact YTD; 1px vertical marker = YTD-expected; dotted extension to year-end if forecast exists
- [ ] **F6** demo defaults kk (verify first-load kk + fmtPct comma-decimal everywhere incl. KPI hero); ENG one click away
- [ ] **F7** ticker rotates real seeded alerts (burn-out, возражение ≤2 дн, 260 недовыставлено), not org+trivia
- [ ] AC: golden tests 8/8; timing; QA beats 1–5 per REGENERATED checklist; screenshot per beat; timer visibly at «осталось 2 раб. дня»; **one full-page kk Overview that survives an economist's squint (F1/F2/F4/F5/F6 visibly done)**

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

## Deferred to post-demo (from the old P-queue, if time never allows)

P6 full forecast engine (manifest-precomputed forecasts cover the demo) · P8 live RAG/eval ≥22/24 · P9 city panel full + alerts engine · PD3 full 12-role matrix · adapter round-trip demo.

## Icebox

(New ideas land here as one-liners. Zero discussion until golden path is done.)

## Interrupt-the-lead queue (batched)

1. Exact pitch slot/format when known → recompute cuts if <18h (drop order: city panel, live copilot, kk-полировка; never beats 2/4/6-canned).
2. ~~RAPIDAPI_KEY into local `.env`~~ — done (key stored locally, untracked; verified `git check-ignore`).
3. Review gates: Epic A look approval; Epic D kk native review + freeze GO.
