# 25 — EPIC H «REBRAND · COLLAB · DEPLOY» (+ G5 research addendum)

> Paste to the coding agent AFTER its Epic G report. Same laws: branch+PR, golden QA (30/30 incl. Epic F import checks) before merge, demo-stable fallback, no key leaks. This epic carries THREE lead decrees that override earlier design law — apply them exactly.

---

## H0 · G5 radar addendum (research pack R14–R21 landed — consume it)

`docs/research/official_sources.csv` (34 rows, validated) + `official_sources_notes.md`:
1. Radar sources = the CSV verbatim (official_url = user quick-link; mirror_url = what the parser fetches; version_signal = the regex). One regex covers all 9 uchet.kz mirrors: `(?:Обновленный\s+)?с изменениями на:\s*(\d{2}\.\d{2}\.\d{4})` — **first match only, and guard the decoy**: the header «Дата обновления: 16.01.2024» appears ABOVE the real marker — never take the page's first date, take the pattern match. kk marker format floats — per-row signal from CSV.
2. **МРП 2026 = 4 325 ₸** (закон №239-VIII от 08.12.2025) → config `mrp_2026: 4325`; the 200/800 МРП threshold bars now show real ₸: **865 000 / 3 460 000 ₸**.
3. КПН-2026 = UNKNOWN officially → keep config value with tooltip «утверждается приказом; уточняется».
4. **Bonus (cheap, high-value): «поставщик в реестре ФСМС» AUTO badge** — fms.ecc.kz/ru/fsms/healthcare_subjects is static HTML, no login, GET pagination, fresh data (edits 29.06–02.07.2026). Radar row + a badge on the org header. Degrade to quick-link on fetch failure.
5. Deadline calendar: add the pre-announced **01.01.2027 смена редакций перечней ПП №672/№421** as a seeded future event («плановое обновление перечней — проверить маппинг источников»). Shows the system thinks ahead — jury candy.

## H1 · Rebrand decree v3 (overrides docs/15/19 where stated — lead's word is final)

