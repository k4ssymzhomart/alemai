# QALAM 1.0 — Coder Results

Session summary and handoff. Product: **QALAM** (Қалам · ранее Igerim) — clinic-side
intelligent monitoring of ГОБМП/ОСМС contract execution. Task 07, Health AI Hackathon,
Astana AI Week 2026. Repo: `github.com/k4ssymzhomart/alemai`.

Generated 2026-07-09 at the Epic D HARD STOP.

---

## 1. What QALAM is

A clinic's control loop over its Fund contract: it watches план/факт execution, forecasts
where money will be lost (under-execution) or burned early (over-execution), runs a
pre-billing rules check against the real ЕКД (Единый классификатор дефектов), reconciles
МИС ↔ счёт ↔ оплата, tracks the 5-working-day объection windows, and generates the actual
documents (обращение в Фонд, возражение). A guardrailed copilot answers in kk/ru where
**every number comes from the data layer, never from the language model**.

Positioning vs the Fund's **Qalqan** (antifraud, post-submission): Qalqan is the payer's
shield; QALAM is the clinic's self-check **before** the invoice — the only defence, because
after a defect is assigned, п. 24 forbids МИС corrections.

---

## 2. Session arc — five epics, all built

| Epic | What shipped | PR | State |
|---|---|---|---|
| **A** — Absorb + reskin | docs 13–18 landed; first B&W «Ведомость» skin | #56 | merged |
| **A.2** — Redesign + rename | de-brutalized to a premium annual-report look; **Igerim → QALAM** | #57 | merged |
| **B** — Data truth | datagen `gp14-real` rescale, storylines manifest, F2/F3 | #58 | merged |
| **C** — GUARD (the teeth) | rules engine + pre-billing + reconcile + возражения + Passport + F1–F7 | #59 | merged |
| **D** — ACT + SPEAK | docgen (обращение/возражение docx) + copilot + roles/settings | #60 | **open, CI green, HARD STOP** |

`main` is demo-stable through **beat 5**; Epic D (beats 3+6) waits on the lead's kk
native-review + freeze GO before merge.

---

## 3. Design system (final)

Lead's gate verdict rejected the first «терминал/ведомость» skin as too heavy and rejected
Literata; the final system is **«премиальный годовой отчёт частного банка, в один цвет»**:

- **Colour:** strictly `#000` / `#fff` only — the Tailwind palette is *replaced* (not
  extended), so a colour violation is a class that does not exist. Optical greys = black at
  fixed opacities. `border-radius: 0` everywhere.
- **Type:** **Manrope** (display, sentence-case) / **Inter** (UI) / **IBM Plex Mono** (all
  numbers, ₸, dates, codes). KZ glyph gate passes for `Ә Ғ Қ Ң Ө Ұ Ү Һ І` + ₸ at every
  weight. The only uppercase is the 11px letterspaced micro-label.
- **Weight diet:** hairline 1px `ink/15` rules, no offset shadows, **one black element per
  screen** (the verdict block or a ≤2-day timer), outline chips, faint-wash hover.
- **Charts:** ECharts monochrome, decal patterns (not hue), hairline gridlines, calm fade.
- Print stylesheet (A4, chrome hidden, keeps the demo-data badge); `/design` internal QA page.
- Brand slot: wordmark `Qalam`, favicon `Q`, `/public/brand/logo.svg` drop-in ready.

---

## 4. Data — `gp14-real` profile (Epic B)

Modelled on the real ГП №14: **31 000 attached, ~1.2 bn ₸/yr, КПН ≈ 1 710 ₸/чел/мес**,
13 contract lines. `datagen/storylines.yaml` is the single source of every planted number;
`assert_storylines.py` (28 checks) and `assert_seed_integrity.py` (86 checks) verify them
after seed. Overview reads a plausible **60.8 % mid-year** (ПМСП capitation ~37 %, FFS lines
87–94 %, МРТ 108–109 %). Plan amounts round cleanly (F3); forecasts/risk precomputed (F2).

