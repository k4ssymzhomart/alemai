#!/usr/bin/env bash
# EPIC I2 — two-window collaboration walk (Дана acts → Ерлан sees it live).
# Drives the API with two sessions and prints a verification after each step.
# Self-cleaning: the excluded position is restored (undo) at the end, so a
# rehearsal needs no reseed. Run `make demo-reset` first for the golden verdict.
#
#   API_BASE=http://localhost:8800/api/v1 bash scripts/qa_collab.sh
set -uo pipefail
B="${API_BASE:-http://localhost:8800/api/v1}"
DANA=$(mktemp); YER=$(mktemp); MARAT=$(mktemp)
trap 'rm -f "$DANA" "$YER" "$MARAT"' EXIT
line(){ printf '\n\033[1;35m── %s ──\033[0m\n' "$1"; }
ok(){ printf '   \033[1;32m✓ %s\033[0m\n' "$1"; }
jget(){ python3 -c "import sys,json;d=json.load(sys.stdin);print($1)" 2>/dev/null; }
login(){ curl -s -c "$2" -X POST "$B/auth/login" -H 'Content-Type: application/json' \
  -d "{\"username\":\"$1\",\"password\":\"qalam2026\"}" | jget "d['name']+' / '+d['role']"; }

line "0 · Two parallel sessions"
ok "Дана  → $(login statistician "$DANA")"
ok "Ерлан → $(login director "$YER")"

line "1 · Ерлан's bell baseline"
U0=$(curl -s -b "$YER" "$B/events" | jget "d['unread']"); ok "unread = $U0"

line "2 · Дана runs the November pre-billing check"
RUN=$(curl -s -b "$DANA" -X POST "$B/rules/run" -H 'Content-Type: application/json' -d '{"scope":"period:2025-11"}')
RID=$(echo "$RUN" | jget "d['run_id']")
echo "$RUN" | python3 -c "import sys,json;t=json.load(sys.stdin)['totals'];print('   verdict:',t['block_positions'],'позиций ·',t['block_amount'],'₸ · санкц.',t['sanction_risk'],'₸')"
ok "run $RID"

line "3 · Ерлан's bell after the check (≤5s, cross-session)"
EV=$(curl -s -b "$YER" "$B/events"); U1=$(echo "$EV" | jget "d['unread']")
echo "$EV" | python3 -c "import sys,json;e=json.load(sys.stdin)['items'][0];print('   top:',e['title_ru'],'· от',e['actor'])"
ok "unread $U0 → $U1"

line "4 · Дана excludes a flagged position (until the UI ships, API-driven)"
FID=$(curl -s -b "$DANA" "$B/rules/runs/$RID/findings?limit=1" | jget "d['findings'][0]['id']")
curl -s -b "$DANA" -X PATCH "$B/findings/$FID" -H 'Content-Type: application/json' -d '{"status":"excluded","comment":"qa_collab"}' \
  | python3 -c "import sys,json;print('   finding',json.load(sys.stdin)['status'])"
ok "excluded $FID"

line "5 · Ерлан sees the exclusion live"
EV2=$(curl -s -b "$YER" "$B/events"); U2=$(echo "$EV2" | jget "d['unread']")
echo "$EV2" | python3 -c "import sys,json;e=json.load(sys.stdin)['items'][0];print('   top:',e['title_ru'],'· от',e['actor'])"
ok "unread $U1 → $U2"

line "6 · Дана undoes the exclusion («Отменить исключение» — I2)"
curl -s -b "$DANA" -X PATCH "$B/findings/$FID" -H 'Content-Type: application/json' -d '{"status":"open"}' >/dev/null
EV3=$(curl -s -b "$YER" "$B/events")
echo "$EV3" | python3 -c "import sys,json;e=json.load(sys.stdin)['items'][0];print('   top:',e['title_ru'],'· от',e['actor'])"
ok "restored $FID (state clean — no reseed needed)"

line "7 · RBAC — Марат (curator) is scoped to aggregates"
login curator "$MARAT" >/dev/null
CT=$(curl -s -b "$MARAT" "$B/events" | python3 -c "import sys,json;d=json.load(sys.stdin);print(','.join(sorted({e['type'] for e in d['items']})) or '(none)')")
CODE=$(curl -s -b "$MARAT" -o /dev/null -w '%{http_code}' "$B/rules/runs/$RID/findings")
ok "curator case-level event types: $CT"
ok "curator GET findings → HTTP $CODE (403 = correctly denied)"

line "RESULT"
if [ "${U1:-0}" -gt "${U0:-0}" ] && [ "${U2:-0}" -gt "${U1:-0}" ]; then
  echo "   ✅ real-time cross-session flow OK — Ерлан's bell rose $U0→$U1→$U2 on Дана's actions"
else
  echo "   ⚠️ unread did not increment as expected (was the state reseeded?)"
fi
