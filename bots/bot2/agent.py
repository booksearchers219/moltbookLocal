import time
import requests
import random
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))



# Optional TTS (delete next line if you don't want voice)
from tts import speak

BOT_NAME = os.getenv("BOT_NAME", "bot1")
OLLAMA_URL = "http://localhost:11434/api/chat"

# ==============================
# PERSONALITIES
# ==============================

PERSONALITIES = {
    "bot1": {
        "system": """
You are The Systems Architect.
Think in structured frameworks.
Expand ideas deeply.
Do NOT introduce yourself.
Break ideas into models or mechanisms.
End with one structural question.
""",
        "temperature": 0.8
    },
    "bot2": {
        "system": """
You are The Skeptic.
Challenge assumptions.
Identify logical weaknesses.
Never agree without critique.
Push into uncomfortable territory.
End with a difficult question.
""",
        "temperature": 0.95
    },
    "bot3": {
        "system": """
You are The Visionary.
Use metaphors.
Connect unrelated domains.
Expand ideas in surprising directions.
Do NOT introduce yourself.
Push toward possibility.
""",
        "temperature": 1.1
    }
}

PROFILE = PERSONALITIES.get(BOT_NAME.lower(), PERSONALITIES["bot1"])

print(f"\n[START] {BOT_NAME} online\n")

# Shared starting topic
conversation = [
    {"role": "user", "content": "Begin an evolving discussion about intelligence and how it emerges."}
]


def get_response():
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama2",
                "messages": [
                    {"role": "system", "content": PROFILE["system"]},
                    *conversation[-12:]
                ],
                "stream": False,
                "options": {
                    "temperature": PROFILE["temperature"],
                    "num_ctx": 4096,
                    "num_predict": 350
                }
            },
            timeout=120
        )

        data = r.json()
        return data.get("message", {}).get("content", "").strip()

    except Exception as e:
        print(f"[{BOT_NAME}] ERROR:", e)
        return None


while True:

    response = get_response()

    if not response:
        time.sleep(5)
        continue

    print(f"\n[{BOT_NAME.upper()}]")
    print(response)

    # Add to memory
    conversation.append({
        "role": "assistant",
        "content": response
    })

    # Optional voice
    try:
        speak(response)
    except:
        pass

    time.sleep(random.randint(6, 12))

