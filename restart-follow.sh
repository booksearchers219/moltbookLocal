#!/usr/bin/env bash

set -e

echo "========================================"
echo "🔄 Restarting containers (attached mode)"
echo "📜 Logs will follow — Ctrl+C to stop"
echo "========================================"

docker compose down

# Start in FOREGROUND (no -d)
docker compose up

