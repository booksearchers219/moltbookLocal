#!/usr/bin/env bash
set -e

BASE_DIR="$HOME/moltbook-local"
WEB_DIR="$BASE_DIR/web"
BOTS_DIR="$BASE_DIR/bots"

echo "🚀 Starting Moltbook Local (single terminal logs)"
echo

cleanup() {
  echo
  echo "🛑 Shutting down Moltbook..."
  pkill -f "agent.py" || true
  pkill -f "server.js" || true
  pkill -f "ollama serve" || true
  exit 0
}
trap cleanup SIGINT SIGTERM

# --- Ensure port 11434 is free ---
if lsof -i :11434 >/dev/null 2>&1; then
  echo "🛑 Port 11434 already in use. Killing existing process..."
  sudo fuser -k 11434/tcp || true
  sleep 1
fi

# --- Start Ollama ---
echo "🧠 Starting Ollama (single parallel mode)..."

export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE=5m

ollama serve > >(sed 's/^/[OLLAMA] /') 2>&1 &
sleep 3

# --- Start Web Server ---
echo "🌐 Starting web server (server.js)..."
cd "$WEB_DIR"
node server.js > >(sed 's/^/[WEB] /') 2>&1 &
sleep 2

# --- Start Bots (using per-bot directories) ---
echo "🤖 Starting bot1..."
BOT_NAME=bot1 python3 "$BOTS_DIR/bot1/agent.py" > >(sed 's/^/[bot1] /') 2>&1 &

echo "🤖 Starting bot2..."
BOT_NAME=bot2 python3 "$BOTS_DIR/bot2/agent.py" > >(sed 's/^/[bot2] /') 2>&1 &

echo "🤖 Starting bot3..."
BOT_NAME=bot3 python3 "$BOTS_DIR/bot3/agent.py" > >(sed 's/^/[bot3] /') 2>&1 &

echo
echo "✅ Moltbook is running"
echo "   Web: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop everything"

wait

