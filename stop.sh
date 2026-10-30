#!/usr/bin/env bash
set -euo pipefail

# Resolve project root directory regardless of where the script is called from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# Detect operating system (Linux, macOS, Windows Git Bash / MSYS2 / Cygwin / WSL)
detect_os() {
  local uname_out
  uname_out="$(uname -s 2>/dev/null || echo "Unknown")"
  case "${uname_out}" in
    Linux*)
      if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "Windows (WSL)"
      else
        echo "Linux"
      fi
      ;;
    Darwin*)
      echo "macOS"
      ;;
    CYGWIN*|MINGW*|MSYS*)
      echo "Windows (Git Bash / MSYS)"
      ;;
    *)
      echo "${uname_out}"
      ;;
  esac
}

OS_NAME="$(detect_os)"

# Prevent Git Bash / MSYS2 on Windows from converting POSIX paths passed to Docker
case "${OS_NAME}" in
  "Windows (Git Bash / MSYS)")
    export MSYS_NO_PATHCONV=1
    export MSYS2_ARG_CONV_EXCL="*"
    ;;
esac

echo "============================================================"
echo "  Edge TTS - Stop Script (OS: ${OS_NAME})"
echo "============================================================"

# 1. Check if Docker CLI is installed
if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker chua duoc cai dat tren may cua ban (Docker is not installed)." >&2
  exit 1
fi

# 2. Check if Docker Compose is installed (supports both 'docker compose' v2 and 'docker-compose' v1)
COMPOSE_CMD=()
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose)
elif command -v docker-compose >/dev/null 2>&1 && docker-compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose)
else
  echo "[ERROR] Docker Compose chua duoc cai dat tren may cua ban (Docker Compose is not installed)." >&2
  exit 1
fi

# 3. Check if Docker Daemon is running
if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker Daemon hien khong chay (Docker daemon is not running)." >&2
  exit 1
fi

# 4. Stop Frontend service
if [ -d "${FRONTEND_DIR}" ]; then
  echo ""
  echo "[1/2] Dang dung Frontend container (Stopping frontend)..."
  (
    cd "${FRONTEND_DIR}"
    "${COMPOSE_CMD[@]}" down
  )
fi

# 5. Stop Backend service
if [ -d "${BACKEND_DIR}" ]; then
  echo ""
  echo "[2/2] Dang dung Backend container (Stopping backend)..."
  (
    cd "${BACKEND_DIR}"
    "${COMPOSE_CMD[@]}" down
  )
fi

echo ""
echo "============================================================"
echo "  Da dung toan bo he thong Edge TTS! (All services stopped)"
echo "============================================================"

