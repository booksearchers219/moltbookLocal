import os
import time
import requests
import random
import subprocess
from datetime import datetime

BOT_NAME = os.getenv("BOT_NAME", "bot")

OLLAMA_URL = "http://localhost:11434/api/chat"
WEB_URL = "http://localhost:3000/api/bot-message"

AUDIO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../audio"))

os.makedirs(AUDIO_DIR, exist_ok=True)

print(f"[START] {BOT_NAME} online")


# -----------------------------
# OLLAMA CALL (HARDENED)
# -----------------------------
def get_response(prompt):
    for attempt in range(2):  # retry once
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": "llama2",
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "num_ctx": 2048,
                        "num_predict": 150
                    }
                },
                timeout=120
            )

            data = r.json()
            content = data.get("message", {}).get("content", "").strip()

            if content:
                return content

            print(f"[{BOT_NAME}] [WARN] Empty response (attempt {attempt+1})")

        except Exception as e:
            print(f"[{BOT_NAME}] [ERROR] Ollama failed: {e}")

        time.sleep(2)

    return None


# -----------------------------
# AUDIO GENERATION
# -----------------------------
def generate_audio(text):
    if not text.strip():
        return None

    filename = f"{BOT_NAME}_{int(time.time())}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    try:
        subprocess.run(
            ["espeak", "-w", filepath, text],
            check=True
        )
        print(f"[{BOT_NAME}] [AUDIO] generated {filename}")
        return filename
    except Exception as e:
        print(f"[{BOT_NAME}] [ERROR] Audio generation failed: {e}")
        return None


# -----------------------------
# POST TO WEB
# -----------------------------
def post_to_web(text, wav_filename):
    try:
        requests.post(
            WEB_URL,
            json={
                "bot": BOT_NAME,
                "content": text,
                "audio": wav_filename
            },
            timeout=10
        )
        print(f"[{BOT_NAME}] [POSTED]")
    except Exception as e:
        print(f"[{BOT_NAME}] [ERROR] Failed to post: {e}")


# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    prompt = "Say something friendly and conversational."

    response = get_response(prompt)

    if not response:
        print(f"[{BOT_NAME}] [SKIP] No valid response")
        time.sleep(5)
        continue

    print(f"[{BOT_NAME}] {response}")

    wav = generate_audio(response)

    if wav:
        post_to_web(response, wav)

    sleep_time = random.randint(6, 12)
    print(f"[{BOT_NAME}] [SLEEP] {sleep_time}s")
    time.sleep(sleep_time)

