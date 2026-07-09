# QA — two-window real-time collaboration (EPIC I2)

The demo's core: **Дана (statistician)** acts, **Ерлан (chief/director)** sees it
**live** — the bell updates within one poll cycle (≤ 5 s), no manual refresh.
This checklist is what the presenter drives; the assertable parts are automated
in [`qa_golden.py`](qa_golden.py) (`collab` beats) and a runnable API walk is in
[`qa_collab.sh`](qa_collab.sh).

## Setup
1. `cd .claude/worktrees/main-latest && make demo-reset` — clean golden state.
2. Two browser windows side by side, both at `http://localhost:3000`:
   - **Window A (normal):** log in as `statistician` (Дана).
   - **Window B (Incognito):** log in as `director` (Ерлан).
   Password for both: `qalam2026`. Incognito is required — two roles can't share
   one cookie session (and clean cookies also dodge HTTP 431).

## Steps & expected outcomes

| # | Window | Action | Expected outcome |
|---|--------|--------|------------------|
| 1 | Ерлан | Open **Обзор** | forecast gap **70 061 600 ₸**, **4** risks, 13 lines |
| 2 | Ерлан | Note the bell 🔔 | baseline unread count (record it) |
| 3 | Дана | Open **Проверка реестра** (auto-runs the Nov check) | verdict **46 позиций · 168 600 ₸ · санкц. риск 6 665 700 ₸** |
| 4 | Ерлан | **Do not touch anything**, wait ≤ 5 s | 🔔 increments; top item «Проверка реестра (period:2025-11): 46 позиций · **от Даны**» |
| 5 | Дана | Exclude a flagged position *(see note)* | position marked «исключена» |
| 6 | Ерлан | wait ≤ 5 s | 🔔 increments; «Позиция исключена · <ЕКД> · **от Даны**» |
| 7 | Дана | **Отменить исключение** (undo) *(see note)* | position restored |
| 8 | Ерлан | wait ≤ 5 s | 🔔 «Позиция возвращена в счёт-реестр · **от Даны**» |
| 9 | Ерлан | Click the bell → «Барлығын оқылды» / mark all read | unread → 0 |
| 10 | Ерлан | Risk МРТ → **Сформировать обращение** (kk) | Word doc downloads (logo letterhead); Дана's bell shows «Сформирован документ · от Ерлана» |
| 11 | Марат (`curator`, 3rd window) | Open the app | city aggregates only; **no** case-level events in the bell, findings API returns 403 (RBAC) |

## Notes / known state (2026-07)
- **Steps 5 & 7 (exclude / undo) are API-driven today** — the per-position
  exclude/undo **UI on Проверка реестра is not shipped yet** (deferred I2 item;
  needs a frontend rebuild + browser verify). Until it ships, drive steps 5/7
  with `qa_collab.sh` or:
  ```bash
  B=http://localhost:8800/api/v1
  # (log in as Дана first to get a cookie jar, or use the service token)
  RID=$(curl -s -X POST $B/rules/run -H 'Content-Type: application/json' \
        -d '{"scope":"period:2025-11"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["run_id"])')
  FID=$(curl -s "$B/rules/runs/$RID/findings?limit=1" | python3 -c 'import sys,json;print(json.load(sys.stdin)["findings"][0]["id"])')
  curl -s -X PATCH $B/findings/$FID -H 'Content-Type: application/json' -d '{"status":"excluded"}'   # exclude
  curl -s -X PATCH $B/findings/$FID -H 'Content-Type: application/json' -d '{"status":"open"}'        # undo
  ```
- The **live bell beats that already work in the browser** with zero extra UI:
  step 3→4 (Дана opens Проверка реестра → Ерлан's bell), any **import** (Импорт →
  bell), and **обращение** generation (step 10). Lead these if recording before
  the exclude/undo UI lands.
- **Undo emits a symmetric `finding_restored` event** (I2) so rehearsals reset
  the finding without a full reseed.
- Between takes: `make demo-reset` (≈ 19 s) always restores the exact state.
