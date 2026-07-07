# 03 — PERSONAS, AS-IS, EPICS & USER STORIES

Format per story: **ID. Title** — `priority (MoSCoW) | size (S/M/L) | demo-critical? | suggested owner`
Owners: **BE** = backend dev (folrwix), **FE** = frontend dev (rasssppberrry), **LEAD** = Kassymzhomart (+Claude everywhere).
AC = acceptance criteria. Stories map 1:1 to GitHub issues (§12).

---

## 1. Personas

| Persona | Role | Pain today | Success for them |
|---|---|---|---|
| **Айгерім, 38** | Экономист поликлиники №14 | Contract + amendments in Excel; monthly план/факт by hand over ~30 contract lines; misses корректировка windows; panics before year-end | Opens one screen, sees risks ranked by ₸, files заявка from a generated draft in 10 min |
| **Дана, 29** | Статистик / мед. информатика | Forms счёт-реестр from MIS exports; ФЛК rejections; re-submissions; blamed for снятия | Pre-billing check turns her from "guilty party" into the person who saves millions |
| **Бақыт, 55** | Зам. главврача по леч. работе | Learns about under-execution post-mortem at quarterly review | Early warnings with concrete capacity actions (add МРТ shift, push screenings) |
| **Ерлан, 60** | Главврач | Signs everything; reports upward in KZ/RU; fears приписки scandals | Monthly management report auto-drafted in Kazakh; sleeps at night — firewall on |
| **Марат, 45** | Curator at управление здравоохранения / ФСМС | 14 clinics, 14 Excel formats, zero comparability | One standardized risk panel across clinics (our scale story; secondary persona) |
| **Сәуле, 33** | Участковый врач | Gets fined for coding errors she didn't know about | Sees her own claims flagged gently BEFORE submission — protection, not surveillance |

## 2. As-is workflow (what we replace)

```
МИС (Damumed) ──export──► Excel #1 (факт услуг)     Fund portal ──export──► Excel #2 (принято/снято)
Договор+доп.соглашения (PDF/XLSX) ──ручной ввод──► Excel #3 (план)
        Айгерім: 3–4 дня/мес VLOOKUP-ада ──► план/факт отчёт ──► Ерлан ──► управление
Дефекты обнаруживаются ПОСЛЕ снятия с оплаты. Корректировка — когда вспомнили. Прогнозов нет.
```

To-be: one ingestion layer → one truth DB → dashboard + forecast + firewall + copilot. (Architecture: 05.)

## 3. Epic A — Contracts & plans

**A1. Import contract line items** — `MUST | M | demo:yes | BE`
As Айгерім, I want to import the annual contract annex (XLSX/CSV) with lines (вид помощи × источник × месяц × объём × сумма) so the system knows the plan.
AC: Given a template XLSX, when uploaded, then lines are parsed, validated (sum checks, 12 months), errors reported per row, and plan visible in dashboard within 30s. Manual add/edit form exists as fallback.

**A2. Amendments (доп. соглашения) with versioning** — `MUST | M | demo:yes | BE`
As Айгерім, I want to load amendments so план always reflects the current redaction, with history.
AC: Given an amendment changing 3 lines, when applied, then new plan values take effect from its effective date; a diff view shows old→new per line; all analytics use the version active at the queried date.

**A3. Contract registry** — `SHOULD | S | demo:no | BE`
Multiple contracts (years, sources, orgs) listed with status and totals; switcher in UI.

**A4. 2026 package mapping reference** — `SHOULD | M | demo:yes | LEAD`
As the system, I need the ГОБМП↔ОСМС service/diagnosis mapping (incl. the 25 diseases moved in 2026) as editable reference data, so source-attribution rules (R17) work.
AC: mapping table seeded; effective-dated (pre/post 01.01.2026); editable in admin.

## 4. Epic B — Ingestion & reconciliation (автосверка)

**B1. Import MIS services/cases export** — `MUST | L | demo:yes | BE`
As Дана, I want to upload the MIS export of rendered services (CSV/XLSX) so факт enters the system.
AC: Column-mapping wizard with saved presets; ≥50k rows parse <60s; invalid rows quarantined with reasons, not dropped silently; идемпотентность (re-upload same file → no duplicates).

**B2. Import Fund statements (принято/снято/оплачено + дефекты)** — `MUST | M | demo:yes | BE`
AC: Given portal export, when loaded, then each claim's status updated (submitted→accepted/rejected/paid), defect codes attached; totals reconcile to file control sums.

**B3. Three-way reconciliation** — `MUST | L | demo:yes | BE`
As Айгерім, I want automatic сверка МИС ↔ выставлено ↔ принято/оплачено so discrepancies surface themselves.
AC: Report with 4 buckets: (1) rendered-not-billed (недовыставление, with ₸), (2) billed-not-in-MIS (red flag), (3) accepted-not-paid aging, (4) amount mismatches. Each row drills to claim. Bucket totals shown in ₸. **This is a demo beat: "система нашла 4.2 млн ₸ невыставленных услуг".**

