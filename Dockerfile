# ------------------------
# Stage 2: Node server + RAG ingestion
# ------------------------
FROM node:22-slim AS node-build

# Install Python + venv
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/server

# ------------------------
# Node.js dependencies
# ------------------------
COPY server/package*.json ./
RUN npm install
COPY server/ .

# ------------------------
# Copy RAG ingestion scripts
# ------------------------
COPY rag-news-ingestion/ /app/rag-news-ingestion

# ------------------------
# Create Python virtual environment and install dependencies
# ------------------------
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r /app/rag-news-ingestion/requirements.txt

# ------------------------
# Environment variables
# ------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/rag-news-ingestion

# ------------------------
# Expose server port
# ------------------------
EXPOSE 5000

# ------------------------
# Start: first run ingestion, then start Node server
# ------------------------
CMD bash -c "\
    python /app/rag-news-ingestion/scripts/fetch_rss.py && \
    python /app/rag-news-ingestion/scripts/scrape_articles.py && \
    python /app/rag-news-ingestion/scripts/process_articles.py && \
    python /app/rag-news-ingestion/scripts/chunk_articles.py && \
    python /app/rag-news-ingestion/scripts/generate_embeddings.py && \
    node index.js \
    "
