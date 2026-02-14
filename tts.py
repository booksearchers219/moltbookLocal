import subprocess

VOICE_MAP = {
    "SystemsArchitect": "en+m1",
    "Skeptic": "en+robot",
    "Visionary": "en+f2"
}

def speak(text, bot_name):
    voice = VOICE_MAP.get(bot_name, "en+m1")

    subprocess.run([
        "espeak-ng",
        "-v", voice,
        "-s", "160",
        "-p", "50",
        text
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )

