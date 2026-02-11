import os
import sys
import subprocess

# =============================
# Voice tuning presets
# =============================
VOICE_PRESETS = {
    "en+robot": {
        "speed": "135",
        "pitch": "35"
    },
    "en+m1": {
        "speed": "160",
        "pitch": "50"
    },
    "en+m3": {
        "speed": "150",
        "pitch": "45"
    },
    "en+f2": {
        "speed": "175",
        "pitch": "65"
    }
}

# =============================
# ENV overrides (per bot)
# =============================
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en+m1")
DEFAULT_RATE  = os.getenv("TTS_RATE")
DEFAULT_PITCH = os.getenv("TTS_PITCH")

# =============================
# Library API (used by agent.py)
# =============================
def speak(text: str, voice: str | None = None):
    if not text:
        return

    voice = voice or DEFAULT_VOICE
    preset = VOICE_PRESETS.get(voice, {"speed": "150", "pitch": "50"})

    speed = DEFAULT_RATE or preset["speed"]
    pitch = DEFAULT_PITCH or preset["pitch"]

    safe = text.replace("\n", " ").strip()

    cmd = [
        "espeak-ng",
        "-v", voice,
        "-s", speed,
        "-p", pitch,
        safe
    ]

    # Non-blocking playback
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# =============================
# CLI MODE (backward compatible)
# =============================
def main():
    if len(sys.argv) < 3:
        print("Usage: tts.py <text> <outfile> [voice]", file=sys.stderr)
        sys.exit(1)

    text = sys.argv[1]
    outfile = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) >= 4 else DEFAULT_VOICE

    preset = VOICE_PRESETS.get(voice, {"speed": "150", "pitch": "50"})
    speed = DEFAULT_RATE or preset["speed"]
    pitch = DEFAULT_PITCH or preset["pitch"]

    cmd = [
        "espeak-ng",
        "-v", voice,
        "-s", speed,
        "-p", pitch,
        "-w", outfile,
        text
    ]

    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    main()

