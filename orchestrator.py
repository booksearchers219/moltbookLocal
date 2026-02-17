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
Respond in 4-6 concise sentences.
Build high-level conceptual models.
Do NOT create numbered lists.
Stay abstract and theoretical.
End with one sharp structural question.
""",
        "temperature": 0.75
    },
    {
        "name": "Skeptic",
        "system": """
You are The Skeptic.
Respond in 3-5 tight sentences.
Critique ideas conceptually.
Avoid formal puzzles or enumerated structures.
End with one difficult question.
""",
        "temperature": 0.9
    },
    {
        "name": "Visionary",
        "system": """
You are The Visionary.
Respond in 4-6 vivid sentences.
Use one metaphor at most.
Avoid rambling or rule-based constructions.
""",
        "temperature": 1.0
    }
]

bot_failures = {bot["name"]: 0 for bot in BOTS}

# -----------------------------
# SHARED MEMORY
# -----------------------------

conversation = [
    {"role": "user", "content": "Begin an evolving discussion about intelligence and how it emerges."}
]

theory_summary = ""

# -----------------------------
# FAILURE RESET
# -----------------------------

def reset_all_failures():
    print("🔄 Resetting failure counters for all bots.\n")
    for bot in bot_failures:
        bot_failures[bot] = 0


# -----------------------------
# SUMMARIZER
# -----------------------------

def update_summary():
    global theory_summary

    if len(conversation) < 6:
        return

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Summarize the evolving theory in 5 concise sentences."},
            *conversation[-6:]
        ],
        "stream": False,
        "options": {
            "num_ctx": 1024,
            "num_predict": 120
        }
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=30)
        data = r.json()
        summary = data.get("message", {}).get("content", "").strip()
        if summary:
            theory_summary = summary
    except:
        pass


# -----------------------------
# SAFE OLLAMA CALL
# -----------------------------

def call_bot(bot):
    messages = [
        {"role": "system", "content": bot["system"]}
    ]

    if theory_summary:
        messages.append({
            "role": "system",
            "content": f"Current evolving theory summary:\n{theory_summary}"
        })

    messages.extend(conversation[-3:])

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": bot["temperature"],
            "num_ctx": 2048,
            "num_predict": 140
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

            content = data.get("message", {}).get("content", "")
            content = content.strip()

            # -------------------------
            # Silence detection
            # -------------------------
            if content and len(content) > 5:
                if not content.endswith((".", "?", "!")):
                    content += "..."
                return content

            # Soft silence (not failure)
            return "__SILENCE__"

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

    # Skip if bot exceeded failure threshold
    if bot_failures[bot["name"]] >= FAILURE_SKIP_THRESHOLD:
        print(f"⏭ Skipping {bot['name']} due to repeated failures.")

        # If ALL bots are failing, reset
        if all(f >= FAILURE_SKIP_THRESHOLD for f in bot_failures.values()):
            reset_all_failures()
            print("🧠 System stabilized. Continuing discussion.\n")

        turn += 1
        continue

    print(f"\nCalling {bot['name']}...")

    response = call_bot(bot)

    # -------------------------
    # Silence handling
    # -------------------------
    if response == "__SILENCE__":
        print(f"⚠️ {bot['name']} returned silence. Nudging conversation.\n")
        conversation.append({
            "role": "assistant",
            "content": "Continue the discussion from a new conceptual angle."
        })
        turn += 1
        continue

    # -------------------------
    # True failure handling
    # -------------------------
    if not response:
        bot_failures[bot["name"]] += 1
        print(f"⚠️ {bot['name']} failed ({bot_failures[bot['name']]} consecutive).")
        turn += 1
        time.sleep(2)
        continue

    # Success
    bot_failures[bot["name"]] = 0

    print(f"\n[{bot['name']}]")
    print(response)

    conversation.append({
        "role": "assistant",
        "content": response
    })

    update_summary()

    try:
        speak(response, bot["name"])
    except Exception as e:
        print("⚠️ TTS error:", e)

    turn += 1
    time.sleep(random.randint(4, 8))

