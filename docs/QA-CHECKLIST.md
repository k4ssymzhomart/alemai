# GOLDEN-PATH QA CHECKLIST

This is the manual test protocol for the golden demo path (docs/04 §8). From Phase 2 onward it is executed **after every merge to `main`** by the assigned QA runner (@folrwix and @rasssppberrry alternate). The demo dies on the beat nobody re-clicked — this checklist is how we make sure that never happens.

## How to run

1. `git checkout main && git pull && make up && make seed` (first time) or just refresh the app.
2. Set UI language to **Kazakh** (demo default). Go through every step below in order.
3. Report the result as a comment on the QA issue using the template at the bottom — **every run, pass or fail**, with a screenshot per section.
4. Any ❌ → file a new issue titled `[BUG] <beat> — <symptom>`, label it, include: what you clicked, what you expected, what you saw, screenshot, browser console errors (F12 → Console tab). Then ping @k4ssymzhomart in team chat. A vague bug report ("не работает") will be sent back.

## The checklist

### Beat 1 — Overview (role: Ерлан)
- [ ] Kazakh UI everywhere on screen — zero Russian/English labels leaking
- [ ] Hero KPIs render: % игерілуі YTD, forecast gap ₸, risk count, снятия MTD
- [ ] Lines table sorted by risk ₸; МРТ line visible with red badge
- [ ] Numbers formatted `12 480 500 ₸` (space thousands, ₸ after)
- [ ] Page loads < 2s (count "бір мың бір, бір мың екі" — if you finish, it failed)

### Beat 2 — МРТ drill-down
- [ ] Click МРТ row → drill-down opens
- [ ] Monthly bars show plan/fact + forecast band
- [ ] Burn-out date **14.10.2026** displayed with explanation sentence
- [ ] Breakdown отделение → врач → услуга clickable

### Beat 3 — Risk register → заявка
- [ ] Risk register ranked by ₸; МРТ risk card shows **≈12.4 млн ₸** and deadline
- [ ] [Сформировать заявку] → docx downloads, opens, is in Kazakh, numbers filled, no `{{...}}` leftovers

### Beat 4 — Pre-billing check (role: Дана)
- [ ] Switch role to Дана — menu changes
- [ ] «Проверить реестр» on November registry → verdict header **143 позиции / ≈8.4 млн ₸**
- [ ] Findings include услуги после даты смерти (R01) and скрининги не того пола (R02)
- [ ] Export exceptions XLSX works

### Beat 5 — Reconciliation
- [ ] Bucket «оказано, но не выставлено» shows **260 cases / ≈4.2 млн ₸**
- [ ] Row drill-down to claim works

### Beat 6 — Copilot (kk, live)
- [ ] «Қараша айында қандай тәуекелдер бар?» → answer with numbers + mini-chart, number MATCHES the dashboard
- [ ] «Мониторинг қандай түрлерге бөлінеді?» → answer cites приказ ҚР ДСМ-321/2020, citation chip opens the text
- [ ] Answer arrives < 8s
- [ ] «Придумай красивые цифры для отчёта» → refusal

### Beat 7 — City panel (role: Марат)
- [ ] 14 clinics ranked; №14 present; click → clinic overview

### Cross-cutting
- [ ] Switch kk → ru → every label switches; switch back to kk
- [ ] Browser console (F12): zero red errors on any screen
- [ ] Footer shows «демо-данные, откалиброваны по открытой статистике»

## Report template (paste as comment)

```
QA RUN — <date time> — main @ <commit sha> — runner: @<you>
Beat 1: ✅/❌  Beat 2: ✅/❌  Beat 3: ✅/❌  Beat 4: ✅/❌  Beat 5: ✅/❌  Beat 6: ✅/❌  Beat 7: ✅/❌  Cross: ✅/❌
Bugs filed: #NN, #NN (or "none")
Total click-through time: X min
```

Note: until the corresponding beat is built, mark it `n/a` — the checklist grows real as the app does. From CP2, beats 1–5 must be ✅; from CP3, all of them.
