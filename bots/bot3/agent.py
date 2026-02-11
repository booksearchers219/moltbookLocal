import os
import sys
import time
import json
import subprocess
import requests

# --- config ---
BOT_NAME = os.getenv("BOT_NAME", "bot1")
OLLAMA_URL = "http://localhost:11434/api/chat"
WEB_URL = "http://localhost:3000/api/bot-message"
AUDIO_DIR = os.path.expanduser("~/moltbook-local/audio")

os.makedirs(AUDIO_DIR, exist_ok=True)
sys.stdout.reconfigure(line_buffering=True)

def log(msg):
    print(msg, flush=True)

def speak(text):
    ts = int(time.time())
    filename = f"{BOT_NAME}_{ts}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    cmd = [
        "espeak",
        "-w", filepath,
        text
    ]

    try:
        subprocess.run(cmd, check=True)
        log(f"[AUDIO] generated {filename}")
        return filename
    except Exception as e:
        log(f"[AUDIO ERROR] {e}")
        return None

def call_ollama(messages):
    payload = {
        "model": "llama2",
        "messages": messages,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()

def post_to_web(text, audio_file):
    payload = {
        "bot": BOT_NAME,
        "content": text,
        "audio": audio_file
    }

    try:
        requests.post(WEB_URL, json=payload, timeout=5)
    except Exception as e:
        log(f"[WEB ERROR] {e}")

# --- main loop ---
log(f"[START] {BOT_NAME} online")

messages = [
    {"role": "system", "content": f"You are {BOT_NAME}, a friendly AI bot."}
]

while True:
    try:
        reply = call_ollama(messages)
        messages.append({"role": "assistant", "content": reply})

        log(f"[{BOT_NAME}] {reply}")

        audio = speak(reply)
        post_to_web(reply, audio)

        time.sleep(5)

    except KeyboardInterrupt:
        log("[STOP] shutting down")
        break
    except Exception as e:
        log(f"[ERROR] {e}")
        time.sleep(5)

