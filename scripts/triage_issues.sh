#!/usr/bin/env bash
# GitHub issue triage — make the repo look clean to judges browsing it.
#
# The demo-prep PAT cannot close/comment/label issues ("Resource not accessible
# by personal access token"). Run this LOCALLY with a token that has `issues:
# write` on k4ssymzhomart/alemai:
#
#   gh auth login          # or export GH_TOKEN=<token with issues:write>
#   bash scripts/triage_issues.sh
#
# It (1) closes every superseded legacy issue (junior queues, story issues,
# stale protocol issues — all now tracked in docs/13–21) with one comment, then
# (2) creates a clean board: a pinned STATUS issue + ~8 roadmap issues.
# Idempotent-ish: re-running skips already-closed issues; roadmap issues would
# duplicate, so only run part (2) once.
set -euo pipefail
REPO="k4ssymzhomart/alemai"
NOTE="Superseded by SOLO mode; scope tracked in docs/13–21 (epics A–E, demo-ready)."

echo "== 1. Closing superseded issues #1–#55 =="
for n in $(seq 1 55); do
  state=$(gh issue view "$n" --repo "$REPO" --json state --jq .state 2>/dev/null || echo MISSING)
  [ "$state" = "OPEN" ] || { echo "  #$n $state — skip"; continue; }
  gh issue close "$n" --repo "$REPO" --comment "$NOTE" && echo "  #$n closed"
done

echo "== 2. Roadmap board (run ONCE) =="
if [ "${SKIP_CREATE:-0}" = "1" ]; then echo "  SKIP_CREATE=1 — not creating"; exit 0; fi

status=$(gh issue create --repo "$REPO" --title "📌 STATUS — QALAM demo-ready (epics A–E ✅)" --body "$(cat <<'EOF'
QALAM (ранее Igerim) — Task 07, Astana AI Week 2026. SOLO mode.

**Epics A–E complete, main demo-stable** (tag \`demo-stable\`):
- A/A.2 — QALAM design system (premium B&W, Manrope)
- B — gp14-real data + storylines manifest
- C — rules engine (ЕКД, golden 8/8) + pre-billing + reconcile + возражения + Passport
- D — docgen (обращение docx) + copilot (deterministic, kk) + roles/settings
- E — demo-reset <60s, golden-path QA ×2, pitch render, print pack

Golden path (beats 1–6) verified: освоение 60,8% · пре-биллинг 46/168 600 ₸ · санкц. риск 6,67 млн ₸ · сверка 260/2 992 000 ₸ · копилот kk. Scope & pitch in docs/13–21. Open issues below = roadmap only.
EOF
)")
echo "  STATUS: $status"
gh issue pin "$status" --repo "$REPO" 2>/dev/null && echo "  pinned" || echo "  (pin needs perms; pin manually)"

roadmap() { gh issue create --repo "$REPO" --title "$1" --body "$2" --label roadmap 2>/dev/null \
  || gh issue create --repo "$REPO" --title "$1" --body "$2"; }  # label may not exist yet

roadmap "[roadmap] Damumed МИС API connector" "Auto-pull service registries from Damumed (today: XLSX import + mapping wizard). docs/14 IT-6."
roadmap "[roadmap] ИСФ defect webhooks" "Receive ИСФ defect notifications via API instead of выгрузка import. docs/14 DF-6."
roadmap "[roadmap] Live LLM copilot mode" "3-stage RapidAPI/Claude parse path behind LLM_MODE=live; canned stays default. (RapidAPI key returned HTTP 402 at freeze.)"
roadmap "[roadmap] City rollout — 14 ГП live panel" "city-composite profile → live curator panel with normalized снятия/1000. Beat 7."
roadmap "[roadmap] Линейная шкала исполнения" "Position on the payment linear scale (Правила оплаты п. 78). docs/14 EC-14."
roadmap "[roadmap] 1С export connector" "Direct снятия/неустойки export to 1С (today: CSV). docs/14 BU-4."
roadmap "[roadmap] Режим прозрачности для ФСМС" "Read-only invited витрина for the Fund — Qalqan-complement. docs/14 KU-4."
roadmap "[roadmap] Security hardening" "Auth/SSO, audit-log completeness, on-prem posture, pen-test before pilot."
echo "== done =="
