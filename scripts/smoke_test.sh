#!/usr/bin/env bash
set -euo pipefail

API="${API:-http://localhost:8000/api/v1}"
MAX_WAIT="${SMOKE_WAIT_SEC:-90}"

fail() { echo "FAIL: $1" >&2; exit 1; }

command -v curl >/dev/null || fail "curl required"
command -v jq >/dev/null || fail "jq required (sudo apt install jq)"

echo "0. Waiting for API at $API (up to ${MAX_WAIT}s) ..."
elapsed=0
until curl -sf "$API/health" >/dev/null 2>&1; do
  if (( elapsed >= MAX_WAIT )); then
    echo "Backend logs (last 20 lines):"
    docker compose logs backend --tail 20 2>/dev/null || true
    fail "API not reachable after ${MAX_WAIT}s. Check: docker compose logs backend"
  fi
  sleep 3
  elapsed=$((elapsed + 3))
  echo "   ... still waiting (${elapsed}s)"
done
echo "   API is up."

echo "1. Health check"
curl -sf "$API/health" | jq .

echo "2. Bins registered"
curl -sf "$API/bins" | jq 'length'

echo "3. Telemetry flowing (wait 10 s...)"
sleep 10
curl -sf "$API/telemetry/latest" | jq 'length'

echo "4. DCPI computed"
curl -sf "$API/dcpi" | jq '.[0]'

echo "5. Route optimized"
curl -sf -X POST "$API/routes/optimize" | jq .

echo "6. KPI summary"
curl -sf "$API/kpis/summary" | jq .

echo "ALL PASS"
