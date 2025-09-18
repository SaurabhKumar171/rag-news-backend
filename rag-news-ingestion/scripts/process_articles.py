import json
import os

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATA_DIR_PROCESSED = os.path.join(BASE_DIR, "../data/processed")
    os.makedirs(DATA_DIR_PROCESSED, exist_ok=True)
    file_path_processed = os.path.join(DATA_DIR_PROCESSED, "articles.json")
    
    with open(file_path_processed) as f:
        articles = json.load(f)

    # Standard schema
    cleaned = []
    for art in articles:
        cleaned.append({
            "id": art["id"],
            "title": art["title"],
            "url": art["url"],
            "published": art.get("published"),
            "source": art.get("source"),
            "text": art["text"]
        })

    DATA_DIR = os.path.join(BASE_DIR, "../data")
    os.makedirs(DATA_DIR, exist_ok=True)

    file_path = os.path.join(DATA_DIR, "news.json")
    
    with open(file_path, "w") as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ Final corpus saved at data/news.json ({len(cleaned)} articles)")
