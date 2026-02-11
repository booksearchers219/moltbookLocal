// Moltbook browser message + audio handler

const VOICES = {
  bot1: { rate: 1.0, pitch: 1.0 },
  bot2: { rate: 1.15, pitch: 1.3 },
  bot3: { rate: 0.9, pitch: 0.8 }
};

let lastSeen = 0;

function speak(bot, text) {
  if (!("speechSynthesis" in window)) return;

  const u = new SpeechSynthesisUtterance(text);
  const v = VOICES[bot] || {};

  u.rate = v.rate || 1;
  u.pitch = v.pitch || 1;

  window.speechSynthesis.speak(u);
}

async function poll() {
  try {
    const res = await fetch("/api/messages");
    const msgs = await res.json();

    msgs.forEach(m => {
      if (m.id <= lastSeen) return;

      lastSeen = m.id;

      const box = document.getElementById("messages");
      if (box) {
        const div = document.createElement("div");
        div.textContent = `[${m.bot}] ${m.content}`;
        box.appendChild(div);
      }

      speak(m.bot, m.content);
    });
  } catch (e) {
    console.error("poll error", e);
  }
}

setInterval(poll, 2000);

