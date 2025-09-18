import os
import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import JinaEmbeddings
from dotenv import load_dotenv
import google.generativeai as genai

# ------------------------
# Load environment variables
# ------------------------
load_dotenv()

jina_api_key = os.getenv("JINA_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not jina_api_key:
    raise ValueError("JINA_API_KEY not found in environment variables")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# ------------------------
# Setup Chroma persistent client
# ------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")

client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_collection("news_chunks")
# print("✅ Loaded collection:", collection.name)

# ------------------------
# Initialize embedder + Gemini
# ------------------------
embedder = JinaEmbeddings(model="jina-embeddings-v2-base-en", jina_api_key=jina_api_key)
genai.configure(api_key=gemini_api_key)
llm = genai.GenerativeModel("gemini-1.5-flash")

# ------------------------
# RAG Query Function
# ------------------------
def rag_query(query: str, n_results: int = 10):
    # Step 1: Embed query
    query_embedding = embedder.embed_query(query)

    # Step 2: Retrieve from Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    # results = collection.peek(limit=5)
    # print(results["documents"])

    # Step 3: Build context
    context = "\n\n".join(results["documents"][0])

    # Step 4: Ask Gemini
    prompt = f"""Answer the following question using the provided context.
If the context is not enough, say so instead of guessing.

Question: {query}

Context:
{context}

Answer:"""

    response = llm.generate_content(prompt)
    return response.text

# ------------------------
# Interactive Loop
# ------------------------
if __name__ == "__main__":
    print("🤖 RAG Chatbot ready! Ask your question (type 'exit' to quit).")
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit"]:
            break
        answer = rag_query(query)
        print(f"\nAI: {answer}")
