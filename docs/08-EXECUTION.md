# 08 — EXECUTION PLAN (T0 = NOW)

The hackathon is live. This plan is phase-based with hour offsets from T0; §8 compresses it for whatever time actually remains. LEAD adapts once the exact deadline is known — write it at the top of the team chat NOW: `DEMO AT: ____`, `FREEZE AT: DEMO−3h`.

---

## 1. Team topology (3 humans + Claude everywhere)

| Who | Track | Owns | Never blocked by |
|---|---|---|---|
| **Kassymzhomart (LEAD)** | Product/Data/AI | datagen (H4), forecast+risk (D1–D5), rules catalog content (E2), copilot (G2/G3), docs/templates (F3/G4), pitch (09), issues+reviews | others: everything LEAD builds runs on synthetic data locally |
| **folrwix (BE)** | Backend/Platform | repo+compose (H6), schema+API (05 §4–5), imports (A1/A2/B1/B2), reconciliation (B3), rules engine core (E1), alerts (F1), demo-reset (H5) | FE — API contract file agreed at T+1 |
| **rasssppberrry (FE)** | Frontend/i18n | Next.js scaffold, i18n (G1), Overview (C1/C2/C3), Risk register UI (D2/F2), Pre-billing screen (E3), Reconcile screen, Copilot UI, City panel (C5) | BE — works against mocked API from the OpenAPI stub until real endpoints land |

Claude usage protocol: every task starts by pasting the relevant doc section + interface contracts into Claude; generated code goes through LEAD review like human code. Don't hand-write boilerplate anyone can generate.

## 2. First 90 minutes (do in this order, in parallel)

- [ ] ALL: team huddle 15 min — confirm name (IGERIM), read 01 §3 pillars + 04 §8 golden path aloud, write `DEMO AT / FREEZE AT`, agree API-contract-first rule.
- [ ] LEAD: create GitHub repo `igerim`, push this docs pack, create milestone Phases 1–4, batch-create issues from 03 (MUST first, labels per 03 §12).
- [ ] BE: scaffold monorepo per 05 §3, docker-compose up postgres, FastAPI hello, CI stub. Commit `main` green.
- [ ] FE: Next.js scaffold + Tailwind + shadcn + i18next with kk/ru/en stub locales; layout shell with sidebar nav per 04 §2.
- [ ] LEAD: start datagen skeleton; commit `shared/glossary.csv` (from 02 §10).
- [ ] IF MedHub data already available → run triage protocol 06 §2 (LEAD + BE, 60–90 min hard cap) → declare REAL/HYBRID/SYNTHETIC in team chat.
- [ ] ALL: mentors question list dispatched (06 §2.5): корректировка windows, ЕКД list, счёт-реестр sample, №14 export formats.

## 3. Phase plan

### Phase 1 — Spine (T+1.5h → T+10h) · goal: data flows end to end
BE: schema migration, `POST /imports/*` for contract + MIS export + fund statement (CSV/XLSX adapters, quarantine), mv_line_execution, `GET /metrics/*`.
LEAD: datagen v1 (contract + claims + statuses, no storylines yet) → seed works; API contract (OpenAPI) frozen with FE; issue triage.
FE: Overview C1 against mock → swap to real API when metrics land; i18n keys as-you-go (no hardcoded strings — PR checklist).
**Checkpoint CP1 (T+10h): dashboard shows seeded план/факт end to end. If CP1 slips >2h → cut C4/D4 now (03 §11 cut line 1).**

### Phase 2 — Differentiators core (T+10h → T+22h)
LEAD: storylines 1–7 into datagen; forecast engine D1→D3 + backtest; risk classes D2; recommendations F2 content.
BE: rules engine E1 + first 12 rules wired (R01–R04, R06, R07, R10, R11, R15–R17, R20); reconciliation B3; amendments A2.
FE: line drill-down C2, risk register + rec cards, pre-billing screen E3, reconcile screen.
**Checkpoint CP2 (T+22h): golden-path beats 1–5 clickable (kk UI, maybe rough). Rules catch storylines (golden tests green).**