**B4. Attached population import (РПН)** — `SHOULD | S | demo:no | BE`
Monthly прикреплённое население counts (by sex-age group if available) for подушевой analytics and R06.

**B5. Insurance status snapshot** — `SHOULD | S | demo:no | BE`
Patient insured-status flags (anonymized) to power R16/R17 source rules.

## 5. Epic C — Monitoring dashboard (SEE)

**C1. Contract execution overview** — `MUST | M | demo:yes | FE`
As Ерлан, I want one screen: % освоения YTD/MTD per line, plan vs fact vs forecast, traffic lights.
AC: Sorted by risk ₸ by default; filters (source, care type, month); loads <2s on seeded data; RU/KZ/EN switch affects every label (i18n keys from day one).

**C2. Line drill-down** — `MUST | M | demo:yes | FE`
Click a line → monthly bars (plan/fact/forecast band), cumulative curve, breakdown by отделение → врач → услуга.

**C3. Money waterfall** — `SHOULD | S | demo:yes | FE`
Выставлено → снято (по причинам ЕКД) → принято → оплачено, per month. One glance shows where ₸ leaks.

**C4. Освоение heatmap calendar** — `COULD | S | demo:no | FE`
Month×line heatmap; instant visual of seasonal under/over patterns.

**C5. Multi-clinic curator view** — `SHOULD | M | demo:yes(finale) | FE`
As Марат, I want all 14 clinics ranked by composite risk so I see the city at once. Seed 14 synthetic clinics; used as the pitch finale scale shot.

## 6. Epic D — Forecast & risk (FORESEE)

**D1. Line-level year-end forecast** — `MUST | L | demo:yes | LEAD`
As Айгерім, I want a year-end execution forecast per line with confidence band.
AC: Method per 06 §5 (run-rate × working days × seasonality; Holt-Winters when history ≥24m); each forecast stores method+inputs; UI shows the band and the **explanation sentence** ("тек. темп 92 случая/мес × 5 мес + сезонность ноября 1.12 → 3 462 из плана 3 900").

**D2. Risk classification & register** — `MUST | M | demo:yes | LEAD`
AC: Classes: критическое недоосвоение (<−10% projected), риск недоосвоения (−10..−5%), в графике (±5%), риск перевыполнения (+5..+10%), критическое перевыполнение (>+10%) — thresholds configurable. Risk register lists lines with gap ₸, class, deadline to act, recommended action. Backtest MAPE displayed (trust!).

**D3. Burn-out date** — `MUST | S | demo:yes | LEAD`
For over-executing lines: projected date when annual volume is exhausted ("МРТ закончится 14 октября"). Show on card and drill-down.

**D4. What-if simulator** — `COULD | M | demo:maybe | LEAD`
Sliders: +1 МРТ смена, +10% скрининг-кампания → recompute forecast. Strong jury moment if time allows.

**D5. Корректировка opportunity calculator** — `SHOULD | M | demo:yes | LEAD`
As Айгерім, I want the ₸ recoverable if volumes are reallocated at the next корректировка (over-exec lines ↑, under-exec ↓) so my заявка is argued with numbers.
AC: Given forecasts, produces a proposed reallocation table (respecting same-source constraint) + total ₸ protected.

## 7. Epic E — Defect firewall & anti-приписки (GUARD)

**E1. Rules engine core** — `MUST | L | demo:yes | BE`
As the system, I run a catalog of declarative rules (YAML: id, severity, scope, logic, message KZ/RU) against claims pre-submission.
AC: Runs on 50k claims <30s;每 finding: rule id, claim, ₸ at risk, human-readable bilingual message; results persisted per run; rule on/off toggles.

**E2. Seed rule catalog (25+ rules)** — `MUST | L | demo:yes | LEAD+BE`
Catalog per 06 §7, including the December-2025 audit signatures: services to deceased (R01), sex-mismatch (R02), age-mismatch (R03), child drug приписки (R19). **Demo line: "мы ловим именно то, что нашёл аудит Минфина — до отправки счёта".**

**E3. Pre-billing check screen** — `MUST | M | demo:yes | FE`
As Дана, before forming счёт-реестр I run the check and see findings grouped by rule/severity with ₸; export exceptions list (XLSX) for fixing in MIS.
AC: One button "Проверить реестр"; verdict header ("Реестр: 12 480 позиций, риск-позиции: 143 на 8.4 млн ₸"); drill to claim.

**E4. Anomaly detection (statistical)** — `SHOULD | M | demo:yes | LEAD`
Per-doctor/day volumes, weekend/off-schedule services, template-identical service packages, end-of-month stuffing — z-scores + IsolationForest, explained in plain words ("Врач X: 84 приёма 30 июня при медиане 31").

**E5. Defect analytics** — `SHOULD | S | demo:no | FE`
Pareto by rule/отделение/врач; repeat-offender trend; "стоимость дефектов" per month.

