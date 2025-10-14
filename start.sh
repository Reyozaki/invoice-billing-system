#!/usr/bin/env bash
set -euo pipefail

# --- 🧹 Fix Windows-style line endings automatically ---
if grep -q $'\r' "$0"; then
  echo "⚙️  Fixing Windows-style line endings in $0 ..."
  tmpfile=$(mktemp)
  tr -d '\r' <"$0" >"$tmpfile"
  mv "$tmpfile" "$0"
  chmod +x "$0"
  exec "$0" "$@" # Restart cleanly after fixing
fi

COMPOSE_FILE="docker/docker-compose.yaml"

# --- 🌱 Load .env variables if present ---
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# --- 🧩 Helper functions ---
info() { echo -e "🔹 \033[1;34m$1\033[0m"; }
success() { echo -e "✅ \033[1;32m$1\033[0m"; }
warn() { echo -e "⚠️  \033[1;33m$1\033[0m"; }
error() {
  echo -e "❌ \033[1;31m$1\033[0m" >&2
  exit 1
}

# --- 🧰 Pre-flight checks ---
command -v docker >/dev/null 2>&1 || error "Docker is not installed or not in PATH."
command -v docker-compose >/dev/null 2>&1 || error "docker-compose not found. Install Docker Compose v2+."
command -v uvicorn >/dev/null 2>&1 || error "Uvicorn not found. Install it with: pip install uvicorn"

# --- 🚀 Start containers ---
info "Starting Docker containers..."
docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans

# --- 🧹 Ensure cleanup on exit ---
cleanup() {
  info "Stopping Docker containers..."
  docker-compose -f "$COMPOSE_FILE" down
}
trap cleanup EXIT

# --- 🐘 Detect PostgreSQL container ---
DB_CONTAINER_NAME=$(docker-compose -f "$COMPOSE_FILE" ps -q postgres | xargs -r docker inspect --format '{{.Name}}' | sed 's#^/##')
DB_USER=${POSTGRES_USER:-postgres}

if [ -z "$DB_CONTAINER_NAME" ]; then
  error "PostgreSQL container not found in docker-compose file."
fi
info "Detected PostgreSQL container: $DB_CONTAINER_NAME"

# --- ⏳ Wait for PostgreSQL readiness ---
info "Waiting for PostgreSQL to be ready..."
if docker inspect "$DB_CONTAINER_NAME" --format '{{.State.Health}}' >/dev/null 2>&1; then
  until [ "$(docker inspect -f '{{.State.Health.Status}}' "$DB_CONTAINER_NAME")" == "healthy" ]; do
    echo "⏳ Waiting for PostgreSQL health check..."
    sleep 2
  done
else
  until docker exec "$DB_CONTAINER_NAME" pg_isready -U "$DB_USER" >/dev/null 2>&1; do
    echo "⏳ Waiting for database to accept connections..."
    sleep 2
  done
fi
success "PostgreSQL is ready! 🎉"

# --- 🌐 Start FastAPI Server ---
APP_MODULE=${APP_MODULE:-app.main:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

info "Starting FastAPI server with Uvicorn..."
uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --reload
