

import feedparser
import re
import html


def _clean(text: str) -> str:
    """Strip HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def fetch_news(rss_url: str, max_items: int = 14) -> list[dict]:
    """
    Fetch articles from an RSS feed URL.

    Args:
        rss_url:   Full RSS URL (e.g. Google News RSS endpoint)
        max_items: Maximum number of articles to return

    Returns:
        List of article dicts with keys: title, description, source, link, published
    """
    try:
        feed = feedparser.parse(rss_url)

        if feed.bozo and not feed.entries:
            return []

        articles = []
        for entry in feed.entries[:max_items]:
            title = _clean(entry.get("title", ""))
            if not title:
                continue

            desc = _clean(entry.get("summary", "") or entry.get("description", ""))
            source = ""
            if hasattr(entry, "source") and entry.source:
                source = entry.source.get("title", "")
            if not source:
                source = feed.feed.get("title", "Google News")

            link = entry.get("link", "")
            published = entry.get("published", "")

            articles.append({
                "title": title,
                "description": desc[:300] if desc else "",
                "source": source,
                "link": link,
                "published": published,
            })

        return articles

    except Exception as e:
        return []


# ── Category → RSS URL mapping ─────────────────────────────────────────────────
RSS_FEEDS = {
    "Top stories":  "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "Technology":   "https://news.google.com/rss/search?q=technology&hl=en-IN&gl=IN&ceid=IN:en",
    "Science":      "https://news.google.com/rss/search?q=science&hl=en-IN&gl=IN&ceid=IN:en",
    "Health":       "https://news.google.com/rss/search?q=health&hl=en-IN&gl=IN&ceid=IN:en",
    "World":        "https://news.google.com/rss/search?q=world+news&hl=en-IN&gl=IN&ceid=IN:en",
    "Business":     "https://news.google.com/rss/search?q=business&hl=en-IN&gl=IN&ceid=IN:en",
    "Politics":     "https://news.google.com/rss/search?q=politics&hl=en-IN&gl=IN&ceid=IN:en",
    "Sports":       "https://news.google.com/rss/search?q=sports&hl=en-IN&gl=IN&ceid=IN:en",
}
