import os
import sys
import time
import json
import random
import subprocess
import requests

# --- config ---
BOT_NAME = os.getenv("BOT_NAME", "bot1")
MODEL = "llama2"
OLLAMA_URL = "http://localhost:11434/api/chat"
WEB_URL = "http://localhost:3000/api/bot-message"
AUDIO_DIR = os.path.expanduser("~/moltbook-local/audio")

os.makedirs(AUDIO_DIR, exist_ok=True)
sys.stdout.reconfigure(line_buffering=True)

def log(msg):
    print(msg, flush=True)

# --- Safe Ollama Call ---
def call_ollama(messages, retries=2):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 2048
        }
    }

    for attempt in range(retries + 1):
        try:
            r = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=300
            )
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"].strip()

        except requests.exceptions.Timeout:
            log(f"[WARN] Ollama timeout (attempt {attempt+1})")

        except Exception as e:
            log(f"[WARN] Ollama error: {e}")

        if attempt < retries:
            sleep_time = 10 + random.randint(0, 5)
            log(f"[BACKOFF] Sleeping {sleep_time}s")
            time.sleep(sleep_time)

    log("[ERROR] Ollama failed after retries.")
    return ""

# --- Audio ---
def speak(text):
    if not text:
        return None

    ts = int(time.time())
    filename = f"{BOT_NAME}_{ts}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    cmd = ["espeak", "-w", filepath, text]

    try:
        subprocess.run(cmd, check=True)
        log(f"[AUDIO] generated {filename}")
        return filename
    except Exception as e:
        log(f"[AUDIO ERROR] {e}")
        return None

# --- Send to Web ---
def post_to_web(text, audio_file):
    payload = {
        "bot": BOT_NAME,
        "content": text,
        "audio": audio_file
    }

    try:
        requests.post(WEB_URL, json=payload, timeout=10)
    except Exception as e:
        log(f"[WEB ERROR] {e}")

# --- main loop ---
log(f"[START] {BOT_NAME} online")

messages = [
    {"role": "system", "content": f"You are {BOT_NAME}, a friendly AI bot."}
]

MAX_HISTORY = 6  # prevents runaway memory/context growth

while True:
    try:
        reply = call_ollama(messages)

        if not reply:
            log("[SKIP] Empty reply, cooling down.")
            time.sleep(8)
            continue

        messages.append({"role": "assistant", "content": reply})

        # --- Trim history ---
        if len(messages) > MAX_HISTORY:
            messages = [messages[0]] + messages[-(MAX_HISTORY-1):]

        log(f"[{BOT_NAME}] {reply}")

        audio = speak(reply)
        post_to_web(reply, audio)

        # --- Stagger sleep to prevent collisions ---
        sleep_time = random.randint(6, 12)
        log(f"[SLEEP] {sleep_time}s")
        time.sleep(sleep_time)

    except KeyboardInterrupt:
        log("[STOP] shutting down")
        break

    except requests.exceptions.Timeout:
        log("[WARN] Timeout — backing off 15s")
        time.sleep(15)

    except Exception as e:
        log(f"[ERROR] {e}")
        time.sleep(10)

