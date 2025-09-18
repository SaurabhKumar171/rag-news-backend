import express from "express";
import bodyParser from "body-parser";
import cors from "cors";
import { spawn } from "child_process";
import { createClient } from "redis";

const app = express();
app.use(cors());
app.use(bodyParser.json());

// const redisClient = createClient();
// await redisClient.connect();
// Get Redis host from env, default to localhost
const redisHost = process.env.REDIS_HOST || "127.0.0.1";
// const redisClient = createClient({
//   socket: { host: redisHost, port: 6379 },
// });
const redisClient = createClient({ url: `redis://${redisHost}:6379` });

redisClient.connect();

const SESSION_TTL = 60 * 60 * 24; // 24 hours

// Helper to push messages to a Redis list
async function pushMessage(sessionId, message) {
  await redisClient.rPush(sessionId, JSON.stringify(message));
  await redisClient.expire(sessionId, SESSION_TTL); // refresh TTL
}

// Helper to get session history
async function getHistory(sessionId) {
  const items = await redisClient.lRange(sessionId, 0, -1);
  return items.map((item) => JSON.parse(item));
}

// POST /chat
app.post("/chat", async (req, res) => {
  const { sessionId, query } = req.body;

  // Call Python RAG pipeline (local)
  // const pythonBin = "../rag-news-ingestion/env/bin/python";
  // const process = spawn(pythonBin, [
  //   "../rag-news-ingestion/scripts/rag_chat_api.py",
  //   query,
  // ]);

  // Call Python RAG pipeline (docker)
  const pythonBin = "/opt/venv/bin/python";
  const process = spawn(pythonBin, [
    "/app/rag-news-ingestion/scripts/rag_chat_api.py",
    query,
  ]);

  let output = "";
  let error = "";

  process.stdout.on("data", (data) => {
    output += data.toString();
  });

  process.stderr.on("data", (data) => {
    error += data.toString();
  });

  process.on("close", async (code) => {
    if (code !== 0) {
      console.error("Python error:", error);
      const history = await getHistory(sessionId);
      return res.status(500).json({ error, history });
    }

    // Store messages in Redis list
    await pushMessage(sessionId, { role: "user", content: query });
    await pushMessage(sessionId, { role: "assistant", content: output.trim() });

    const history = await getHistory(sessionId);
    res.json({ answer: output.trim(), history });
  });
});

// GET /history/:sessionId
app.get("/history/:sessionId", async (req, res) => {
  const history = await getHistory(req.params.sessionId);
  res.json(history);
});

// DELETE /history/:sessionId
app.delete("/history/:sessionId", async (req, res) => {
  await redisClient.del(req.params.sessionId);
  res.json({ success: true });
});

app.listen(5000, () =>
  console.log("✅ Server running on http://localhost:5000")
);
