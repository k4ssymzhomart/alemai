# 10 — RISK REGISTER

Scoring: P (probability 1–5) × I (impact 1–5). Review at every checkpoint (08 §6); owner shouts when trigger fires. Mitigations are pre-decided — no debating at hour 30.

| # | Risk | P | I | Trigger | Mitigation / pre-decision | Owner |
|---|------|---|---|---------|---------------------------|-------|
| 1 | Real MedHub data late, partial, or unusable | 4 | 4 | Triage (06 §2) fails ≥1 criterion | SYNTHETIC/HYBRID mode declared within 90 min; storylines guarantee the demo; adapters shown as integration proof | LEAD |
| 2 | Real data contradicts our domain assumptions (fields, formats, care types) | 3 | 4 | Adapter mapping <90% joinable | Map what joins, quarantine rest visibly (feature, not bug: "система показывает грязные данные"); ask mentors same hour | BE |
| 3 | Scope creep / baseline trap repeat | 4 | 5 | Any work not on a MUST story while golden path incomplete | Cut lines 03 §11 pre-agreed; LEAD enforces at checkpoints; new ideas → `icebox` label, zero discussion | LEAD |
| 4 | Copilot Kazakh quality embarrasses us on stage | 2 | 5 | Eval set <22/24 at CP3 | Glossary-forced prompts; native review of 6 demo answers; fallback: ru body + kk terms; canned cached answers for rehearsed questions | LEAD |
| 5 | LLM API unreachable at venue | 3 | 4 | Pre-demo pre-warm fails | Hotspot; second provider key; cached answers (07 §7); worst case — video beat 6 | BE |
| 6 | Integration hell FE↔BE at CP2 | 3 | 4 | Golden beats 1–5 not clickable at CP2 | API contract frozen at T+1; FE mock mode with exported real JSON — demo from mock is allowed | FE |
| 7 | Forecast looks wrong on real data (regime changes, sparse lines) | 3 | 3 | Backtest MAPE >15% on real | Demo forecasts on synthetic/hybrid lines; state honestly; show MAPE badge — honesty is the feature | LEAD |
| 8 | Jury: "this exists already / Fund has it" | 3 | 4 | Q&A | Rehearsed answer 09 §5 Q1 (provider-side, pre-billing, forecast, kk) — do not improvise | LEAD |
| 9 | Demo machine/venue failure | 2 | 5 | — | Cloud mirror + full golden-path video + screenshots in deck; reset script <60s | BE |
| 10 | Team burnout / member down | 3 | 3 | Anyone >20h awake | Staggered 3h sleep blocks scheduled by LEAD (08 §3 Phase 4); independent tracks absorb loss | ALL |
| 11 | Regulatory facts wrong on stage (номера приказов, windows) | 2 | 4 | Mentor contradicts a ⚠️VERIFY item | All ⚠️VERIFY items from 02 asked to mentors day one; slides avoid unverified specifics; copilot cites corpus only | LEAD |
| 12 | Over-polished deck, under-rehearsed demo | 2 | 4 | <2 full dress runs done | G-FREEZE gate blocks: no rehearsals → no new slides | LEAD |
| 13 | Rules engine flags too much (noise) on real data | 2 | 3 | Findings >5% of claims | Thresholds are params; demo severity=block only; noise reframed: "настройка чувствительности — за клиникой" | BE |
| 14 | Another team does Kazakh copilot too | 1 | 3 | Scouting during event | Ours is guardrailed + cited + glossary-consistent; emphasize validator live (Q21 honesty test) | LEAD |
| 15 | Demo exceeds time slot | 3 | 3 | Dress run >7 min | Beat 7 (city panel) is the designated skip; never skip beats 2/4/6 | LEAD |
| 16 | Losing the "why now" urgency in delivery | 2 | 3 | Dry run feels flat | Cold open slide 1 memorized verbatim; печатный kk отчёт в руки жюри | LEAD |
| 17 | Git chaos, broken main before demo | 2 | 4 | Red CI on main | Protected main, freeze at DEMO−3h, tag `demo-stable` at CP3; rollback = `git checkout demo-stable && make demo-reset` | BE |
| 18 | Prize-jury asks for live edit ("add a rule now") | 2 | 2 | Q&A | H2 rule editor if built; else edit YAML live in editor + rerun — rehearse this 2-min stunt once | BE |

**Meta-risk:** this doc pack goes unread by the team. Mitigation: 08 §2 huddle reads 01 §3 + 04 §8 aloud; each member's first issue links their track's doc sections.
