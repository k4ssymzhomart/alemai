# 17 — NEXT DIRECTIVE FOR THE CODING AGENT (post-research, post-review)

> Paste everything below the line into the coding agent. It supersedes packet definitions P3+ in docs/11 where they conflict; docs/11's laws (§1), reporting (§5), and don'ts (§7) remain in force.

---

Lead review verdict on P1–P2: spine accepted. Two systemic problems found and now fixed at spec level — you implement: (1) **navigation logic** — drill-downs land on raw number dumps; (2) **design** — default SaaS look is replaced by a strict B&W system. Additionally the research pack (docs/research/, commit bcbe5c0) landed with corrections that change datagen scale, rule sanctions, copilot answers, and pitch facts. Read, in order: `docs/16-RESEARCH-INTEGRATION.md` (corrections C1–C12), `docs/13-ROLES-PERMISSIONS.md`, `docs/14-USER-STORIES-V2.md` (§0 IA fix + status tags), `docs/15-DESIGN-SYSTEM.md`. Do not re-read the research pack wholesale — 16 §5 maps exactly which file feeds which packet.

## 0. Timeline fork (unresolved — build order hedges it)

The pitch slot is unknown: possibly **tomorrow (09.07)** at Astana AI Week, possibly a separate challenge **~23.07** (research/hackathon_intel.md §6). Until the lead confirms:
- Work the order below, which front-loads everything demo-visible.
- Keep `demo-stable` tag updated after every green packet — at any moment we must be ≤30 min from a presentable demo.
- The lead asks organizers TODAY; on his signal: `DEMO=tomorrow` → jump to §5 compression; `DEMO=23.07` → full order + second-pass polish list (§6).

## 1. Revised packet order

**PD1 — Design system «Ведомость» (do FIRST, before any new screens)**
Implement docs/15 §§1–3, 5–8, 11: tokens (ink/paper only — strip default Tailwind palette so violations are impossible), radius 0 global, fonts with the **KZ glyph gate screenshot**, ECharts `vedomost` theme with decals, restyle existing Overview/drill screens, Marquee alert ticker, StampMark/VerdictBlock/DeadlineBox/ExecutionBar/CodeChip components, Logo slot (`/public/brand/logo.svg` fallback wordmark), print stylesheet.
**AC:** golden beat 1 in new skin; `grep` gates from 15 §10 pass (no rounded, no stray hex colors); glyph-gate screenshot in PR; print of Overview looks like a document.

**PD2 — IA fix: Passport pattern (kills «цифровая каша»)**
Implement 14 §0 globally: Line Passport (5-block order: Кто я → Вердикт → Почему → Что делать → Данные-collapsed), breadcrumbs, no-naked-numbers rule («как посчитано» popover fed by metrics.yaml descriptions), designed empty states everywhere (dot pattern + 1 sentence + 1 action), «данные демо» footer badge.
**AC:** clicking any Overview row lands on a Passport that a non-expert can read aloud; zero pages render raw JSON-ish number grids; every KPI has label+unit+period+popover.

**P3′ — Datagen rescale + storylines (revised)**
(a) **Profile system**: `--profile gp14-real` (DEFAULT: 31,000 attached, 20 участков, ~1.2 bn ₸/yr, КПН base 1,700 ₸/чел/мес, real №14 department mix per research/clinic14_facts.md §4) and `--profile city-composite` (для city panel: 14 clinics of varied scale 31k–120k).
(b) **`datagen/storylines.yaml` = single source of truth** for every planted number; `assert_storylines.py`, `docs/QA-CHECKLIST.md` (regenerate it from the manifest — script, not hand-edit) and the pitch numbers all derive from it. Rescale the 7 storylines to gp14-real (keep burn-out at 14.10.2026 — rate-shaped, scale-free; recompute ₸ values); add storyline 8: **возражение window** — 4 потенциальных дефекта из «ИСФ-выгрузки» с дедлайнами через 1/3/4/5 раб. дней (feeds DF-timers demo moment).
(c) Datagen export columns aligned to research/schet_reestr_columns.csv + damumed_export_format.md (mark INFERRED columns in the adapter preset).
**AC:** `make seed` (gp14-real) → assert_storylines PASS; QA-CHECKLIST regenerated and committed; overview shows believable ~61% mid-year execution at the new scale.

**PD3 — Roles & settings skeleton**
Role switcher (13 §2: 12 login roles), permission matrix enforced in nav + API scopes (dept/peds/self scoping per 13 §3), Settings tree (13 §4) — sections functional where backend exists (пороги, правила toggles, брендинг upload, язык, о системе with **справочник versions in footer: «ЕКД ред. №19 от 27.02.2026»**), read-only stubs elsewhere (no dead ends — stub explains what will live there).
**AC:** switching role visibly transforms nav+data scope; врач sees only own cases; куратор sees only aggregates; settings saves thresholds and they affect risk classes.

