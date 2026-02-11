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
  pkill -f agent.py || true
  pkill -f server.js || true
  exit 0
}
trap cleanup SIGINT SIGTERM

# --- Ollama ---
if ! pgrep -x ollama >/dev/null; then
  echo "🧠 Starting Ollama..."
  ollama serve > >(sed 's/^/[OLLAMA] /') 2>&1 &
  sleep 2
else
  echo "🧠 Ollama already running"
fi

# --- Web server ---
echo "🌐 Starting web server (server.js)..."
cd "$WEB_DIR"
node server.js > >(sed 's/^/[WEB] /') 2>&1 &
sleep 1

# --- Bots ---
start_bot () {
  local BOT_NAME="$1"
  echo "🤖 Starting $BOT_NAME..."
  cd "$BOTS_DIR/$BOT_NAME"
  BOT_NAME="$BOT_NAME" python3 agent.py \
    > >(sed "s/^/[$BOT_NAME] /") 2>&1 &
}

start_bot bot1
start_bot bot2
start_bot bot3

echo
echo "✅ Moltbook is running"
echo "   Web: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop everything"
echo

wait

