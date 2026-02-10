FROM python:3.11-slim

# -----------------------------
# System dependencies (single cached layer)
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    pulseaudio-utils \
    alsa-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Python dependencies
# -----------------------------
RUN pip install --no-cache-dir requests

# -----------------------------
# App setup
# -----------------------------
WORKDIR /app

COPY agent.py tts.py ./

# -----------------------------
# Run the agent
# -----------------------------
CMD ["python", "agent.py"]

