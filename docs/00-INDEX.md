# IGERIM — HACKATHON DOC PACK · INDEX

> **Product name as of 09.07.2026: QALAM** (ранее Igerim). `qalam = қалам, перо` — инструмент, которым подписывают документы. All `IGERIM` references in docs 01–18 refer to the same product; only brand surfaces (UI wordmark, favicon, README) were renamed in Epic A.2. Case-holder framing = MedHub ecosystem.

**Task 07 · Health AI Hackathon, AI WEEK Astana 2026 · Team: Kassymzhomart (LEAD) · folrwix (BE) · rasssppberrry (FE)**
Product: **IGERIM (Игерім)** — clinic-side intelligent monitoring of ГОБМП/ОСМС contract execution.
Status: hackathon LIVE. Start at 08-EXECUTION §2 (first 90 minutes). Everything else supports it.

| Doc | What's inside | Read first if you are… |
|---|---|---|
| [01-STRATEGY](01-STRATEGY.md) | Why we lost before, win thesis (5 pillars), why-now (Dec-2025 scandal, 2026 reform), impact math, judging model | everyone — read §3 aloud at huddle |
| [02-DOMAIN](02-DOMAIN.md) | ОСМС/ГОБМП primer, contract lifecycle, billing/monitoring cycle, ЕКД, glossary kk/ru/en, sources, ⚠️VERIFY list for mentors | everyone (LEAD: §9 RAG corpus) |
| [03-USER-STORIES](03-USER-STORIES.md) | Personas, as-is, 8 epics, 39 stories with AC, MoSCoW + cut lines, GitHub conventions | LEAD (issues), all devs |
| [04-PRODUCT-SPEC](04-PRODUCT-SPEC.md) | Pillar behavior contracts, 10 screens, NFRs, i18n spec, ethics posture, **golden demo path §8** | FE, then everyone |
| [05-ARCHITECTURE](05-ARCHITECTURE.md) | Stack (final), component diagram, monorepo layout, full data model, API surface, copilot guardrail design | BE, FE |
| [06-DATA-ANALYTICS](06-DATA-ANALYTICS.md) | Data triage protocol (hour one!), synthetic generator + 7 planted storylines, metrics dictionary, forecast math, **25-rule defect catalog**, anomaly design, pre-demo gates | LEAD, BE |
| [07-KAZAKH-COPILOT](07-KAZAKH-COPILOT.md) | The signature bet: 3 capabilities, no-hallucination contract, system prompt draft, 24-question eval set, fallbacks | LEAD |
| [08-EXECUTION](08-EXECUTION.md) | T0=now plan: first 90 min, phases + checkpoints, parallel tracks, git protocol, contingency matrix, time-compression table | everyone, immediately |
| [09-PITCH-DEMO](09-PITCH-DEMO.md) | 10 slides, 7-beat demo script with spoken lines, 15 hard Q&A answers, stage logistics | LEAD; all rehearse §5 |
| [10-RISKS](10-RISKS.md) | 18 pre-decided risks with triggers and owners | review at each checkpoint |

## The five pillars (if you remember nothing else)

**SEE** live план/факт → **GUARD** defects caught до счёта → **FORESEE** forecast + burn-out dates → **ACT** заявки с деньгами → **SPEAK** Kazakh copilot with citations.

## Non-negotiables

1. `main` always demoable; golden path (04 §8) is the only definition of progress.
2. No number reaches the jury that the system didn't compute.
3. Kazakh is a pillar, not a translation chore — glossary.csv is law.
4. Cut lines are pre-agreed (03 §11); at checkpoints we cut, we don't debate.
5. «До счёта, а не после штрафа» — if a feature doesn't serve that sentence, icebox it.
