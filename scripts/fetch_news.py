"""Fetches recent headlines from configured RSS feeds and stores structured summaries."""
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import feedparser


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def keyword_matches(text: str, keywords: List[str]) -> List[str]:
    lowered = text.lower()
    hits = []
    for keyword in keywords:
        key = keyword.lower()
        if key in lowered and keyword not in hits:
            hits.append(keyword)
    return hits


def truncate(text: str, length: int = 140) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= length:
        return text
    return text[: length - 1] + "…"


def fetch_feed_items(feed: dict, max_items: int, keywords: List[str]) -> dict:
    parsed = feedparser.parse(feed["url"])
    items = []
    for entry in parsed.entries[:max_items]:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", entry.get("description", "")).strip()
        published = entry.get("published") or entry.get("updated") or ""
        match_text = f"{title} {summary}"
        matches = keyword_matches(match_text, keywords)
        items.append(
            {
                "title": title,
                "summary": truncate(summary, 160),
                "link": entry.get("link", ""),
                "published": published,
                "keywords": matches,
            }
        )
    return {
        "name": feed.get("name", ""),
        "language": feed.get("language", ""),
        "url": feed.get("url", ""),
        "items": items,
    }


def collect_news(config: dict) -> dict:
    max_items = config.get("max_items_per_feed", 3)
    keywords = config.get("keywords", [])
    feeds = config.get("feeds", [])
    snapshot = {
        "retrieved_at": datetime.now().isoformat(),
        "feeds": [],
    }
    for feed in feeds:
        try:
            snapshot["feeds"].append(fetch_feed_items(feed, max_items, keywords))
        except Exception as exc:
            snapshot["feeds"].append(
                {
                    "name": feed.get("name"),
                    "url": feed.get("url"),
                    "error": str(exc),
                }
            )
    return snapshot


def save_snapshot(snapshot: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = output_dir / f"news_snapshot_{stamp}.json"
    with fname.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return fname


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch headlines from RSS feeds")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/news_feeds.json"),
        help="Path to RSS feed configuration",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/news"),
        help="Directory to write news snapshots",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    snapshot = collect_news(config)
    output = save_snapshot(snapshot, args.output)
    print(f"已將新聞摘要寫入：{output}")


if __name__ == "__main__":
    main()
