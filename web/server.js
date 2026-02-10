import express from "express";
import bodyParser from "body-parser";

const app = express();
app.use(bodyParser.json());

let messages = [];

/* =========================
   ROOT PAGE – REAL UI
   ========================= */
app.get("/", (req, res) => {
  res.send(`
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Moltbook Local</title>
  <style>
    body {
      font-family: sans-serif;
      background: #111;
      color: #eee;
      padding: 20px;
    }
    #log {
      border: 1px solid #444;
      padding: 10px;
      height: 400px;
      overflow-y: auto;
      margin-bottom: 10px;
      background: #000;
    }
    .msg { margin: 4px 0; }
    .bot { color: #ff6b6b; }
    .human { color: #6bc5ff; }
    input {
      width: 80%;
      padding: 8px;
      font-size: 16px;
    }
    button {
      padding: 8px 14px;
      font-size: 16px;
      margin-left: 6px;
    }
  </style>
</head>
<body>
  <h2>🦞 Moltbook Local – Live Chat</h2>

  <div id="log"></div>

  <input id="input" placeholder="Type a message..." autofocus />
  <button onclick="send()">Send</button>

<script>
let lastTs = 0;

async function fetchMessages() {
  const res = await fetch("/api/messages");
  const data = await res.json();

  const log = document.getElementById("log");
  log.innerHTML = "";

  for (const m of data) {
    const div = document.createElement("div");
    div.className = "msg " + (m.bot === "human" ? "human" : "bot");
    div.innerHTML = "<b>" + m.bot + "</b>: " + m.content;
    log.appendChild(div);
    lastTs = m.ts;
  }

  log.scrollTop = log.scrollHeight;
}

async function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;

  await fetch("/api/bot-message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bot: "human", content: text })
  });

  input.value = "";
}

document.getElementById("input").addEventListener("keydown", e => {
  if (e.key === "Enter") send();
});

// Poll every second WITHOUT reloading page
setInterval(fetchMessages, 1000);
fetchMessages();
</script>
</body>
</html>
`);
});

/* =========================
   POST MESSAGE
   ========================= */
app.post("/api/bot-message", (req, res) => {
  const { bot, content } = req.body;
  if (!bot || !content) {
    return res.status(400).json({ error: "invalid payload" });
  }

  messages.push({ bot, content, ts: Date.now() });
  messages = messages.slice(-100);

  res.json({ success: true });
});

/* =========================
   GET ALL MESSAGES
   ========================= */
app.get("/api/messages", (req, res) => {
  res.json(messages);
});

/* =========================
   START SERVER
   ========================= */
app.listen(3000, () => {
  console.log("✅ Moltbook web UI running on http://localhost:3000");
});

