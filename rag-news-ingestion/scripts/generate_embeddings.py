import os
import json
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import JinaEmbeddings
from dotenv import load_dotenv 

# Load .env file
load_dotenv()

# Access API key from environment
jina_api_key = os.getenv("JINA_API_KEY")
if not jina_api_key:
    raise ValueError("JINA_API_KEY not found in environment variables")

# ------------------------
# Setup paths
# ------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHUNKS_FILE = os.path.join(DATA_DIR, "news_chunks.json")

# ------------------------
# Load chunks
# ------------------------
with open(CHUNKS_FILE, "r") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

# ------------------------
# Initialize embedder
# ------------------------
embedder = JinaEmbeddings(model="jina-embeddings-v2-base-en", jina_api_key=jina_api_key)

# ------------------------
# Generate embeddings
# ------------------------
texts = [chunk["text_chunk"] for chunk in chunks]
embeddings = embedder.embed_documents(texts)

for chunk, emb in zip(chunks, embeddings):
    # Flatten in case Jina returns [[...]]
    if isinstance(emb[0], list):
        emb = emb[0]
    chunk["embedding"] = emb

print("✅ Embeddings generated for all chunks")

# ------------------------
# Store embeddings in Chroma (persistent)
# ------------------------
client = chromadb.PersistentClient(path="./chroma_db")  # folder to save everything

collection_name = "news_chunks"

# Delete existing collection if exists
if collection_name in [c.name for c in client.list_collections()]:
    client.delete_collection(name=collection_name)

collection = client.create_collection(name=collection_name)

for chunk in chunks:
    collection.add(
        ids=[chunk["chunk_id"]],
        embeddings=[chunk["embedding"]],
        documents=[chunk["text_chunk"]],
        metadatas={
            "title": chunk["title"],
            "article_id": chunk["article_id"]
        }
    )


# Persist DB to disk
# client.persist()
print(f"✅ Stored {len(chunks)} chunks in Chroma vector DB")
