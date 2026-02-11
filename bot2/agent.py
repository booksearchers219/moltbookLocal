#!/usr/bin/env python3

import requests
import time
import os
import sys
import traceback

OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
WEB_URL = "http://moltbook-web:3000/api/bot-message"
MODEL = "llama2"

BOT_NAME = os.getenv("BOT_NAME", "bot2")
IDLE_SLEEP = 6

messages = [
    {
        "role": "system",
        "content": (
            f"You are {BOT_NAME}, an autonomous AI bot. "
            "You casually chat with other bots."
        )
    },
    {
        "role": "user",
        "content": "Start the conversation with an interesting question."
    }
]


def call_ollama(msgs):
    return requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": msgs,
            "stream": False,
            "options": {
                "num_predict": 256,
                "temperature": 0.8,
                "top_p": 0.9
            }
        },
        timeout=180
    )


def post_to_web(bot, text):
    try:
        requests.post(
            WEB_URL,
            json={
                "bot": bot,
                "role": "assistant",
                "content": text
            },
            timeout=5
        )
    except Exception as e:
        print(f"[WARN] Failed to post to web: {e}")


print(f"[START] {BOT_NAME} online")
sys.stdout.flush()

while True:
    try:
        resp = call_ollama(messages)
        resp.raise_for_status()

        reply = resp.json()["message"]["content"].strip()

        # Console output
        print(f"[{BOT_NAME}] {reply}")
        sys.stdout.flush()

        # 🔥 SEND TO WEB UI
        post_to_web(BOT_NAME, reply)

        messages.append({"role": "assistant", "content": reply})
        messages.append({
            "role": "user",
            "content": "Reply naturally and continue."
        })

        time.sleep(IDLE_SLEEP)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:
        traceback.print_exc()
        time.sleep(10)

