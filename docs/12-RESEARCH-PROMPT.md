# 12 — RESEARCH PROMPT (for a parallel Claude Cowork session)

> Open a new Claude Cowork session, select the `alemai` project folder, and paste everything below the line. Run it in parallel with the coding agent — nothing in coding Phases P1–P7 blocks on this, but every file you deliver upgrades the product's realism.

---

You are the research agent for **IGERIM** — Task 07 (intelligent monitoring of ОСМС/ГОБМП contract execution), Health AI Hackathon Astana 2026. The organizers did **not** provide real clinic data, so our demo runs on synthetic data — your job is to make that synthetic world, our rules engine, and our pitch **factually indistinguishable from the real system**. Context if needed: read `docs/02-DOMAIN.md` (especially its ⚠️VERIFY marks — they are your question list) and `docs/06-DATA-ANALYTICS.md` §1/§4/§7.

## Output contract (strict)

- Everything goes into **`docs/research/`**. Machine-readable first: CSV for anything tabular, MD for notes. No prose essays — tables and extracts beat summaries.
- Every file header: sources (full URLs + access date) and a per-item confidence tag: **CONFIRMED** (read in an official/primary source), **LIKELY** (secondary source, consistent), **INFERRED** (your reconstruction — mark loudly).
- Never fabricate: if a thing is unfindable, write `UNKNOWN` and add it to the mentor-question list (see RESEARCH-INDEX).
- Maintain **`docs/research/RESEARCH-INDEX.md`** from the very first file: item status table (R1–R13: done/partial/blocked), one-line "impact on IGERIM" per file, and the growing **MENTOR-QUESTIONS** list (things only hackathon mentors/№14 staff can confirm).
- Timebox: max 25 min per R-item before you write a partial file with what you have and move on. Ship partials; iterate later.
- Work order: all P0 first, then P1, then P2. Commit/push after each item if git is set up; otherwise just save files.

## P0 — realism blockers (do first)

