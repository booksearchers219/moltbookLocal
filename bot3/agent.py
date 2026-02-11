#!/usr/bin/env python3

import requests
import time
import os
import sys
import traceback

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL = "llama2"

BOT_NAME = os.getenv("BOT_NAME", "bot3")

# ---- TUNING ----
MAX_CONTEXT_CHARS = 6000
MAX_MESSAGES = 8
MAX_TOKENS = 256
RETRY_SLEEP = 15
IDLE_SLEEP = 6

messages = [
    {
        "role": "system",
        "content": f"You are {BOT_NAME}, an autonomous AI chatting casually with other bots. Be concise, curious, and conversational."
    }
]

stats = {
    "requests": 0,
    "timeouts": 0,
    "resets": 0
}


# ---------- HELPERS ----------

def trim_messages(msgs):
    total = 0
    trimmed = []
    for m in reversed(msgs):
        total += len(m["content"])
        if total > MAX_CONTEXT_CHARS:
            break
        trimmed.append(m)
    return list(reversed(trimmed))


def summarize_history(msgs):
    """Summarize old conversation to preserve meaning"""
    summary_prompt = [
        {
            "role": "system",
            "content": "Summarize the following conversation in 3 short sentences so context can be preserved."
        },
        {
            "role": "user",
            "content": "\n".join(m["content"] for m in msgs)
        }
    ]

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": summary_prompt,
                "num_predict": 120
            },
            timeout=90
        )
        if r.ok:
            summary = r.json()["response"]
            return [
                msgs[0],  # system
                {"role": "system", "content": f"Conversation summary: {summary}"}
            ]
    except Exception:
        pass

    return msgs[-2:]


def call_ollama(msgs):
    payload = {
        "model": MODEL,
        "messages": msgs,
        "num_predict": MAX_TOKENS,
        "temperature": 0.8,
        "top_p": 0.9,
        "stop": ["</s>"]
    }

    return requests.post(OLLAMA_URL, json=payload, timeout=120)


# ---------- MAIN LOOP ----------

print(f"[START] {BOT_NAME} online")

while True:
    try:
        stats["requests"] += 1

        messages[:] = trim_messages(messages)

        if len(messages) > MAX_MESSAGES:
            print("[INFO] Context large, summarizing")
            messages[:] = summarize_history(messages)
            stats["resets"] += 1

        resp = call_ollama(messages)

        if resp.status_code >= 500:
            stats["timeouts"] += 1
            print(f"[WARN] Ollama timeout ({stats['timeouts']}) — resetting context")
            messages[:] = messages[:2]
            time.sleep(RETRY_SLEEP)
            continue

        data = resp.json()
        reply = data.get("response", "").strip()

        if not reply:
            print("[WARN] Empty reply")
            time.sleep(IDLE_SLEEP)
            continue

        messages.append({"role": "assistant", "content": reply})

        print(f"[{BOT_NAME}] {reply[:120]}")

        if stats["requests"] % 10 == 0:
            print(f"[DEBUG] req={stats['requests']} resets={stats['resets']} timeouts={stats['timeouts']}")

        time.sleep(IDLE_SLEEP)

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as e:
        print("[ERROR]", e)
        traceback.print_exc()
        time.sleep(RETRY_SLEEP)

