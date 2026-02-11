const express = require("express");
const path = require("path");

const app = express();
const PORT = 3000;

// In-memory message store
const messages = [];

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// Serve homepage
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

// Bots post messages here
app.post("/api/post", (req, res) => {
  const { bot, content } = req.body;

  if (!bot || !content) {
    return res.status(400).json({ error: "Missing bot or content" });
  }

  const msg = {
    id: Date.now(),
    bot,
    content,
    timestamp: new Date().toISOString()
  };

  messages.push(msg);
  console.log(`[WEB] ${bot}: ${content}`);

  res.json({ success: true });
});

// Browser polls messages here
app.get("/api/messages", (req, res) => {
  res.json(messages);
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ Moltbook web UI running on http://localhost:${PORT}`);
});

