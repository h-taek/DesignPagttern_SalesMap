#!/usr/bin/env bash
# SalesMap dev launcher: backend(8000) + AI(8100) + frontend(5173)
# Usage:
#   ./dev.sh            # 세 서버만 기동
#   ./dev.sh --docker   # infra/docker compose up -d 까지 같이 실행
# Ctrl+C 한 번으로 전부 종료됩니다.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/uvicorn" ]]; then
  echo "[dev.sh] .venv/bin/uvicorn 이 없습니다. GUIDELINE 2-2/2-3 참고해 가상환경부터 만드세요." >&2
  exit 1
fi

LOG_DIR="$ROOT/.dev-logs"
mkdir -p "$LOG_DIR"

if [[ "${1:-}" == "--docker" ]]; then
  echo "[dev.sh] docker compose up -d (infra) ..."
  (cd "$ROOT/infra" && docker compose up -d)
fi

pids=()

cleanup() {
  echo ""
  echo "[dev.sh] shutting down..."
  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
  echo "[dev.sh] bye."
}
trap cleanup INT TERM EXIT

echo "[dev.sh] backend  → http://localhost:8000  (log: .dev-logs/backend.log)"
"$ROOT/.venv/bin/uvicorn" app.main:app --reload --port 8000 --app-dir backend \
  >"$LOG_DIR/backend.log" 2>&1 &
pids+=($!)

echo "[dev.sh] ai       → http://localhost:8100  (log: .dev-logs/ai.log)"
"$ROOT/.venv/bin/uvicorn" app.main:app --reload --port 8100 --app-dir ai \
  >"$LOG_DIR/ai.log" 2>&1 &
pids+=($!)

echo "[dev.sh] frontend → http://localhost:5173  (log: .dev-logs/frontend.log)"
(cd "$ROOT/frontend" && npm run dev) \
  >"$LOG_DIR/frontend.log" 2>&1 &
pids+=($!)

echo "[dev.sh] all started. tail 로그를 보고 싶으면 다른 터미널에서:"
echo "         tail -f .dev-logs/backend.log .dev-logs/ai.log .dev-logs/frontend.log"
echo "[dev.sh] Ctrl+C 로 종료."

wait
