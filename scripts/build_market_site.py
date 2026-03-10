"""Build US/TW market pages from the latest snapshots."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path("market_dashboard")
SITE_DIR = BASE_DIR / "site"
SITE_DIR.mkdir(parents=True, exist_ok=True)

US_SNAPSHOT_DIRS = [Path("reports/us"), Path("reports/us_demo")]
TW_SNAPSHOT_DIRS = [Path("reports/tw")]
NEWS_SNAPSHOT_DIRS = [Path("reports/news_live"), Path("reports/news_demo"), Path("reports/news")]
STYLE_PATH = SITE_DIR / "style.css"


def load_latest_snapshot(paths: List[Path]) -> Optional[Dict[str, Any]]:
    for path in paths:
        if not path.exists():
            continue
        files = sorted(path.glob("*.json"))
        if not files:
            continue
        with files[-1].open("r", encoding="utf-8") as f:
            try:
                return {
                    "payload": json.load(f),
                    "timestamp": files[-1].stem,
                    "path": files[-1],
                }
            except json.JSONDecodeError:
                continue
    return None


def safe_format(value: Any, precision: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{value:,.{precision}f}"
    except Exception:
        return str(value)


def pick_value(entry: Dict[str, Any]) -> Optional[float]:
    for key in ("regularMarketPrice", "regularMarketOpen", "regularMarketPreviousClose"):
        val = entry.get(key)
        if isinstance(val, (int, float)):
            return val
    return None


def pick_change(entry: Dict[str, Any]) -> Optional[float]:
    change = entry.get("regularMarketChange")
    if isinstance(change, (int, float)):
        return change
    price = pick_value(entry)
    prev = entry.get("regularMarketPreviousClose")
    if price is not None and isinstance(prev, (int, float)):
        return price - prev
    return None


def pick_change_pct(entry: Dict[str, Any]) -> Optional[float]:
    pct = entry.get("regularMarketChangePercent")
    if isinstance(pct, (int, float)):
        return pct
    change = pick_change(entry)
    prev = entry.get("regularMarketPreviousClose")
    if change is not None and isinstance(prev, (int, float)) and prev:
        return (change / prev) * 100
    return None


def build_category_section(category: str, entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return ""
    rows = []
    for entry in entries[:10]:
        name = entry.get("name") or entry.get("symbol")
        symbol = entry.get("symbol", "—")
        value = pick_value(entry)
        change = pick_change(entry)
        pct = pick_change_pct(entry)
        status = "neutral"
        if pct is not None:
            if pct > 0:
                status = "positive"
            elif pct < 0:
                status = "negative"
        rows.append(
            f"""
<tr>
  <td>{name}</td>
  <td>{symbol}</td>
  <td>{safe_format(value)}</td>
  <td class=\"{status}\">{safe_format(change)}</td>
  <td class=\"{status}\">{safe_format(pct)}</td>
  <td>{entry.get('currency', '—')}</td>
</tr>
"""
        )
    return f"""
<section class=\"panel\">
  <h2>{category}</h2>
  <table>
    <thead>
      <tr>
        <th>名稱</th>
        <th>代號</th>
        <th>價格/開盤</th>
        <th>漲跌</th>
        <th>漲跌幅 (%)</th>
        <th>幣別</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</section>
"""


def build_news_items(news_snapshot: Optional[Dict[str, Any]], limit: int = 6) -> str:
    if not news_snapshot:
        return "<p>尚未取得新聞摘要。</p>"
    bullets = []
    total = 0
    feeds = news_snapshot.get("payload", {}).get("feeds", [])
    for feed in feeds:
        for item in feed.get("items", [])[:2]:
            title = item.get("title") or "(無標題)"
            summary = item.get("summary") or ""
            link = item.get("link") or "#"
            bullets.append(
                f"<li><strong>[{feed.get('name')}]</strong> <a href=\"{link}\" target=\"_blank\">{title}</a> — {summary}</li>"
            )
            total += 1
            if total >= limit:
                break
        if total >= limit:
            break
    if not bullets:
        return "<p>尚未取得新聞摘要。</p>"
    return "<ul>" + "".join(bullets) + "</ul>"


def render_page(title: str, subtitle: str, timestamp: str, sections: List[str], news: str, filename: Path) -> None:
    content = f"""
<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
  <header>
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <p>資料時間：{timestamp}</p>
  </header>
  <main>
    {''.join(sections)}
    <section class=\"panel\">
      <h2>新聞快照</h2>
      {news}
    </section>
  </main>
  <footer>
    建置時間：{datetime.utcnow():%Y-%m-%d %H:%M UTC}
  </footer>
</body>
</html>
"""
    filename.write_text(content, encoding="utf-8")


def build_site() -> None:
    us_snapshot = load_latest_snapshot(US_SNAPSHOT_DIRS)
    tw_snapshot = load_latest_snapshot(TW_SNAPSHOT_DIRS)
    news_snapshot = load_latest_snapshot(NEWS_SNAPSHOT_DIRS)

    if not STYLE_PATH.exists():
        print(f"warning: {STYLE_PATH} not found. Please ensure style.css exists.")

    us_sections: List[str] = []
    if us_snapshot:
        categories = us_snapshot["payload"].get("data", {})
        if "data" in categories and isinstance(categories["data"], dict):
            categories = categories["data"]
        for category, items in categories.items():
            if not isinstance(items, list):
                continue
            us_sections.append(build_category_section(category, items))
        us_timestamp = us_snapshot["payload"].get("retrieved_at", "—")
    else:
        us_sections.append("<p>尚未取得美股快照。</p>")
        us_timestamp = "—"

    tw_sections: List[str] = []
    if tw_snapshot:
        categories = tw_snapshot["payload"].get("data", {})
        if "data" in categories and isinstance(categories["data"], dict):
            categories = categories["data"]
        for category, items in categories.items():
            if not isinstance(items, list):
                continue
            tw_sections.append(build_category_section(category, items))
        tw_timestamp = tw_snapshot["payload"].get("retrieved_at", "—")
    else:
        tw_sections.append("<p>尚未取得台股快照。</p>")
        tw_timestamp = "—"

    news_html = build_news_items(news_snapshot)

    render_page(
        title="美股即時資訊",
        subtitle="涵蓋指數 ETF、科技加半導體個股與相關期貨",
        timestamp=us_timestamp,
        sections=us_sections,
        news=news_html,
        filename=SITE_DIR / "us.html",
    )

    render_page(
        title="台股即時資訊",
        subtitle="涵蓋台股期貨與依賴美股盤前動態的觀察點",
        timestamp=tw_timestamp,
        sections=tw_sections,
        news=news_html,
        filename=SITE_DIR / "tw.html",
    )


if __name__ == "__main__":
    build_site()
