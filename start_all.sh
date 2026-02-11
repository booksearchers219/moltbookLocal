#!/usr/bin/env bash

set -e

BASE="$HOME/moltbook-local"

echo "🚀 Starting Moltbook Local (single terminal logs)"
echo ""

PIDS=()

prefix () {
  local tag="$1"
  sed -u "s/^/[$tag] /"
}

# --- Start web server ---
echo "🌐 Starting web server..."
cd "$BASE/web"
node server.cjs 2>&1 | prefix WEB &
PIDS+=($!)

sleep 2

# --- Start bots ---
start_bot () {
  local name="$1"
  echo "🤖 Starting $name..."
  cd "$BASE/bots/$name"
  BOT_NAME="$name" python3 agent.py 2>&1 | prefix "$name" &
  PIDS+=($!)
}

start_bot bot1
start_bot bot2
start_bot bot3

# --- Open browser ---
sleep 1
xdg-open http://localhost:3000 >/dev/null 2>&1 || true

echo ""
echo "✅ Moltbook is running"
echo "   Web: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop everything"
echo ""

# --- Cleanup on Ctrl+C ---
cleanup () {
  echo ""
  echo "🧹 Shutting down..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
  exit 0
}

trap cleanup INT TERM

# Keep alive
wait

