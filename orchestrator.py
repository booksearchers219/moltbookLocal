#!/usr/bin/env python3
import requests
import time
import random
from tts import speak

# -----------------------------
# CONFIG
# -----------------------------

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "phi"

REQUEST_TIMEOUT = 60
MAX_RETRIES = 2
FAILURE_SKIP_THRESHOLD = 3

# -----------------------------
# PERSONALITIES
# -----------------------------

BOTS = [
    {
        "name": "SystemsArchitect",
        "system": """
You are The Systems Architect.
Build structured models.
Expand deeply.
Do not introduce yourself.
End with one structural question.
""",
        "temperature": 0.8
    },
    {
        "name": "Skeptic",
        "system": """
You are The Skeptic.
Challenge assumptions.
Expose weaknesses.
Never agree without critique.
End with a difficult question.
""",
        "temperature": 0.95
    },
    {
        "name": "Visionary",
        "system": """
You are The Visionary.
Use metaphors.
Connect unrelated domains.
Expand ideas in surprising directions.
Do not introduce yourself.
""",
        "temperature": 1.1
    }
]

# Track consecutive failures per bot
bot_failures = {bot["name"]: 0 for bot in BOTS}

# -----------------------------
# SHARED MEMORY
# -----------------------------

conversation = [
    {"role": "user", "content": "Begin an evolving discussion about intelligence and how it emerges."}
]

# -----------------------------
# SAFE OLLAMA CALL
# -----------------------------

def call_bot(bot):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": bot["system"]},
            *conversation[-4:]
        ],
        "stream": False,
        "options": {
            "temperature": bot["temperature"],
            "num_ctx": 1024,
            "num_predict": 80
        }
    }

    for attempt in range(MAX_RETRIES):
        try:
            print(f"🧠 Attempt {attempt + 1} for {bot['name']}...")

            r = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )

            r.raise_for_status()

            data = r.json()

            if not isinstance(data, dict):
                print("⚠️ Invalid JSON structure.")
                continue

            content = data.get("message", {}).get("content", "")

            if not isinstance(content, str):
                continue

            content = content.strip()

            if not content:
                continue

            return content

        except requests.exceptions.Timeout:
            print("⚠️ Ollama timed out.")
        except requests.exceptions.ConnectionError:
            print("⚠️ Cannot connect to Ollama.")
        except Exception as e:
            print("⚠️ Ollama error:", e)

        time.sleep(1)

    return None


# -----------------------------
# MAIN LOOP
# -----------------------------

print("\n=== Multi-Agent Conversation Started ===\n")

turn = 0

while True:
    bot = BOTS[turn % len(BOTS)]

    # Skip bot if it's failing repeatedly
    if bot_failures[bot["name"]] >= FAILURE_SKIP_THRESHOLD:
        print(f"⏭ Skipping {bot['name']} due to repeated failures.")
        turn += 1
        continue

    print(f"\nCalling {bot['name']}...")

    response = call_bot(bot)

    if not response:
        bot_failures[bot["name"]] += 1
        print(f"⚠️ {bot['name']} failed ({bot_failures[bot['name']]} consecutive).")
        turn += 1
        time.sleep(2)
        continue

    # Reset failure counter on success
    bot_failures[bot["name"]] = 0

    print(f"\n[{bot['name']}]")
    print(response)

    conversation.append({
        "role": "assistant",
        "content": response
    })

    # Safe TTS
    try:
        speak(response, bot["name"])
    except Exception as e:
        print("⚠️ TTS error:", e)

    turn += 1
    time.sleep(random.randint(4, 8))

