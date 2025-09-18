import json
import os
import requests
from bs4 import BeautifulSoup

def scrape_article(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        # heuristic: most news sites have <p> tags for body
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return " ".join(paragraphs)
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return None

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATA_DIR_RAW = os.path.join(BASE_DIR, "../data/raw")
    os.makedirs(DATA_DIR_RAW, exist_ok=True)
    file_path_raw = os.path.join(DATA_DIR_RAW, "rss_articles.json")
    
    with open(file_path_raw) as f:
        rss_articles = json.load(f)

    processed = []
    for art in rss_articles:
        text = scrape_article(art["url"])
        if text:
            art["text"] = text
            processed.append(art)



    DATA_DIR = os.path.join(BASE_DIR, "../data/processed")
    os.makedirs(DATA_DIR, exist_ok=True)

    file_path = os.path.join(DATA_DIR, "articles.json")
    with open(file_path, "w") as f:
        json.dump(processed, f, indent=2)

    print(f"✅ Scraped {len(processed)} full articles")
