FROM node:20-slim

# -----------------------------
# System dependencies (TTS)
# -----------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    pulseaudio-utils \
    alsa-utils \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# App setup
# -----------------------------
WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]