### Phase 3 — SPEAK + ACT (T+22h → T+34h)
LEAD: copilot — semantic layer, tools, prompts, validator; regs corpus fetched+chunked (kk+ru); eval set run; docx templates F3/G4 (заявка kk/ru, monthly report kk/ru).
BE: copilot endpoints (SSE), alerts F1 + deadlines seed, city aggregates C5, demo-reset H5, remaining rules to 25.
FE: copilot panel (streaming, citation chips, «как посчитано» trace), reports screen, city panel, waterfall C3, polish pass on kk texts (native-check every visible string).
**Checkpoint CP3 (T+34h): full golden path 1–7 runs. Copilot eval ≥22/24. `make demo-reset` <60s.**

### Phase 4 — Freeze & stagecraft (T+34h → demo)
- FREEZE at DEMO−3h: only bugfixes on golden path; new features forbidden (LEAD enforces ruthlessly — this is where hackathons die).
- Pitch deck final (09 §3), print one Kazakh monthly report artifact, screen-record full golden path as fallback video.
- Two full dress rehearsals with timer (demo <7 min), incl. one on battery + phone hotspot.
- Sleep plan: minimum one 3h block per person across any 48h window; LEAD schedules staggered.

## 4. Parallelism rule that saves us

SEE (BE+FE) and FORESEE/SPEAK (LEAD) are **independent tracks by design** — LEAD's engines run on the seeded DB and expose pure functions; BE wires them to API when ready. Last time differentiation waited for the baseline; this time they progress simultaneously. If a track stalls, its owner shouts in chat within 15 min ("stuck > 15 min = escalate to Claude/mentor/pair").

## 5. Git & review protocol (LEAD)

- `main` protected, always demoable; short-lived branches; PR <400 lines; review SLA 30 min; self-merge allowed ONLY for docs/locales.
- Merge order priority: golden-path blockers > MUST > SHOULD.
- Conventional commits; issue refs (`feat: forecast burn-out date (#D3)`).
- Every merge → FE smoke: click golden path 1–7 (2 min ritual).

## 6. Gates (no-go without them)

| Gate | Criteria |
|---|---|
| G-DATA (end of triage) | REAL/HYBRID/SYNTHETIC decided, seed reproducible |
| G-DEMO (CP3) | golden tests 7/7, eval ≥22/24, reset <60s, path <7 min twice |
| G-FREEZE | deck done, video fallback recorded, roles for demo assigned (driver: Дана-screens = FE; narrator: LEAD; copilot ops: BE) |

## 7. Contingency matrix

| If | Then |
|---|---|
| Real data unusable/late | SYNTHETIC mode (we planned for it; say so proudly: «архитектура принимает реальные выгрузки — вот адаптеры») |
| LLM API blocked on venue Wi-Fi | phone hotspot; cached canned answers (07 §7); fallback provider key ready |
| Rules engine perf issue | pre-run findings at seed time; UI reads persisted results |
| FE integration hell at CP2 | FE presents from Storybook-ish mock with real numbers exported to JSON — jury can't tell; fix after |
| Team member down (sick/sleep) | tracks are independent; LEAD redistributes MUSTs by cut lines 03 §11 |
| Demo machine dies | cloud mirror URL + video; deck has screenshots of every beat |

## 8. Time compression table (unknown deadline → pick row)

| Time left | Keep | Pre-cut immediately |
|---|---|---|
| ~48h | full plan | — |
| ~36h | Phases as-is, thinner Phase 3 | C4, D4, E5, E6, H2 |
| ~24h | CP1 + storylines + D1–D3 + E1 with 8 rules + G2 (data Q&A only) + F3 (заявка ru) + golden path 1–4,6 | C3, C5, G3→canned citations, G4, E4 |
| ~12h (worst) | dashboard + 5 rules + burn-out + 1 docx + copilot canned demo | everything else; win on pitch + domain depth |

## 9. Standing meeting rhythm

- Sync at every checkpoint + every 4h max, 10 min, standing: golden-path status, blockers, cut decisions. LEAD writes one-line status to chat after each (`CP2 ✅ / МРТ storyline green / FE swap at 14:00`).
- Decision log = pinned message; disputes get 5 minutes then LEAD decides (speed > consensus at hour 30).
