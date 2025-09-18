import json
import os

def chunk_text(text, chunk_size=200):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size])

if __name__ == "__main__":
    # Absolute path to project root
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Load the cleaned news.json
    news_file = os.path.join(DATA_DIR, "news.json")
    with open(news_file, "r") as f:
        articles = json.load(f)

    # Create chunks
    chunks = []
    for art in articles:
        for idx, chunk in enumerate(chunk_text(art["text"], 200)):
            chunks.append({
                "article_id": art["id"],
                "chunk_id": f"{art['id']}_{idx}",
                "title": art["title"],
                "text_chunk": chunk
            })

    # Save chunks to news_chunks.json
    chunks_file = os.path.join(DATA_DIR, "news_chunks.json")
    with open(chunks_file, "w") as f:
        json.dump(chunks, f, indent=2)

    print(f"✅ Chunked {len(articles)} articles into {len(chunks)} passages")
