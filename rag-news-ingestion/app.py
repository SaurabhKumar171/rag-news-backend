import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import chromadb
from langchain_community.embeddings import JinaEmbeddings
import requests

load_dotenv()

# Load API keys
jina_api_key = os.getenv("JINA_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize embedder
embedder = JinaEmbeddings(model="jina-embeddings-v2-base-en", jina_api_key=jina_api_key)

# Initialize Chroma
client = chromadb.Client()
collection = client.get_collection("news_chunks")

app = Flask(__name__)

# --- Endpoint to query news ---
@app.route("/query-news", methods=["POST"])
def query_news():
    data = request.json
    query_text = data.get("query")
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    # Embed query
    query_embedding = embedder._embed(query_text)

    # Retrieve top 5 passages
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    # Combine retrieved passages as context
    context = "\n\n".join(results['documents'][0])

    # Call Gemini API (pseudo code, replace with real endpoint)
    response = requests.post(
        "https://api.gemini.com/generate",  # Replace with actual Gemini API URL
        headers={"Authorization": f"Bearer {gemini_api_key}"},
        json={
            "prompt": f"Answer the question using the following context:\n{context}\n\nQuestion: {query_text}",
            "max_tokens": 300
        }
    )
    answer = response.json().get("answer", "")

    return jsonify({"answer": answer, "context": context})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
