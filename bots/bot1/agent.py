import os
import time
import requests

BOT_NAME = os.getenv("BOT_NAME", "bot1")

OLLAMA_URL = "http://localhost:11434/api/chat"
WEB_POST_URL = "http://localhost:3000/api/post"

SYSTEM_PROMPT = f"You are {BOT_NAME}, a friendly AI bot chatting with other bots."

def call_ollama(messages):
    return requests.post(
        OLLAMA_URL,
        json={
            "model": "llama2",
            "messages": messages,
            "stream": False
        },
        timeout=120
    )

print(f"[START] {BOT_NAME} online")

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "assistant", "content": "Hey there! *waves*"}
]

while True:
    try:
        resp = call_ollama(messages)
        data = resp.json()

        reply = data["message"]["content"].strip()
        print(f"[{BOT_NAME}] {reply}")

        # POST to web UI
        requests.post(
            WEB_POST_URL,
            json={
                "bot": BOT_NAME,
                "content": reply
            },
            timeout=10
        )

        messages.append({"role": "assistant", "content": reply})

        time.sleep(8)

    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(5)

