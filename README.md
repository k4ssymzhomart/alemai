# QALAM (Қалам) · ранее Igerim

**Клиникалық тарапта ГОБМП/ОСМС шарттарының орындалуын зияткерлік мониторингтеу.**
Intelligent clinic-side monitoring of ГОБМП/ОСМС contract execution — Task №07, Health AI Hackathon, AI WEEK Astana 2026.
Product name as of 09.07.2026: **QALAM** (қалам — перо, инструмент, которым подписывают документы). Docs 00–18 still say «Igerim»; same product.

> «Qalam — қаражат жоғалғанға дейін көреді.»
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

**Prerequisite:** Docker Desktop running. Nothing else — no Node, Python or Postgres on the host.

```bash
cp .env.example .env    # optional; sensible defaults work out of the box
make demo               # docker compose up (db + api + web) + seed the demo dataset
```

First run builds the images (a few minutes); later runs are instant. When it finishes:

| | URL |
|---|---|
| **App (this is the demo)** | **http://localhost:3000** |
| API | http://localhost:8800/api/v1 · Swagger: http://localhost:8800/docs |
| API health | http://localhost:8800/healthz |

**Login** — 5 seeded users, password **`qalam2026`** for all:

| Username | Персона | Роль | Что показывает |
|---|---|---|---|
| `director` | **Ерлан** | Главврач | Обзор-вердикт, колокол-уведомления, подпись обращений (docx) |
| `statistician` | **Дана** | Мед. статистик | Проверка реестра, исключение позиций до счёта, импорт |
| `economist` | Айгерім | Экономист | Прогноз, риски, корректировка объёмов |
| `curator` | Марат | Куратор УОЗ | Город: 14 клиник, только агрегаты (без пациентов) |
| `admin` | Админ | IT-админ | Импорты, справочники, нормативный радар, demo-reset |

**Reset to a clean golden state anytime** (≈ 19 s, safe to run mid-demo):

```bash
make demo-reset         # re-seeds the exact demo dataset + verifies integrity
```

## 🎬 Демо для жюри — реальное время в двух окнах (Дана ↔ Ерлан)

Ядро демо — **параллельная работа двух ролей**: медстатистик **Дана** чистит счёт-реестр,
а главврач **Ерлан** видит её действия **вживую** (колокол обновляется ≤ 5 с, без перезагрузки).

**Подготовка (30 секунд):**
1. `make demo-reset` — чистое золотое состояние.
2. Откройте **два окна** браузера рядом:
   - **Окно 1 (слева):** обычное окно → войдите как **`statistician`** (Дана).
   - **Окно 2 (справа):** окно **инкогнито** → войдите как **`director`** (Ерлан).
   *(Инкогнито обязательно: две роли не могут делить одну cookie-сессию. Бонус — чистые cookie обходят возможную ошибку 431, см. Troubleshooting.)*

**Сценарий (≈ 2 минуты, всё проверено end-to-end):**

| # | Окно | Действие | Что видит жюри |
|---|---|---|---|
| 1 | Ерлан | Экран **Обзор** | Освоение, прогноз-разрыв **70 061 600 ₸**, **4 риска** |
| 2 | Дана | **Проверка реестра** → запуск проверки за ноябрь | **46 позиций · 168 600 ₸ · санкционный риск 6 665 700 ₸** |
| 3 | Ерлан | *(ничего не трогает)* | 🔔 Колокол сам загорается ≤ 5 с: «Проверка реестра: 46 позиций · **от Даны**» |
| 4 | Дана | Исключает позицию (код 5.1) **до счёта** | Позиция помечена «исключена» |
| 5 | Ерлан | *(ничего не трогает)* | 🔔 Колокол снова растёт: «Позиция исключена · 5.1 · **от Даны**» |
| 6 | Ерлан | Риск МРТ → **Сформировать обращение** (kk) | Скачивается **Word-документ** с логотипом-бланком, на казахском |
| 7 | Ерлан | **Копайлот**: вопрос по-казахски | Ответ с цифрами дашборда + цитата приказа |
| 8 | *(опц.)* Марат (`curator`) | Войти третьим окном | Только **город/агрегаты** — пациент-уровня и findings нет (RBAC: 403) |

**Ключевая фраза:** «Дана работает — Ерлан видит это в ту же секунду. Это не отчёт постфактум, это живой контур до счёта.»

Between takes just re-run `make demo-reset`. The assertable parts of this flow are covered by
`scripts/qa_golden.py` and the seed-integrity checks.

## Monorepo layout

```
backend/    FastAPI + SQLAlchemy + Postgres (pgvector) — API, rules engine, forecast, copilot
frontend/   Next.js 14 + TypeScript + Tailwind + i18next (kk/ru/en)
datagen/    Synthetic dataset generator (calibrated to open statistics)
shared/     glossary.csv (single terminology source) + reference data
docs/       Full product/domain/execution doc pack — START at docs/00-INDEX.md
```

## Troubleshooting

- **`localhost:3000` shows `HTTP ERROR 431`** — your browser's `localhost` cookie jar is too large (cookies are shared across *all* local apps on `localhost`, any port). Fix instantly: open in **Incognito**, or clear cookies for `localhost`. The container also runs with a raised header limit so this shouldn't recur.
- **Port already in use (`3000` / `8800` / `55432`)** — another local server or a stray `next dev` is holding it. Stop it, then `make up`. (The stack uses `8800`/`55432` on purpose — `8000`/`5432` are left for other projects.)
- **`/api/v1` returns `{"detail":"Not Found"}`** — expected; that bare path has no route. Use real routes like `/api/v1/metrics/overview`, or open `/docs`.
- **Numbers look off after clicking around** — run `make demo-reset` to restore the exact golden dataset.

## Team

| Who | Role |
|---|---|
| [@k4ssymzhomart](https://github.com/k4ssymzhomart) | Lead — product, data/AI, frontend design |
| [@folrwix](https://github.com/folrwix) | Data & rules track |
| [@rasssppberrry](https://github.com/rasssppberrry) | i18n & reference content track |

## ⚡ SOLO MODE (current)

The project runs in solo mode: lead (@k4ssymzhomart) + engineering agent; the contributor tracks are absorbed. The live plan is [docs/SOLO-BACKLOG.md](docs/SOLO-BACKLOG.md) (packets P1–P10 per [docs/11-SOLO-AGENT-PROMPT.md](docs/11-SOLO-AGENT-PROMPT.md)); GitHub issues remain as passive backlog reference only. Short-lived branches or direct commits, self-merge on green CI, `main` always demoable.

## Working agreement (non-negotiable)

1. `main` is always demoable. No direct pushes — branch + PR + review by lead.
2. Branch naming: `feat/<issue-key>-short-name` (e.g. `feat/e2-rules-catalog`).
3. PR < 400 lines diff. Fill the PR template. Review SLA: 30 min.
4. No hardcoded UI strings — every label goes through i18n keys; `shared/glossary.csv` is the terminology law.
5. No number reaches the UI that the system didn't compute.

Demo data is synthetic, calibrated to open statistics («демо-данные, откалиброваны по открытой статистике»).
