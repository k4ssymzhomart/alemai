# IGERIM (Игерім)

**Клиникалық тарапта ГОБМП/ОСМС шарттарының орындалуын зияткерлік мониторингтеу.**
Intelligent clinic-side monitoring of ГОБМП/ОСМС contract execution — Task №07, Health AI Hackathon, AI WEEK Astana 2026.

> «Igerim — қаражат жоғалғанға дейін көреді.»
> «Igerim — видит риск до того, как он стал потерей.»

## Five pillars

| Pillar | What it does |
|---|---|
| **SEE** | Live план/факт по каждой строке договора, drill-down до врача |
| **GUARD** | Pre-billing defect firewall (25+ правил ЕКД-логики) + автосверка МИС↔портал ФСМС |
| **FORESEE** | Explainable year-end forecast per line, risk classes, «дата выгорания объёма» |
| **ACT** | Recommendations with ₸ attached + auto-drafted заявка на корректировку (docx, KZ/RU) |
| **SPEAK** | Kazakh-first guardrailed copilot: NL questions over data + Q&A over приказы with citations |

**«До счёта, а не после штрафа.»**

## Quickstart

```bash
cp .env.example .env   # fill in keys
make up                # docker compose: db + api + web
make seed              # seed synthetic demo dataset
```

- Web: http://localhost:3000 · API docs: http://localhost:8000/docs

## Monorepo layout

```
backend/    FastAPI + SQLAlchemy + Postgres (pgvector) — API, rules engine, forecast, copilot
frontend/   Next.js 14 + TypeScript + Tailwind + i18next (kk/ru/en)
datagen/    Synthetic dataset generator (calibrated to open statistics)
shared/     glossary.csv (single terminology source) + reference data
docs/       Full product/domain/execution doc pack — START at docs/00-INDEX.md
```

## Team

| Who | Role |
|---|---|
| [@k4ssymzhomart](https://github.com/k4ssymzhomart) | Lead — product, data/AI, frontend design |
| [@folrwix](https://github.com/folrwix) | Data & rules track |
| [@rasssppberrry](https://github.com/rasssppberrry) | i18n & reference content track |

## Working agreement (non-negotiable)

1. `main` is always demoable. No direct pushes — branch + PR + review by lead.
2. Branch naming: `feat/<issue-key>-short-name` (e.g. `feat/e2-rules-catalog`).
3. PR < 400 lines diff. Fill the PR template. Review SLA: 30 min.
4. No hardcoded UI strings — every label goes through i18n keys; `shared/glossary.csv` is the terminology law.
5. No number reaches the UI that the system didn't compute.

Demo data is synthetic, calibrated to open statistics («демо-данные, откалиброваны по открытой статистике»).