**P4′ — Rules engine (upgraded)**
As P4 in docs/11 PLUS: sanction column from research (`ekd_code`, `sanction_app`, `sanction_kdu` — ekd_notes.md §4 mapping; messages cite real codes: «код 5.1 — снятие 300%»); **ЕКД versioning by claim date** (ред. №68 until ~14.03.2026, ред. №19 after; код 1.3 archived); «жёлтые» severity for 2.0/7.0 (0 ₸, фиксируется); R24 reclassified indicator-not-defect; R17 uses package_mapping_2026.csv (перечни-precedence: СЗЗ→ГОБМП, иначе ЗПДН→ОСМС).
**AC:** golden tests 8/8 (incl. new storyline); each finding renders CodeChip + real sanction ₸ math; rule run on claim dated 2025-11 applies ред. №68, dated 2026-04 → ред. №19.

**P5′ — Reconciliation + pre-billing + возражения (upgraded)**
As P5 PLUS the DF-track (14 §3): лента потенциальных дефектов со статусами трека (выявлен→возражение→повторное→центр. аппарат), **DeadlineBox timers: 5 раб. дней возражение / 3 повторное / 3 подписание — working-day aware, «молчание = автоснятие (п. 27)» warning**, конструктор возражения (docx kk/ru via P7 engine), ST-5 ЕПС-таймер (≤3 раб. дней), ST-6 yellow defects section, VR-scope «мои случаи».
**AC:** beats 4–5 pass with manifest numbers; возражение timer beat rehearsable (a timer visibly at «осталось 2 раб. дня» in seed).

**P6 — Forecast & risk** — unchanged from docs/11, plus DF-5 МРП-threshold progress bars (200/800 МРП, МРП 2026 value in config) on director panel.

**P7′ — Recommendations + documents (corrected)**
Docgen templates replaced: **«Обращение в Фонд о размещении дополнительных объёмов (пп. 25)/26) п. 19 Правил закупа)»** with авто-расчёт остатка средств по виду помощи (EC-8/EC-9), возражение template (DF-3), monthly report (kk/ru). Remove any «заявка на корректировку» wording — the real mechanism is размещение по п. 19.
**AC:** beat 3 generates the обращение with the п. 19 citation and correct math from live data.

**P8 — Copilot** — as docs/11 P8 (RapidAPI pipeline) PLUS: corpus = research/regs/ (11 files, includes full ЕКД); eval set updated per C10 (Q13 two-type answer, 13-bis currency check); role-aware answers (CP-3); templates for DF-timer Q&A (CP-4). Answer templates kk/ru go into the lead's native-review batch.

**P9 — Scale & alerts** — as docs/11 PLUS deadlines seed from korrektirovka_rules.md §6 (real dated events: кампания прикрепления до 10.11, окно-запрет 01.11–01.02, 15/10/3 раб. дня; ежеквартальная сверка flagged LIKELY⚠️ in UI tooltip), city panel on city-composite profile with normalized metrics (снятия/1000 прикреплённых).

**P10 — Freeze & stagecraft** — as docs/11 PLUS: pitch asset pack refresh from 16 §3 (Qalqan answer card, 38 млрд stat, 3.4 трлн budget, «п. 24/п. 15» argument cards); print one Line Passport + one kk monthly report for the jury.

## 2. ADD-stories routing

Fold per tags in docs/14 (each ≤0.5 day; cut first under pressure EXCEPT bolded five: EC-8, EC-9, DF-2, ST-6, DT-2). ROADMAP items: never build — they exist for Q&A.

## 3. Facts hygiene (unchanged laws, new specifics)

Never render: «4 вида мониторинга», «заявка на корректировку», «2.7 трлн» (use 3.4 per chair), old ФСМС transfer date. The UI footer shows справочник versions. All LIKELY/INFERRED research data carries `source:` provenance and, where user-visible, a ⚠️ tooltip («уточняется у Фонда»).

## 4. Interrupts to the lead (updated)

(1) DEMO date from organizers → replan per §0. (2) RAPIDAPI_KEY at P8. (3) Native review: one batch after P7′ (обращение/возражение kk texts + copilot templates), one after P9. (4) Mentor-question answers (research RESEARCH-INDEX list) — integrate as they arrive; корректировка windows and ЕКД-2021 are the two that change product behavior.

## 5. If DEMO=tomorrow (compression)

Ship order: PD1 (skin) → P3′a+b (rescale+manifest; skip adapter column alignment) → P4′ with 10 rules (R01–R04, R07, R10, R16, R17, R20 + storyline coverage) → P5′ pre-billing + DF-timers (skip конструктор возражения docx — show timer + template preview) → PD2 on the 3 demo screens only → P7′ обращение docx (ru first, kk if time) → canned copilot (6 questions) → P10 mini (reset, video, print). Cut: PD3 beyond role switcher, P6 full engine (use manifest-precomputed forecasts — they're planted anyway), P9 city (use static seed), eval run.

## 6. If DEMO=23.07 (second pass after full order)

Polish list: E2E golden tests in CI, live forecast engine backtested, rule editor UI (H2), copilot live-mode eval ≥22/24, real Damumed XLSX round-trip demo, «режим прозрачности» mock (KU-4) as roadmap slide screenshot, rehearsals ×3.

Start with PD1 now. Status report format unchanged (docs/11 §5); include the two grep-gates and glyph-gate screenshot in the PD1 report.