### Canonical planted numbers (feed the pitch)

| # | Storyline | Value | Beat / ЕКД |
|---|---|---|---|
| 1 | МРТ over-execution | 118 % run-rate от 03.2026 → burn-out **14.10.2026**, возместимо ~5.67 млн ₸ | beat 2/3 · пп.25/26 п.19 |
| 2 | Стоматология | 71 % run-rate → недоосвоение **17.4 млн ₸** | beat 1 · critical_under |
| 3 | «Творческий» врач | **80** визитов/день, **30** в выходные | beat 1 · R10/R11 |
| 4 | Услуги после смерти | **2** пациента / **3** услуги | beat 4 · R01 (ЕКД 5.1) |
| 5 | Пол/возраст (11.2025) | 31 маммография муж. + 12 скринингов = **46 позиций / 168 600 ₸** | beat 4 · R02/R03 |
| 6 | Недовыставление | **260** случаев / **2 992 000 ₸** | beat 5 · сверка bucket 1 |
| 7 | Реформа 2026 | **180** диабет-случаев E11 на ГОБМП / 612 000 ₸ | beat 4 · R17 (ЗПДН) |
| 8 | Окно возражения | 4 дефекта, дедлайны **1/3/4/5 раб. дней** (10/14/15/16.07), 67 300 ₸ | DF-timers · пп.26–27 |

Overview aggregates: forecast gap **70 061 600 ₸**, risk count **4**.

---

## 5. Rules engine (Epic C)

13-rule ЕКД catalog (`backend/rules/catalog.yaml`) with **real ЕКД codes + sanction math +
edition-by-claim-date** (ред. №68 до ~14.03.2026 / ред. №19 после). Golden tests **8/8**
(10 pytest); 50k-claim run = **110 ms**. Pre-billing on the Nov-2025 registry reproduces
the exact **46 позиций / 168 600 ₸** verdict. «Жёлтые» severity for ЕКД 2.0/7.0 (0 ₸,
fix-without-снятие). Sanctions cite the real penalty (код 5.1 → 300 % / 100 КПН).

---

## 6. Screens & beats (golden path)

| Beat | Screen | Status |
|---|---|---|
| 1 | Overview — grouped ledger, F1 YTD-%+annual, F5 bar, F2 tiles, F7 ticker | ✅ live |
| 2 | Line Passport (PD2: Кто я → Вердикт → Почему → Что делать → Данные) | ✅ live |
| 3 | Risk → обращение docx (пп.25/26 п.19 + авто-расчёт) | ✅ Epic D |
| 4 | Pre-billing («БЛОКЕРЫ 46 / 168 600 ₸» + findings + StampMark) + возражения timers | ✅ live |
| 5 | Reconcile (4 buckets, 260/2.99M, drill-down) | ✅ live |
| 6 | Copilot (6 Q&A, real numbers, citations, refusal, network-off) | ✅ Epic D |
| 7 | City panel (14 clinics) | ⏳ P9 — optional / designated skip |

The Overview findings F1–F7 (execution semantics, no-dead-tiles, group-by-care-type,
6px bar, kk defaults, real ticker alerts) are all done — it survives an economist's squint.

---

## 7. Copilot & docgen (Epic D)

- **Copilot** is a deterministic keyword pipeline: intent router → data/regulation/report/refuse,
  every figure pulled from metrics/objections/reconcile, a number-validator, kk/ru/en
  templates. **No live LLM call in the default path** → works with the network OFF (the
  mandatory canned mode) and the "numbers never pass through the model" claim is literally
  true. Verified: Q1 «4 тәуекел» (matches dashboard), Q13 «екі түрі» + cite п.4 приказ №68,
  Q13-bis проактивный отменён, objection «1 раб. день», reconcile «260 / 2 992 000 ₸», Q21
  refuses. Receipt-style dock UI with citation chips. Live RapidAPI path documented, not required.
