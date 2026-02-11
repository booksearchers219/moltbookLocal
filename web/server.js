const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

/**
 * 🔴 CRITICAL FIX
 * Map /audio → ../audio
 */
const audioPath = path.resolve(__dirname, "..", "audio");
app.use("/audio", express.static(audioPath));

// in-memory message store
const messages = [];

// bots post here
app.post("/api/bot-message", (req, res) => {
  let { bot, content } = req.body;

  // 1️⃣ Accept audio from proper fields if present
  let audio =
    req.body.audio ||
    req.body.audio_file ||
    req.body.wav ||
    null;

  // 2️⃣ Fallback: extract .wav filename from content text
  if (!audio && typeof content === "string") {
    const match = content.match(/([a-zA-Z0-9_-]+\.wav)/);
    if (match) {
      audio = match[1];
      // remove filename from visible text
      content = content.replace(match[0], "").trim();
    }
  }

  messages.push({
    bot,
    content,
    audio,
    ts: Date.now()
  });

  console.log(
    `[WEB] ${bot}: ${content} : ${audio || "(no audio)"}`
  );

  res.json({ ok: true });
});

// user input
app.post("/api/user-message", (req, res) => {
  messages.push({ bot: "user", content: req.body.content, ts: Date.now() });
  res.json({ ok: true });
});

// frontend polls here
app.get("/api/messages", (req, res) => {
  res.json(messages.slice(-100));
});

// serve UI
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

// start server
app.listen(PORT, () => {
  console.log(`✅ Web server running at http://localhost:${PORT}`);
  console.log(`📂 Serving audio from: ${audioPath}`);
});

