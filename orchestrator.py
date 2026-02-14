import requests
import time
import random
from tts import speak

# -----------------------------
# CONFIG
# -----------------------------

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
WEB_URL = "http://127.0.0.1:3000/api/bot-message"
MODEL = "phi"   # much faster than llama2

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

# -----------------------------
# SHARED MEMORY
# -----------------------------

conversation = [
    {"role": "user", "content": "Begin an evolving discussion about intelligence and how it emerges."}
]

# -----------------------------
# CALL OLLAMA
# -----------------------------

def call_bot(bot):
    try:
        r = requests.post(
            OLLAMA_URL,
            json={
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
            },
            timeout=180
        )

        data = r.json()
        return data.get("message", {}).get("content", "").strip()

    except Exception as e:
        print("Ollama error:", e)
        return None


# -----------------------------
# MAIN LOOP
# -----------------------------

print("\n=== Multi-Agent Conversation Started ===\n")

turn = 0

while True:
    bot = BOTS[turn % len(BOTS)]

    print(f"\nCalling {bot['name']}...")

    response = call_bot(bot)

    if not response:
        time.sleep(3)
        continue

    print(f"\n[{bot['name']}]")
    print(response)

    conversation.append({
        "role": "assistant",
        "content": response
    })

    # Speak
    speak(response, bot["name"])

   
    turn += 1
    time.sleep(random.randint(4, 8))

