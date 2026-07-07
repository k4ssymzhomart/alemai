# 05 — ARCHITECTURE

Design principle: **boring, fast, explainable.** Every component must be buildable by 3 people during a live hackathon, demoable offline on a laptop, and defensible to a technical judge in one sentence.

---

## 1. Stack (final — do not relitigate mid-hackathon)

| Layer | Choice | One-sentence defense |
|---|---|---|
| Backend | **Python 3.12 + FastAPI + SQLAlchemy 2 + Pydantic v2** | analytics-native language; typed API; autodocs (/docs) impress judges |
| DB | **PostgreSQL 16 + pgvector** | one DB for OLTP, analytics views, and RAG embeddings — zero extra infra |
| Analytics | **pandas + numpy + statsmodels** (in-process) | explainable stats > black-box ML for a finance jury |
| Rules | **YAML catalog → Python evaluator** (compiles to SQL/pandas predicates) | domain experts can read the rules; editable without deploy |
| LLM | **Claude API** (claude-sonnet) via tool-use; provider-agnostic thin client (fallback: OpenAI; roadmap: local KazLLM) | best multilingual quality for kk; guardrails via tools |
| Frontend | **Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui + ECharts + i18next** | fast to build, looks like a product, i18n first-class |
| Docs gen | **python-docx + docxtpl (jinja)** | заявка/report templates kk/ru |
| Infra | **docker-compose** (db, api, web) + Makefile (`make up seed reset demo`) | one command = pilot-readiness proof |
| Background jobs | FastAPI BackgroundTasks (no Celery) | hackathon: fewer moving parts |

Anti-choices (ready answers): no microservices (unnecessary), no Kafka (batch imports), no custom-trained model (no labeled data in 48h; rules+stats are auditable), no Streamlit (product look matters).

## 2. Component diagram

```
                ┌────────────────────────── Next.js (kk/ru/en) ──────────────────────────┐
                │ Overview │ Risks │ Pre-billing │ Reconcile │ Copilot │ Reports │ City │
                └────────────┬───────────────────────────────┬───────────────────────────┘
                             │ REST /api/v1                  │ SSE (copilot stream)
        ┌────────────────────▼────────────────────────────────▼───────────────────┐
        │                          FastAPI                                        │
        │  ingest/ (parsers, mapping, quarantine)   analytics/ (metrics, forecast)│
        │  rules/  (YAML loader, evaluator)         recs/ (recommendations, docx) │
        │  copilot/ (orchestrator, tools: run_metric_query | search_regulations   │
        │            | get_glossary; prompt builder; citation formatter)          │
        └───────┬──────────────────────┬──────────────────────────┬───────────────┘
                │ SQLAlchemy           │ pgvector search           │ Claude API (or fallback)
        ┌───────▼──────────────────────▼──────────┐        ┌──────▼──────┐
        │ PostgreSQL: core schema + agg views     │        │  LLM        │
        │ + regulations chunks (embeddings)       │        └─────────────┘
        └─────────────────────────────────────────┘
Imports in: XLSX/CSV (договор, доп.согл., МИС export, portal statements, РПН) → adapters
```

## 3. Monorepo layout

```
igerim/
├── docker-compose.yml, Makefile, .env.example, README.md
├── backend/
│   ├── app/main.py, api/ (routers: contracts, imports, metrics, risks, rules,
│   │        reconcile, alerts, copilot, reports, admin)
│   ├── app/models/ (SQLAlchemy), app/schemas/ (Pydantic)
│   ├── app/services/ {ingest, metrics, forecast, rules_engine, anomaly,
│   │        recommendations, reconcile, docgen, copilot}
│   ├── rules/*.yaml            # the catalog (06 §7) — reviewable by domain experts
│   ├── templates/*.docx        # zayavka_kk, zayavka_ru, report_kk, report_ru
│   ├── regs/                   # fetched приказы (kk+ru), chunker script
│   └── tests/ (rules golden tests, forecast backtest, api smoke)
├── frontend/
│   ├── app/(dashboard)/..., components/, lib/api.ts
│   └── locales/{kk,ru,en}.json          # built partly from shared/glossary.csv
├── datagen/
│   ├── generate.py (06 §4), storylines.py, config.yaml
├── shared/glossary.csv          # single terminology source (04 §5)
└── docs/                        # this pack
```

## 4. Data model (core tables; ids uuid; money in тиын-free int ₸; all times UTC)

