# 01 — WINNING STRATEGY

**Product:** IGERIM (Игерім / Igerim) — Intelligent GOBMP/OSMS Execution & Risk Intelligence Monitor
**Task:** №07 — Intelligent monitoring of OSMS/GOBMP contract execution (Track 2: Finance & Management with AI)
**Event:** Health AI Hackathon, AI WEEK Astana 2026. Flagship stakeholder: City Polyclinic №14, Astana.
**Status:** HACKATHON IS LIVE. This doc pack is the playbook.

---

## 1. Retro: why we lost last time, and the correction

Last time we optimized for the baseline — "make the basic functionality work." Baseline gets you a passing grade, not a win. Every team in the room will ship a dashboard with план/факт charts. The jury will see eight of them in a row.

**Corrections this time:**

1. **Bet on differentiation from hour one, not hour twenty.** The Kazakh-language AI copilot, the forecast engine, and the anti-приписки firewall are built IN PARALLEL with the core, not after it. See 08-EXECUTION for the parallel tracks.
2. **Domain depth as a weapon.** We speak the jury's language: счёт-реестр, ЕКД, корректировка объёмов, проактивный мониторинг, Закон №206-VIII. A team that says "приказ ҚР ДСМ-321/2020" out loud beats a team that says "we monitor contracts."
3. **Money in every sentence.** Every feature is expressed in тенге saved or recovered. Juries at finance-track tasks are economists.
4. **A demo that tells a story, not a tour of screens.** One narrative, three risks caught, ₸ counted. See 09-PITCH-DEMO.

## 2. The "why now" — three tailwinds nobody should waste

These are real, current, verifiable events. They are the emotional and political core of our pitch:

1. **The ФСМС scandal → Minfin era.** Government IT-audit found systemic fraud in billing: **3,640 services billed to 996 deceased patients**, **769,446 screenings not matching the patient's sex (~1.8 bn ₸)**, **68,717 cases of drug приписки on children**. Dec-2025: PM Bektenov orders the audit response; **16.01.2026: the Fund is formally moved under Ministry of Finance management** (chair Гульмира Сабденбек since 23.01.2026); **16.03.2026: the Fund pilots its own antifraud platform Qalqan**. The Fund contested **38 bn ₸** of billed services in 2025 alone. Payment discipline in 2026 is the strictest in the system's history — and per п. 24 of the monitoring rules, data can't be fixed after a defect is assigned. Clinics that can't self-audit before billing will bleed money. (Our Qalqan positioning: 16-RESEARCH-INTEGRATION C9.)
2. **January 2026: Единый пакет reform (Law №206-VIII of 14.07.2025).** Services redistributed between ГОБМП and ОСМС: 25 chronic diseases (incl. diabetes — 414k patients, ДЦП — 26k, rheumatism — 13k) moved to the OSMS package; onco-screenings moved to ГОБМП for everyone; ~1M new insured expected. **Every clinic's contract structure and billing-source logic changed on 01.01.2026.** Every internal Excel built before 2026 is obsolete. This is a greenfield moment for monitoring tools — and a killer argument for our configurable rules engine.
3. **Scale of money.** ФСМС buys **2.7 trillion ₸** of services in 2026 (1.36T OSMS + 1.3T ГОБМП). Even 0.5% efficiency gain = 13.5 bn ₸/year nationally. Astana's 14 state clinics are the beachhead.

**Pitch hook (draft, RU):** «В декабре 2025 года премьер-министр передал ФСМС под контроль Минфина. Аудит нашёл услуги, оказанные умершим, и 769 тысяч скринингов не того пола. Государство ужесточает контроль. Мы даём клинике инструмент, который решает проблему у источника — до выставления счёта, а не после штрафа.»

## 3. Win thesis

> **Everyone will monitor the past. We manage the future and speak the state language.**

Five pillars (memorize; each maps to a demo beat):

| # | Pillar | One-liner | What competitors will have |
|---|--------|-----------|---------------------------|
| 1 | **SEE** | Live план/факт по каждой строке договора, drill-down до врача | Yes — everyone. Table stakes. |
| 2 | **GUARD** | Pre-billing defect firewall + автосверка МИС↔портал ФСМС. Catches exactly what the Minfin audit found — before submission | Few, shallow |
| 3 | **FORESEE** | Forecast year-end execution per contract line, risk score, "дата выгорания объёма" | Almost nobody, and not explainable |
| 4 | **ACT** | Recommendations with ₸ attached + auto-drafted заявка на корректировку (docx, RU/KZ) with deadline calendar | Nobody |
| 5 | **SPEAK** | Kazakh-first AI copilot: NL questions over the data + Q&A over приказы with citations; official reports in Kazakh | Nobody does Kazakh well. Our signature move |

**The line that wins Q&A:** "ФСМС мониторит для себя и постфактум. Поликлиника остаётся слепой до момента снятия с оплаты. Igerim — это контур мониторинга НА СТОРОНЕ КЛИНИКИ, работающий до счёта, а не после штрафа. А для управления здравоохранения — единая панель по всем 14 клиникам."

