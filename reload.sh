#!/usr/bin/env bash

set -e

echo "🧹 Full rebuild (no cache)"

docker compose down --remove-orphans
docker compose build --no-cache
docker compose up -d
docker compose ps

echo "✅ Full rebuild complete"