**E6. Appeal helper (возражение)** — `COULD | S | demo:no | LEAD`
Draft dispute letter for a снятие with claim evidence attached.

## 8. Epic F — Alerts & actions (ACT)

**F1. Alert center + deadline calendar** — `MUST | M | demo:yes | BE+FE`
As Айгерім, I get alerts (in-app; Telegram if time) for: new critical risk, burn-out <45 days, корректировка window opening/closing, счёт deadline, снятия above threshold.
AC: Alert = severity, ₸, one-line action, link; calendar view of regulatory deadlines (dates configurable — verify onsite ⚠️).

**F2. Recommendation cards with ₸** — `MUST | M | demo:yes | LEAD`
Each risk → card: "Подать заявку на увеличение объёма МРТ до 15 сентября → защитить 12.4 млн ₸" with buttons [Сформировать заявку] [Отложить] [Не актуально].

**F3. Auto-drafted заявка/письмо (docx, RU/KZ)** — `MUST | M | demo:yes | LEAD`
As Айгерім, one click generates the корректировка заявка / официальное письмо with our numbers substituted, in Russian AND Kazakh, ready for signature.
AC: docx via template engine; number formatting per locale; placeholders never leak ({{}} guards); Ерлан-ready.

## 9. Epic G — Copilot & i18n (SPEAK)

**G1. Full UI i18n kk/ru/en** — `MUST | M | demo:yes | FE`
Kazakh default in demo. All strings via i18n keys; glossary (02 §10) is the terminology source of truth; no hardcoded labels. Number/date formats localized.

**G2. Data Q&A copilot (text-to-SQL, guardrailed)** — `MUST | L | demo:yes | LEAD`
As Ерлан, I ask in Kazakh: «Қараша айында қай бағыттар бойынша игерілмеу қаупі бар?» and get an answer with real numbers + mini-chart + "show calculation".
AC: NL→semantic-layer→SQL whitelist (07 §4); numbers ONLY from query results; if unanswerable → honest "не могу посчитать это из данных" + suggestion; answers in the question's language; p95 <8s.

**G3. Regulations Q&A with citations (RAG)** — `MUST | M | demo:yes | LEAD`
«Какие виды мониторинга предусмотрены правилами?» → answer + exact приказ/пункт citation, kk/ru.
AC: Corpus per 02 §9; every claim cites chunk source; "открыть пункт" shows the text; refuses beyond corpus.

**G4. Monthly management report generator** — `SHOULD | M | demo:yes | LEAD`
One click → docx/pdf: освоение summary, risks, defects, recommendations — in Kazakh (and RU) — the artifact Ерлан sends upward. Judges hold it in their hands: print one.

**G5. Copilot eval set green** — `SHOULD | S | demo:no | LEAD`
24 QA pairs (07 §6) pass before demo; failures triaged.

## 10. Epic H — Platform & demo infrastructure

**H1. RBAC stub** — `SHOULD | S | demo:no | BE` — roles (экономист/статистик/руководитель/куратор) gate menus; hardcoded users fine.
**H2. Rule editor UI** — `COULD | M | demo:maybe | FE` — no-code toggle/threshold editing; jury asks "а можно своё правило?" → yes, live.
**H3. Anonymization posture** — `MUST | S | demo:no | BE` — hashed patient IDs only, no ФИО/ИИН anywhere in DB/UI; document it (jury WILL ask; 09 §5 Q7).
**H4. Synthetic data generator + seed** — `MUST | L | demo:yes | LEAD` — per 06 §4, with 5 planted storylines; `make seed` idempotent.
**H5. Demo reset script** — `MUST | S | demo:yes | BE` — one command restores pristine demo state <60s.
**H6. Docker-compose one-command up** — `MUST | S | demo:yes | BE` — `docker compose up` → seeded, working app; also = pilot-readiness proof.

## 11. Story census & cut lines

39 stories total: MUST = 23 (the demo), SHOULD = 12 (win margin), COULD = 4 (only if ahead of schedule).
**Cut line 1 (behind at mid-hackathon):** drop C4, D4, E6, H2 silently.
**Cut line 2 (crisis):** drop C5, E4, E5, G4 — demo still coherent with SEE+GUARD+FORESEE+ACT+G2/G3.
**Never cut:** B3, D1–D3, E1–E3, F3, G1–G3 — they ARE the differentiation.

## 12. GitHub conventions (LEAD enforces)

- One issue per story, title = `[A1] Import contract line items`; labels: `epic:A..H`, `must/should/could`, `demo-critical`, `size:S/M/L`; milestones: `Phase 1..4` per 08-EXECUTION.
- Branch `feat/a1-contract-import`; PR template: what/screenshots/i18n-keys-added?/rules-touched?/how-tested. Review SLA 30 min by LEAD; small PRs (<400 lines diff).
- `main` always demoable. Feature freeze per 08 §6.
