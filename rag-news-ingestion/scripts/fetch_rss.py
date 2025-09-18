import feedparser
import json
import os

RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.cnn.com/rss/edition.rss"
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",   
    "https://www.investing.com/rss/news_25.rss",        
    "https://www.moneycontrol.com/rss/MCtopnews.xml",     
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",  
    "https://www.marketwatch.com/rss/topstories",        
    "https://finance.yahoo.com/news/rssindex",  
]

def fetch_rss_articles():
    articles = []
    article_id = 1

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:50]:  # take up to 25 per feed
            articles.append({
                "id": str(article_id),
                "title": entry.title,
                "url": entry.link,
                "published": getattr(entry, "published", None),
                "source": feed.feed.get("title", "Unknown"),
                "summary": entry.get("summary", "")
            })
            article_id += 1

    return articles

if __name__ == "__main__":
    articles = fetch_rss_articles()
    # print(articles)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../data/raw")
    os.makedirs(DATA_DIR, exist_ok=True)

    file_path = os.path.join(DATA_DIR, "rss_articles.json")
    with open(file_path, "w") as f:
        json.dump(articles, f, indent=2)

    print(f"✅ Saved {len(articles)} articles to data/raw/rss_articles.json")
