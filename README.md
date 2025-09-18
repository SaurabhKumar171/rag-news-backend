# 📰 RAG News Chatbot – Developer Guide

A **Retrieval-Augmented Generation (RAG) chatbot** for news articles.  
It ingests news data via Python pipelines, stores embeddings in ChromaDB, and serves responses through a Node.js backend with Redis caching.

---

## 📐 Architecture

```
RSS Feeds / HTML 
   → Python Ingestion Pipeline 
   → Chroma Vector DB 
   → Node.js Backend 
   → React Frontend (optional)
```

---

## ⚙️ Components

### **1. Python Ingestion Pipeline** (`rag-news-ingestion/`)
Scripts:

- `scripts/fetch_rss.py`  
- `scripts/scrape_articles.py`  
- `scripts/process_articles.py`  
- `scripts/chunk_articles.py`  
- `scripts/generate_embeddings.py`  

**Responsibilities:**
- Fetch, scrape, process, chunk, and embed news articles.  
- Store embeddings in **ChromaDB**.

---

### **2. Node.js Backend** (`server/`)

Example setup:

```js
import express from "express";
import { createClient } from "redis";
import { spawn } from "child_process";

const app = express();

const redisClient = createClient({
  url: `redis://${process.env.REDIS_HOST}:${process.env.REDIS_PORT}`
});

await redisClient.connect();
```

- Exposes REST API endpoints:  
  - `POST /chat`  
  - `GET /history/:sessionId`  
  - `DELETE /history/:sessionId`  
- Uses **Redis** for session caching.

---

### **3. Redis**

- Stores session history per `sessionId`.  
- **TTL** configurable via `.env`.

---

## 💻 Local Environment Setup

### **Python**
```bash
cd rag-news-ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` file:
```env
JINA_API_KEY=
GEMINI_API_KEY=
RSS_FEEDS=http://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss
```

---

### **Node.js**
```bash
cd server
npm install
```

`.env` file:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
SESSION_TTL=86400
```

---

## ▶️ Running the Services Locally

### **Python Ingestion**
```bash
source venv/bin/activate
python scripts/fetch_rss.py
python scripts/scrape_articles.py
python scripts/process_articles.py
python scripts/chunk_articles.py
python scripts/generate_embeddings.py
```

### **Node.js Server**
```bash
npm start
# Server runs on http://localhost:5000
```

---

## 🐳 Docker Instructions

### `docker-compose.yml`
```yaml
version: "3.9"
services:
  redis:
    image: redis:7
    container_name: redis
    ports:
      - "6379:6379"

  rag-server:
    build: .
    container_name: rag-server
    ports:
      - "5000:5000"
    depends_on:
      - redis
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      SESSION_TTL: 86400
```

### `Dockerfile` (Node + Python)
```dockerfile
# Stage: Node server + Python scripts
FROM node:22-slim

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Node setup
COPY server/package*.json ./server/
RUN cd server && npm install
COPY server ./server

# Python RAG scripts
COPY rag-news-ingestion ./rag-news-ingestion
RUN pip3 install --no-cache-dir -r rag-news-ingestion/requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/rag-news-ingestion

EXPOSE 5000

CMD bash -c "\
python3 /app/rag-news-ingestion/scripts/fetch_rss.py && \
python3 /app/rag-news-ingestion/scripts/scrape_articles.py && \
python3 /app/rag-news-ingestion/scripts/process_articles.py && \
python3 /app/rag-news-ingestion/scripts/chunk_articles.py && \
python3 /app/rag-news-ingestion/scripts/generate_embeddings.py && \
node server/index.js"
```

### Build & Run
```bash
docker-compose build
docker-compose up
```

---

## 📡 API Endpoints

### **POST /chat**
Request:
```json
{
  "sessionId": "abc123",
  "query": "Latest stock market update"
}
```

Response:
```json
{
  "answer": "Sensex closed at 28220.98, down 113.57 points...",
  "history": [
    { "role": "user", "content": "Latest stock market update" },
    { "role": "assistant", "content": "Sensex closed at..." }
  ]
}
```

---

### **GET /history/:sessionId**
Response:
```json
[
  { "role": "user", "content": "Latest stock market update" },
  { "role": "assistant", "content": "Sensex closed at..." }
]
```

---

### **DELETE /history/:sessionId**
Response:
```json
{ "success": true }
```

---

## 🗄️ Caching Strategy

- Redis stores session history per `sessionId`.  
- TTL controlled via `.env` (`SESSION_TTL=86400` → 24 hours).  
- Preload frequently asked queries for **cache warming**.

---

## ✅ Summary

- **Python pipeline** handles ingestion, processing, and embeddings.  
- **Node.js backend** serves queries via REST API with Redis caching.  
- **Docker support** provided for easy deployment.  

🚀 Start experimenting with the chatbot by running ingestion + server locally or via Docker.