- **organizations** (id, name_kk, name_ru, type[polyclinic|hospital], attached_population)
- **contracts** (id, org_id, year, number, status)
- **contract_lines** (id, contract_id, care_type[pmsp|kdu|day_hosp|hosp|dent|screening|ambulance], funding_source[gobmp|osms], service_group nullable, month, plan_qty, plan_amount, version_id)
- **contract_versions** (id, contract_id, amendment_no, effective_date, note) — A2 versioning; lines reference version
- **patients** (id=hash, sex, birth_year, attached bool, insured bool, death_date nullable)
- **doctors** (id, org_id, full_name_masked, specialty, dept, schedule_ref nullable)
- **claims** (id, org_id, patient_id, doctor_id, dept, care_type, funding_source, service_code, service_name, icd10, date_start, date_end, qty, tariff, amount, referral_id nullable, status[mis_only|submitted|accepted|rejected|paid], period YYYY-MM, source_file_id)
- **import_files** (id, kind[contract|amendment|mis|fund_statement|rpn], filename, rows_ok, rows_quarantined, control_sum, loaded_at)
- **quarantine_rows** (import_file_id, row_no, raw jsonb, errors[])
- **rules** (code, severity, scope, enabled, params jsonb, message_kk, message_ru, origin) — mirrors YAML
- **findings** (id, run_id, rule_code, claim_id, amount_at_risk, details jsonb, status[open|excluded|fixed|dismissed])
- **rule_runs** (id, scope, started_at, duration_ms, totals jsonb)
- **forecasts** (id, line_key(contract_id,care_type,source,service_group), as_of, horizon_month, method, value_qty, value_amount, ci_low, ci_high, explanation, inputs_hash)
- **risk_assessments** (id, line_key, as_of, class, gap_amount, burn_out_date nullable, recommendation jsonb)
- **alerts** (id, type, severity, title_kk, title_ru, amount, due_date, entity_ref, status)
- **deadlines** (id, kind[korrektirovka_window|invoice_due|report_due], starts, ends, note) — seeded config ⚠️verify dates onsite
- **package_mapping** (icd10/service_code, funding_source, valid_from, valid_to) — the 2026 Единый пакет table (A4)
- **reg_documents** (id, title, number, lang, url) / **reg_chunks** (doc_id, anchor, text, embedding vector)
- **users** (id, name, role), **audit_log** (who, what, when)

Aggregates: materialized view **mv_line_execution** (line_key, month → plan_qty/amount, fact_qty/amount by status, снято_amount) refreshed after imports/rule runs — dashboard reads only this (NFR <2s).

## 5. API surface (REST /api/v1; all list endpoints filterable by contract, source, care_type, period)

- `POST /imports/{kind}` multipart → {file_id, rows_ok, quarantined} ; `GET /imports/{id}/quarantine`
- `GET /contracts`, `GET /contracts/{id}/lines?as_of=`, `POST /contracts/{id}/amendments`
- `GET /metrics/overview`, `GET /metrics/lines`, `GET /metrics/line/{key}/monthly`, `GET /metrics/waterfall`
- `GET /reconcile/buckets`, `GET /reconcile/bucket/{n}/rows`
- `POST /rules/run` {scope} → run_id ; `GET /rules/runs/{id}/findings?group_by=rule` ; `PATCH /findings/{id}` (exclude/dismiss)
- `GET /forecasts?as_of=`, `POST /forecasts/recompute`
- `GET /risks`, `GET /risks/{id}/recommendation`, `POST /risks/{id}/generate-doc` {lang} → docx
- `GET /alerts`, `GET /deadlines`
- `POST /copilot/ask` {question, locale, screen_context} → SSE stream {tokens, tool_traces, citations}
- `POST /reports/monthly` {month, lang} → docx/pdf
- `GET /city/overview` (curator)
- `POST /admin/demo-reset` (H5)

## 6. Copilot architecture (the guardrail design — technical jury bait)

```
question → intent router (data | regulation | report | out_of_scope)
  data:      LLM + tools:
             • list_metrics() → semantic layer catalog (metric name, dims, description kk/ru)
             • run_metric_query(metric, filters, period, group_by) → rows   ← ONLY numbers source
             (no raw SQL from LLM; server builds SQL from whitelisted metric definitions)
  regulation: embed(question) → pgvector top-k over reg_chunks (kk+ru) → LLM answers
             ONLY from chunks, each sentence tagged with citation ids → UI renders «п. X, приказ Y»
  report:    fills report skeleton with run_metric_query results, then styles text
Guards: system prompt (07 §5) + response validator: every number in output must match a number
present in tool results (regex+normalize); violation → regenerate with stricter prompt (1 retry) → fallback template answer.
```

Semantic layer = `metrics.yaml`: ~15 metrics (execution_pct, plan_amount, fact_amount, снято_amount, forecast_gap, burn_out_date, findings_count, недовыставлено_amount...) × dims (month, care_type, source, dept, doctor). Copilot can ONLY compose these. This one file is our "no hallucinated numbers" proof — show it if judges probe.

## 7. Performance & demo resilience

- Seed once → `pg_dump` snapshot → demo-reset = restore (<60s, H5).
- All demo queries hit materialized views; recompute forecast pre-demo, not live (except the what-if, which is in-memory).
- Copilot: pre-warm with 2 canned questions before stage; cache embeddings; if network dies → local fallback: intent router answers the 6 rehearsed questions from cached tool results (looks identical). Full offline video as last resort (08 §7).

## 8. Pilot-phase integration story (say, don't build)

Roadmap slide: MIS API/DB-view integration (Damumed), Fund portal auto-download, РПН sync, 1С export, SSO — "экспортные адаптеры сегодня → API-коннекторы в пилоте; архитектура уже разделяет ingest-адаптеры от ядра". True, because ingest/ is adapter-pattern.

## 9. Testing (minimum that prevents demo death)

- Golden tests per rule: each rule has a fixture claim set with expected findings (planted storylines double as fixtures).
- Forecast backtest test: MAPE threshold on synthetic history.
- API smoke: docker healthcheck + `pytest -m smoke` hitting every GET.
- Frontend: manual golden-path checklist (04 §8) run after every merge to main; no unit-test theater.
- CI: GitHub Actions — lint (ruff, eslint), smoke tests, docker build. Red main = stop-the-line.
