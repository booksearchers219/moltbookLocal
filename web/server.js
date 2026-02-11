const express = require("express");
const cors = require("cors");
const path = require("path");

const app = express();
const PORT = 3000;

let messages = [];

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

app.get("/api/messages", (req, res) => {
  res.json(messages);
});

app.post("/api/bot-message", (req, res) => {
  messages.push(req.body);
  res.json({ ok: true });
});

app.post("/api/user-message", (req, res) => {
  messages.push({ ...req.body, bot: "user" });
  res.json({ ok: true });
});

app.listen(PORT, () => {
  console.log(`✅ Web running at http://localhost:${PORT}`);
});
