#!/usr/bin/env bash
# SalesMap dev launcher (Java): backend(8000) + AI(8100) + frontend(5173)
# Usage:
#   ./dev.sh            # 세 서버만 기동
#   ./dev.sh --docker   # infra/docker compose up -d 까지 같이 실행
#   ./dev.sh --build    # 기동 전에 ./gradlew build 로 양 모듈 빌드
# Ctrl+C 한 번으로 전부 종료됩니다.
#
# 환경변수(.env 대신 export 하거나 앞에 붙여 실행):
#   DATABASE_URL (기본 jdbc:postgresql://localhost:5432/salesmap)
#   DB_USERNAME / DB_PASSWORD (기본 salesmap / salesmap)
#   OPEN_API_KEY, INTERNAL_TOKEN, CORS_ORIGINS, PREDICTOR

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/gradlew" ]]; then
  echo "[dev.sh] gradlew 가 없습니다. 프로젝트 루트에서 실행하세요." >&2
  exit 1
fi

LOG_DIR="$ROOT/.dev-logs"
mkdir -p "$LOG_DIR"

DO_DOCKER=false
DO_BUILD=false
for arg in "$@"; do
  case "$arg" in
    --docker) DO_DOCKER=true ;;
    --build)  DO_BUILD=true ;;
    *) echo "[dev.sh] 알 수 없는 옵션: $arg" >&2; exit 1 ;;
  esac
done

if [[ "$DO_DOCKER" == true ]]; then
  echo "[dev.sh] docker compose up -d (infra) ..."
  (cd "$ROOT/infra" && docker compose up -d)
fi

if [[ "$DO_BUILD" == true ]]; then
  echo "[dev.sh] ./gradlew build -x test ..."
  "$ROOT/gradlew" build -x test
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
"$ROOT/gradlew" :backend-java:bootRun \
  >"$LOG_DIR/backend.log" 2>&1 &
pids+=($!)

echo "[dev.sh] ai       → http://localhost:8100  (log: .dev-logs/ai.log)"
"$ROOT/gradlew" :ai-java:bootRun \
  >"$LOG_DIR/ai.log" 2>&1 &
pids+=($!)

echo "[dev.sh] frontend → http://localhost:5173  (log: .dev-logs/frontend.log)"
(cd "$ROOT/frontend" && npm run dev) \
  >"$LOG_DIR/frontend.log" 2>&1 &
pids+=($!)

echo "[dev.sh] all started. tail 로그를 보고 싶으면 다른 터미널에서:"
echo "         tail -f .dev-logs/backend.log .dev-logs/ai.log .dev-logs/frontend.log"
echo "[dev.sh] 최초 기동은 Gradle 의존성 다운로드로 시간이 걸릴 수 있습니다."
echo "[dev.sh] Ctrl+C 로 종료."

wait
