#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-development}"
AGENT_PORT="${PARTNER_AGENT_PORT:-8000}"
export LANGGRAPH_STRICT_MSGPACK=true

if [[ "$MODE" == "development" ]]; then
  uv sync --frozen
  export NODE_ENV=development
elif [[ "$MODE" == "production" ]]; then
  export NODE_ENV=production
else
  echo "Expected mode: development or production" >&2
  exit 2
fi

uv run --no-sync python -m uvicorn partner_agent_graph.api:app \
  --host 127.0.0.1 --port "$AGENT_PORT" --log-level info &
agent_pid=$!
api_pid=""

cleanup() {
  if [[ -n "$api_pid" ]]; then
    child_pids="$(pgrep -P "$api_pid" || true)"
    if [[ -n "$child_pids" ]]; then
      kill $child_pids 2>/dev/null || true
    fi
    kill "$api_pid" 2>/dev/null || true
  fi
  kill "$agent_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ready=false
for _ in $(seq 1 60); do
  if ! kill -0 "$agent_pid" 2>/dev/null; then
    break
  fi
  if curl --silent --fail "http://127.0.0.1:${AGENT_PORT}/healthz" >/dev/null; then
    ready=true
    break
  fi
  sleep 0.5
done

if [[ "$ready" != "true" ]]; then
  echo "Partner agent service did not become healthy on port ${AGENT_PORT}." >&2
  exit 1
fi

if [[ "$MODE" == "development" ]]; then
  pnpm --filter @workspace/api-server run dev &
else
  node --enable-source-maps artifacts/api-server/dist/index.mjs &
fi
api_pid=$!

wait -n "$agent_pid" "$api_pid"