1. **Logo/icon**: `logo.png` (290×93) and `icon.png` (90×82) currently in repo root → move to `frontend/public/brand/` (delete from root), wire: header (logo, height ~28), login page (logo large), favicon set generated from icon.png (16/32/180/512), docx generator letterhead (logo top-left of обращение/report — python-docx add_picture), print header. The `<Logo/>` slot contract is fulfilled — wordmark fallback stays only for missing-file edge.
2. **Accent color `#5200E0` (violet)** — new token `--accent`. Allowed uses ONLY: primary CTA buttons, active nav item indicator, links & quick-links, focus rings, selected states, small chart accents (forecast line / selected series), logo-adjacent UI. NOT for statuses, not for backgrounds, not decorative floods. The base stays white/black.
3. **Status colors decree — G/Y/R replaces B&W-only severity**: semantic tokens `--ok #12B76A`, `--warn #F79009`, `--critical #D92D20` (adjust ±1 shade for AAA on white). Apply to: risk chips, severity chips (block=red, warn=amber, yellow-defects=amber-outline, ok=green), timers (≤2 дня = red fill, not black), verdict bands (critical verdict = red-tinted left rule; band itself stays light), execution bars (fact fill stays black; status dot G/Y/R). Hatch patterns may remain as secondary texture but color is now the primary signal. Print stylesheet: statuses degrade to the old hatch/inversion (keeps the «печатается на ч/б» pitch line honest — say «в печатной форме» when using it).
4. **Default locale = RUSSIAN.** kk and en switchable; ru is base on load. The Kazakh bet lives on: copilot beat is still performed in kk, glossary law unchanged, all kk strings stay. Update demo assets (render_pitch demo table: beat 1 opens in ru, presenter switches to kk at beat 6).
5. **Remove every «демо-данные/демо-деректер» badge and footer** — all surfaces, print included. (Impact-slide "модельная оценка" caveats in PITCH-TEXT stay — that's a different honesty.)

## H2 · Fill-or-kill (the «why are pages empty» decree)

Audit every nav item. Each either gets REAL content this epic or leaves the nav (dead ends depreciate the product):
- **Тәуекелдер/Риски** → build the risk register page for real: table of risk_assessments (class chips G/Y/R, gap ₸, burn-out, deadline-to-act, [Сформировать обращение]) — API exists, this is a view.
- **Отчёты** → build: monthly report generator page (month picker, ru/kk, [Скачать docx] via existing docgen, version history list once H4 lands).
- **Календарь** → build simple: month list of `deadlines` seed + the 01.01.2027 event + возражение deadlines from objections (already computed). No calendar-grid library — a clean ledger list by date.
- **Аномалии** → if the anomaly backend service does NOT exist (check!): remove from nav, add to roadmap issue. If a cheap version is feasible ≤1.5h (doctor/day volume outliers from claims — one SQL + one table), build that.
- **Қала панелі/City** → stays killed; ensure it's not in nav.
- Everything must pass the dead-end audit from G6 again after changes.

## H3 · Shareable state links (the collaboration decision — NO Liveblocks)

Lead's call, scoped honest: no messenger, no CRM, no external realtime SaaS (venue-offline law + zero integration budget). Instead:
- `share_links` table (id short-code, url_state jsonb: route+query+filters+locale, created_by, created_at, expires nullable).
- Header button «Поделиться» on every screen → `POST /share` → copies `https://<host>/s/<code>` to clipboard (violet toast «Ссылка скопирована»).
- `/s/<code>` resolves → (login if needed) → redirect to the exact route+state. Different role opening it sees the same screen through their own permissions (curator gets aggregates view of the same context — demonstrate this, it's a feature not a bug).
- Combined with G2 events realtime this IS the collaborative mode: «я смотрю на то же, что и ты, и вижу твои изменения через 4 секунды». Two-window demo updated accordingly.
- Liveblocks/Yjs co-editing → roadmap issue «Совместное редактирование документов (пилот)»; one line in PITCH Q&A if asked.

## H4 · Document workspace lite (versions + source suggestions)

- `document_versions`: every docgen call persists (doc_type, entity_ref, params jsonb, author, ts, auto_title, docx blob or regen-params). UI: version list on the Отчёты page and on the Passport doc button (dropdown: «Версии — v3 09.07 14:02 Айгерім»), download any version, «повторить с теми же параметрами».
- **Auto-titles are deterministic** (diff of params: «Обращение по МРТ: превышение 4,8 → 5,1 млн ₸»). RapidAPI is dead (402) — IF the lead tops up the subscription, flag `LLM_TITLES=live` upgrades titles via one API call; build the flag, default off.
- **Comments/предложения источников**: `comments` table (entity_ref, author, text, type[note|source_suggestion], url nullable). Threads on: radar rows («предложить источник» with URL field) and findings. New comments → events → bell. This is the lead's «users add/edit sources» — scoped to где это реально нужно.

## H5 · Deployment pack (answer: Vercel alone — NO; Vercel + Render — YES)

Vercel can't host FastAPI+Postgres+seed jobs sanely. Build `deploy/`:
- `deploy/render.yaml` — Render Blueprint: web service (backend Dockerfile, health `/api/v1/health`, env: DATABASE_URL, CORS_ORIGINS, SEED_ON_BOOT=1 first deploy), managed Postgres.
- `deploy/vercel.md` + `vercel.json` if needed — frontend project config: root `frontend/`, env `NEXT_PUBLIC_API_BASE=https://<render-app>.onrender.com/api/v1`.
- Backend: CORS middleware reads CORS_ORIGINS; make seed runnable via `SEED_ON_BOOT` startup hook (idempotent guard); ensure no localhost hardcodes in frontend (grep).
- `deploy/README-DEPLOY.md`: exact click-path (Render Blueprint → env → deploy; Vercel import → env → deploy), plus alternative «Railway all-in-one» paragraph, plus the law: **the venue demo runs LOCAL compose regardless — the public URL is for jury follow-up, not the stage.**
- AC: `next build` with a fake prod API base green; backend container boots with SEED_ON_BOOT on a scratch DB; document the two URLs placeholder.

## Order & cut lines

H1 → H0 → H2 → H3 → H5 → H4. Cut from the bottom (H4 comments first, then H4 versions, then H5 doc-polish — never cut H1/H0/H2). Timebox ≈ one working day total.

## AC (paste real outputs)

1. Rebrand shots: header with real logo, login, favicon in tab, violet CTA + active nav, G/Y/R chips on Overview/prebilling/timers, ru default load, ZERO demo badges (grep for «демо-д» → only docs).
2. Radar consuming CSV: screenshot with ✓/⚠/— + a real «Тексеру» run log hitting uchet.kz mirrors + decoy-date unit test; МРТ thresholds showing 865 000/3 460 000 ₸; provider-registry badge state.
3. Fill-or-kill: nav before/after list; screenshots of Риски/Отчёты/Календарь with real content.
4. Share-link: two-browser screenshot pair (economist creates, curator opens same state), link round-trip time.
5. H4: version list screenshot + deterministic title example; a source-suggestion comment landing in the bell.
6. Deploy: render.yaml validated (render blueprint lint or dry doc), frontend prod-build green with prod API base, README-DEPLOY committed.
7. QA golden 30/30 ×2 (fresh + post-reset); pytest/ruff/build/CI green; locales ×3 intact; kk NEW strings glossary-reviewed (list changes).
