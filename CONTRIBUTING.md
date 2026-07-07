# CONTRIBUTING — IGERIM working agreement

Condensed from docs/03-USER-STORIES.md §12 and docs/08-EXECUTION.md §5. LEAD enforces. When in doubt: does it make the golden demo path (docs/04 §8) stronger?

## Non-negotiables

- **`main` is always demoable.** Red main = stop-the-line. Every merge to main is followed by the 2-minute frontend smoke ritual: click golden path steps 1–7.
- **Never push directly to `main`.** All changes go through a PR.
- **Branch naming:** `feat/<key>-name`, e.g. `feat/a1-contract-import` (issue key lowercase, short kebab-case name).
- **PR template is mandatory:** what / screenshots / i18n-keys-added? / rules-touched? / how-tested.
- **PRs are small: <400 lines diff.** Split anything bigger.
- **Review:** request review from **@k4ssymzhomart**; SLA is 30 minutes. Self-merge is allowed ONLY for docs and locale files (`docs/**`, `frontend/locales/**`).
- **Merge order priority:** golden-path blockers > MUST > SHOULD.
- **Conventional commits** with issue refs, e.g. `feat: forecast burn-out date (#D3)`.
- **No hardcoded UI strings.** All UI text lives in `frontend/locales/{kk,ru,en}.json` with namespaced keys (`risk.class.critical_under`). The PR checklist blocks hardcoded strings.
- **`shared/glossary.csv` is terminology law.** It is the single source for UI locales, the copilot system prompt, and docx templates. Fix a term there, nowhere else.
- **Conventions from docs/05 §4:** money as integer ₸ (no decimals), all times UTC, ids uuid.

## The junior workflow loop (follow exactly, every time)

1. `git pull` on `main` — start from the latest.
2. Create a branch: `git checkout -b feat/<key>-name`.
3. Work in **small commits** with clear conventional-commit messages.
4. `git push -u origin feat/<key>-name`.
5. Open a PR and fill the template completely.
6. Request review from @k4ssymzhomart.
7. Respond to every review comment (fix or reply) — do not merge past unresolved comments.
8. **Never push to `main`.** Merge only after approval (except docs/locales self-merge).

## Issues

One issue per story, title = `[A1] Import contract line items`; labels `epic:A..H`, `must/should/could`, `demo-critical`, `size:S/M/L`; milestones `Phase 1..4` per docs/08.

## Local commands

`make up` (stack), `make demo` (stack + seed), `make fmt` / `make lint` before pushing. See the Makefile.