- **Docgen** (`/documents/*`, python-docx): обращение / возражение / monthly report as real
  .docx with numbers from the DB, приказ №99 citation, signature block, no `{{}}` leaks,
  ru+kk. Wired to the Passport «Құжат жасау» and objection «Қарсылық құрастыру» buttons.
- **Roles/settings (PD3-lite):** role switch drives nav + scope (Куратор → 3-item nav,
  «Астана · 14 ГП»); Settings «О системе» shows справочник versions («ЕКД ред. №19 ·
  27.02.2026») as the trust signal, plus functional пороги.

---

## 8. Stack & infrastructure

- **Backend:** FastAPI, 21 tables, Alembic, `mv_line_execution` MV, gp14 seed (~500k claims,
  ~16 s), pgvector. Ports remapped: db `55432`, api `8800` (5432/8000 belong to another
  local project — never touched).
- **Frontend:** Next.js 14, kk-default i18n (169 keys × 3 locales), ECharts, no react-query.
- **CI:** backend (ruff + full seed + integrity + pytest incl. rules_golden), data-gates
  (validators), frontend (build). All green on every merged epic.
- **LLM:** no Anthropic key; copilot canned-first, optional RapidAPI GPT-4o-mini for the
  live parse step only.

---

## 9. Decisions made alone (worth a sanity-check)

- **ПМСП capitation modelled at ~37 %** execution — the honest lever that makes both
  "baseline lines 85–105 %" and "overview ≈ 61 %" true; capitation is paid in full regardless.
- **Copilot fully deterministic** (no live LLM by default) — safest for flaky venue wifi.
- **МРТ recoverable = ~5.67 млн ₸** (gp14 scale) recomputed from the over-plan spend, not the
  old 12.4 млн; burn-out 14.10.2026 kept as a labelled forecast constant.
- **Two subagents dropped mid-run** (one spurious, one on the internet blip); the coordinator
  finished the docgen route + wrote the entire copilot pipeline itself and re-verified.
- Two CI fixes were environmental, not code defects: a stale validator missing the `yellow`
  severity, and CI seeding `--sample` (49 blocks) vs the full-profile golden count (46) → CI
  now seeds full.
- обращение letter **date shows the as-of month (June)** not today — minor cosmetic, flagged.

---

## 10. Open items / next

1. **Epic D HARD STOP (now):** lead reviews the kk native-review batch
   (`docs/NATIVE-REVIEW-QUEUE.md` — demo-critical rows are the copilot canned answers +
   `cp.note`) and gives the **freeze GO**. On GO → merge #60, tag `demo-stable` at Epic D.
2. **Epic E — freeze & stagecraft:** `make demo-reset` <60 s, two full QA runs (one on
   battery + hotspot), fallback screen-recording, print pack (Line Passport A4 + kk monthly
   report), pitch asset cards from 16 §3 (Qalqan answer, «38 млрд ₸ оспорено», «п.24/п.15»,
   3.4 трлн), update docs/09 numbers from the manifest.
3. **Beat 7 (city panel):** optional — fold into Epic E or leave as the designated skip.
4. **Secret hygiene:** `RAPIDAPI_KEY` lives only in untracked `.env`; `git grep` confirmed no
   key value in tracked files.

---

## 11. Facts hygiene (never say on stage)

Never render «4 вида мониторинга» (it's **2**: текущий + внеплановый), «заявка на
корректировку» (real mechanism = размещение по **п. 19**), «2,7 трлн» (use **3,4 трлн** per
the chair). ЕКД = Приложение 1 к Правилам мониторинга. Возражение = 5 раб. дней; молчание =
автоснятие (п. 27). Fund = НАО «ФСМС», под управлением Минфина с 16.01.2026, председатель
Гульмира Сабденбек. All demo data carries the «демо-деректер» badge.
