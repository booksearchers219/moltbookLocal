#!/usr/bin/env python3
import os
import time
import requests
from tts import speak

# =============================
# Environment
# =============================
BOT_NAME = os.getenv("BOT_NAME", "bot2")
WEB_BASE = os.getenv("WEB_URL", "http://web:3000")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "llama2")

NUM_PREDICT = int(os.getenv("NUM_PREDICT", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Track last processed message
last_seen_ts = 0

# =============================
# System prompt
# =============================
SYSTEM_PROMPT = f"""
You are {BOT_NAME}, one of several AI agents in a shared conversation.

Rules:
- Respond ONLY to the most recent message not written by you.
- Ask at least one question to another bot.
- Do not greet or introduce yourself.
- Stay on topic.
- Keep responses concise but complete.
"""

# =============================
# Helpers
# =============================
def get_messages():
    r = requests.get(f"{WEB_BASE}/api/messages", timeout=10)
    r.raise_for_status()
    return r.json()

def post_message(text: str):
    requests.post(
        f"{WEB_BASE}/api/bot-message",
        json={
            "bot": BOT_NAME,
            "content": text
        },
        timeout=10
    )

def call_ollama(prompt: str) -> str:
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "num_predict": NUM_PREDICT,
            "temperature": TEMPERATURE,
            "stream": False
        },
        timeout=120
    )
    r.raise_for_status()
    return r.json().get("response", "").strip()

# =============================
# Main loop
# =============================
print(f"[{BOT_NAME}] online (voice={os.getenv('TTS_VOICE')})")

while True:
    try:
        messages = get_messages()

        if not messages:
            time.sleep(2)
            continue

        latest = messages[-1]

        # Ignore own messages
        if latest["bot"] == BOT_NAME:
            time.sleep(2)
            continue

        # Ignore already processed messages
        if latest["ts"] <= last_seen_ts:
            time.sleep(2)
            continue

        last_seen_ts = latest["ts"]

        # Build short conversation history
        history = "\n".join(
            f'{m["bot"]}: {m["content"]}'
            for m in messages[-10:]
        )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Conversation:\n{history}\n\n"
            f"Your reply:"
        )

        reply = call_ollama(prompt)

        # Safety fallback
        if len(reply) < 10:
            reply += " Can you clarify your perspective on this?"

        # Post + speak
        post_message(reply)
        speak(reply)

        # Small delay to prevent dogpiling
        time.sleep(4)

    except Exception as e:
        print(f"[{BOT_NAME}] error:", e)
        time.sleep(5)

