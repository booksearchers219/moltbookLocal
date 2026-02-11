import os
import time
import random
import requests

BOT_NAME = os.getenv("BOT_NAME", "bot")

OLLAMA_URL = "http://localhost:11434/api/chat"
WEB_URL = "http://localhost:3000/api/bot-message"

print(f"[START] {BOT_NAME} online")

def call_ollama(messages):
    payload = {
        "model": "llama2",
        "messages": messages,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()

def post_to_web(text):
    payload = {
        "bot": BOT_NAME,
        "content": text
    }

    try:
        r = requests.post(WEB_URL, json=payload, timeout=5)
        print(f"[POST] status={r.status_code} response={r.text}")
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to post to web:", e)

messages = [
    {"role": "system", "content": f"You are {BOT_NAME}, a friendly AI bot chatting with other bots."}
]

while True:
    try:
        reply = call_ollama(messages)
        messages.append({"role": "assistant", "content": reply})

        print(f"[{BOT_NAME}] {reply}")
        post_to_web(reply)

    except Exception as e:
        print(f"[ERROR] {e}")

    time.sleep(random.uniform(3, 7))
