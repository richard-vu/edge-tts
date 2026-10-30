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
echo "  Edge TTS - Startup Script (OS: ${OS_NAME})"
echo "============================================================"

# 1. Check if Docker CLI is installed
if ! command -v docker >/dev/null 2>&1; then
  echo "[ERROR] Docker chua duoc cai dat tren may cua ban (Docker is not installed)." >&2
  echo "Vui long cai dat Docker truoc khi chay ung dung:" >&2
  echo "  - Windows / macOS: https://www.docker.com/products/docker-desktop/" >&2
  echo "  - Linux:           https://docs.docker.com/engine/install/" >&2
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
  echo "Vui long cai dat Docker Compose plugin hoac Docker Desktop:" >&2
  echo "  - Huong dan: https://docs.docker.com/compose/install/" >&2
  exit 1
fi

# 3. Check if Docker Daemon is running
if ! docker info >/dev/null 2>&1; then
  echo "[ERROR] Docker da duoc cai dat nhung Docker Daemon chua chay (Docker daemon is not running)." >&2
  echo "Vui long mo Docker Desktop (Windows/macOS) hoac khoi dong dich vu Docker (Linux: sudo systemctl start docker)." >&2
  exit 1
fi

echo "[INFO] Detected Docker: $(docker --version)"
echo "[INFO] Detected Compose: $("${COMPOSE_CMD[@]}" version --short 2>/dev/null || "${COMPOSE_CMD[@]}" version)"

# 4. Validate required directories and .env.pro files
if [ ! -d "${BACKEND_DIR}" ]; then
  echo "[ERROR] Khong tim thay thu muc backend tai: ${BACKEND_DIR}" >&2
  exit 1
fi

if [ ! -d "${FRONTEND_DIR}" ]; then
  echo "[ERROR] Khong tim thay thu muc frontend tai: ${FRONTEND_DIR}" >&2
  exit 1
fi

if [ ! -f "${BACKEND_DIR}/.env.pro" ]; then
  echo "[ERROR] Thieu file cau hinh bat buoc: ${BACKEND_DIR}/.env.pro" >&2
  exit 1
fi

if [ ! -f "${FRONTEND_DIR}/.env.pro" ]; then
  echo "[ERROR] Thieu file cau hinh bat buoc: ${FRONTEND_DIR}/.env.pro" >&2
  exit 1
fi

# Ensure backend/data directory exists with current user ownership before mounting volume
mkdir -p "${BACKEND_DIR}/data"

# 5. Start Backend service
echo ""
echo "[1/2] Dang khoi dong Backend (Building & starting backend container)..."
(
  cd "${BACKEND_DIR}"
  "${COMPOSE_CMD[@]}" up -d --build
)

# 6. Start Frontend service
echo ""
echo "[2/2] Dang khoi dong Frontend (Building & starting frontend container)..."
(
  cd "${FRONTEND_DIR}"
  "${COMPOSE_CMD[@]}" up -d --build
)

echo ""
echo "============================================================"
echo "  Khoi dong thanh cong! (All services are up and running)"
echo "  - Frontend UI:      http://localhost:9101"
echo "  - Backend API Docs: http://localhost:9100/docs"
echo "============================================================"