**R1 — ЕКД: Единый классификатор дефектов → `ekd_codes.csv` + `ekd_notes.md`**
The defect classifier lives in annexes to the Правила оплаты услуг (приказ МЗ РК № ҚР ДСМ-291/2020; adilet: https://adilet.zan.kz/rus/docs/V2000021831 — check for the current redaction and amendment orders like V2200031025). Extract the actual defect table: code, name_ru (name_kk from the kaz version if accessible), care-type applicability, sanction/consequence. If the full annex is too large, prioritize outpatient + приписка-related codes. Our 25 rules (docs/06 §7) must cite real ЕКД codes.

**R2 — Счёт-реестр structure → `schet_reestr_format.md` (+ `schet_reestr_columns.csv`)**
What fields does a real счёт-реестр / реестр пролеченных случаев contain? Primary lead: приказ об утверждении форм документов для закупа (adilet: https://adilet.zan.kz/rus/docs/V2100025166) + Fund instructions for поставщики (Fund site, see R13) + any МИС manuals. Deliver a column-level spec: field, type, example, required.

**R3 — Корректировка объёмов mechanics (2026) → `korrektirovka_rules.md`**
From the current redaction of Правила закупа (adilet: https://adilet.zan.kz/rus/docs/V2000021744): exact procedure of volume adjustment — who initiates, how a поставщик applies (заявка), periodicity/windows/deadlines, committee timelines, constraints (e.g., within funding source). Cite exact пункты. This drives our deadline calendar and the заявка generator — precision matters.

**R4 — Tariffs → `tarifikator_sample.csv` + `tariffs_notes.md`**
Current tariff sources: тарификатор for КДУ services, КЗГ list + base rate for stationary, подушевой норматив (КПН) 2026 value + половозрастные коэффициенты. Extract ~50 common outpatient services (МРТ/КТ/УЗИ variants, приёмы, лаборатория, ФГДС, рентген...) with real codes and prices → CSV (code, name_ru, price_₸, source, confidence). If exact 2026 numbers are unfindable, give the latest confirmed year and mark INFERRED-scaling.

**R5 — Единый пакет 2026 mapping → `package_mapping_2026.csv` + `reform_notes.md`**
Official annexes of/under Закон №206-VIII от 14.07.2025 and implementing приказы: the list of the 25 chronic diseases moved to ОСМС (with МКБ-10 ranges if published), what moved to ГОБМП (onco-screenings etc.), diagnostics-regardless-of-status rules. CSV: disease/service group, icd10_range, source_before_2026, source_after_2026, citation, confidence. Feeds rule R17 — the reform-awareness demo moment.

## P1 — adapters & copilot fuel

**R6 — МИС export shapes → `damumed_export_format.md`**
What do Damumed (dominant in Astana; confirm for Polyclinic №14 if possible) exports/reports look like: reestr exports, услуги/случаи reports — column names, formats (XLSX/CSV), what a statistician can actually pull. Sources: Damumed user manuals, help portals, training videos/screenshots, vacancy descriptions, forum posts. Secondary: ЭРСБ/АПП portal field structures. Everything here may be LIKELY/INFERRED — that's fine, mark it.

**R7 — Regulations corpus download → `regs/` + `regs/SOURCES.md`**
Download full texts (kk AND ru) of: (1) Правила закупа V2000021744, (2) Правила оплаты V2000021831, (3) Правила мониторинга V2000021904 + amendment V2500036470, (4) Закон №206-VIII, (5) Кодекс о здоровье (relevant chapters on ГОБМП/ОСМС), (6) any приказ defining ЕКД if separate. Adilet has Kazakh mirrors (`/kaz/docs/...`). Save as clean .txt (one file per doc per lang, e.g., `regs/pravila_zakupa.ru.txt`, `.kk.txt`). This becomes the copilot's RAG corpus verbatim — completeness > commentary.

**R8 — Monitoring rules deep-read → `monitoring_rules.md`**
Close read of V2000021904 (+2025 amendment): the four monitoring types (текущий/целевой/внеплановый/проактивный) — triggers, timelines, поставщик obligations and rights (возражения/appeal windows), how снятие is formalized. Bullet extracts with пункт citations. Feeds copilot eval Q13/Q14 and pitch Q&A.

## P2 — pitch ammo & calibration

**R9 — Hackathon intel → `hackathon_intel.md`** *(do this one even if time-crunched — 15 min)*
AI WEEK Astana 2026 / Astana Hub / Astana IT University / MedHub HAQ pages + socials: exact schedule (**DEMO time/date — if found, put it in ALL CAPS at the top of RESEARCH-INDEX**), pitch format/time limits, judging criteria, jury names/affiliations (search each: Fund? clinic? IT?), prize breakdown, other tracks/teams intel.

**R10 — Polyclinic №14 Astana → `clinic14_facts.md`**
Attached population size, departments/services, leadership names, any public digitalization news, which МИС they run. Sources: official site/socials, damumed.kz client lists, news. Calibrates datagen and lets the pitch name-drop accurately.

**R11 — Calibration stats → `calibration_stats.md`**
Public numbers to calibrate synthetic amounts and impact slide: typical annual contract sums for Astana polyclinics (Fund publishes поставщик/договор registries — check the Fund site's "поставщикам" sections and data portals), city totals for Astana 2025/2026, дефекты/приписки statistics by year, % снятий if ever published. Each number: source + year + confidence.

**R12 — Competitive scan → `competitors.md`**
Who claims to do contract/volume monitoring in KZ already: Damumed modules, other МИС vendors, BI integrators, the Fund's own поставщик-facing cabinet features. For each: what it actually does (evidence), what it lacks vs IGERIM's five pillars. Feeds pitch Q&A #9.

**R13 — The Fund's current identity → append to `RESEARCH-INDEX.md`** *(5 min, do early)*
After the Dec-2025 transfer to Минфин, confirm the Fund's current official name, branding, and website (msqory.kz appeared in 2025 sources — verify it's current). Getting the payer's name right on stage is table stakes; getting its post-reform status right is a flex.

## Method notes

- Primary sources first: adilet.zan.kz (rus + kaz), legalacts.egov.kz, the Fund's official site, gov.kz ministry pages. News (tengrinews, zakon.kz, kt.kz...) only for scale numbers and events, never for legal mechanics.
- Adilet pages are huge — extract the annex/section you need, don't dump whole laws into notes (except R7, where full text IS the deliverable).
- If a source is paywalled/blocked/unfetchable, record the URL + what it likely contains + mark blocked; don't burn the timebox on workarounds.
- Language: notes in English or Russian (your choice, be consistent); extracted legal/reference content stays in original kk/ru.

## Definition of done

`docs/research/RESEARCH-INDEX.md` shows R1–R13 all done/partial with impact notes; MENTOR-QUESTIONS list is ready to be asked at the venue; every CSV parses (no ragged rows); the coding agent can consume your files without asking you anything. When you finish P0, say so explicitly in your status so the lead can point the coding agent at the pack immediately.