## 4. Predicted competitor landscape (and our counters)

| Archetype | What they'll show | Our counter |
|-----------|-------------------|-------------|
| Dashboard team | Superset/PowerBI-style план/факт | Forecast + ₸ recommendations + burn-out dates; theirs answers "what happened", ours "what to do" |
| Chatbot team | GPT wrapper answering health questions | Our copilot is guardrailed: numbers only from SQL, citations from приказы, Kazakh terminology enforced. Ask their bot "сколько снято с оплаты в ноябре" — it will hallucinate |
| ML team | A model predicting something with 0 explainability | Explainable stats + backtest MAPE shown in UI; jury of economists trusts what it can verify |
| Doc-flow team | Document generator for reports | We generate the same docs, but from live verified data, as one of five pillars |

**Moats within 48h:** domain-encoded rules catalog (25+ rules from ЕКД logic + Dec-2025 audit findings), reform-aware 2026 package mapping, Kazakh terminology glossary + eval set, synthetic dataset with planted storylines that makes the demo cinematic.

## 5. Judging model (assumed weights) and how we score

| Criterion (typical) | Weight | Our scoring move |
|---|---|---|
| Relevance / problem fit | 25% | Task-07 language mirrored exactly: "недоосвоение/перевыполнение", "автосверка"; №14 as named user; 2026 reform awareness |
| Working prototype | 25% | Golden demo path rehearsed; seeded data; reset script; offline fallback video |
| Innovation / AI depth | 20% | FORESEE + guardrailed copilot + anomaly detection; not a GPT wrapper |
| Impact / economics | 20% | ₸ math per clinic and city-wide (see §6); ties to hackathon's stated goals (50–70% faster processing, 20% staff time freed) |
| Team / pitch | 10% | Kazakh opener, story demo, hard-Q&A prepared (09-PITCH-DEMO §5) |

## 6. Impact math (headline numbers, honestly labeled as modeled)

Assumptions for a large Astana polyclinic (≈130k прикреплённое население, annual contract ≈ 4–6 bn ₸ across ПМСП/КДУ/дневной стационар/стоматология). All % are parameters to calibrate on MedHub data — say so on stage; it builds trust.

| Loss channel | Modeled size | Igerim effect | Recovered/yr |
|---|---|---|---|
| Снятия с оплаты (дефекты, ЕКД) | 1.5–3% of billed | Firewall catches ~60% pre-submission | 45–90 mln ₸ |
| Недовыставление (rendered in МИС, never billed) | 0.5–1% | Автосверка finds 90%+ | 25–50 mln ₸ |
| Missed корректировка (over-execution unpaid / неосвоение clawed back) | 1–2% | Forecast + deadline alerts + auto-заявка | 40–80 mln ₸ |
| Staff time (economist+statistician manual reconciliation) | 3–4 days/mo | → hours | ≈1 FTE, 20%+ time freed |

**Per clinic: ~110–220 mln ₸/yr (≈2–4% of contract). × 14 Astana clinics: ~1.5–3 bn ₸/yr. National ceiling at 0.5% of 2.7T: 13.5 bn ₸/yr.** Anchor slide: "Igerim окупается за первую неделю работы."

## 7. Naming & brand

**IGERIM (Игерім)** — from игеру, "to master/utilize"; **игерім = освоение** — literally the metric the whole task is about (% игерілуі / % освоения). Backronym: **I**ntelligent **G**OBMP-OSMS **E**xecution & **R**isk **I**ntelligence **M**onitor.
Taglines — KZ: «Igerim — қаражат жоғалғанға дейін көреді.» RU: «Igerim — видит риск до того, как он стал потерей.»
Alternates if team vetoes: Teńgerim (теңгерім=баланс), Qadaǵalau, MedQarjy. Decide in first team huddle, then never revisit.

## 8. Strategic don'ts

- **Don't** build auth, multi-tenant admin, or settings pages beyond RBAC stub — zero jury value.
- **Don't** train custom ML — explainable stats + rules beat a hackathon-trained model, and are defensible in Q&A.
- **Don't** promise real-time HL7/FHIR integration — say "adapters for exports today, API integration in pilot" (see 05-ARCHITECTURE §8).
- **Don't** show a single hallucinated number. Copilot numbers come from SQL only (07-COPILOT §4). One wrong ₸ on stage kills trust with this jury.
- **Don't** frame anti-приписки as "catching doctors" — frame as **protecting the clinic and honest doctors** from coding errors and fines.

## 9. Definition of Winning (in priority order)

1st place → pilot at Polyclinic №14 → MedHub ecosystem entry. Secondary: any prize + pilot offer. The pilot matters more than the money — it's the company-starting outcome. Sell the pilot-readiness: docker-compose one-command deploy, anonymized-data-only mode, rules editable by the clinic's own economist.

*Cross-refs: domain facts → 02-DOMAIN; features → 04-PRODUCT-SPEC; hour-by-hour → 08-EXECUTION; pitch script → 09-PITCH-DEMO.*
