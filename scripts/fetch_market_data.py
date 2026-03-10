"""Fetches quotes from Yahoo Finance for equities and futures with optional Finnhub fallback."""
import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import requests
import yfinance as yf


FINNHUB_CONFIG = Path("config/finnhub.json")


def load_config(config_path: Path) -> dict:
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_finnhub_key() -> Optional[str]:
    key = os.getenv("FINNHUB_API_KEY")
    if key:
        return key
    if not FINNHUB_CONFIG.exists():
        return None
    conf = load_config(FINNHUB_CONFIG)
    return conf.get("api_key")


def fetch_finnhub_quote(symbol: str) -> Optional[dict]:
    key = get_finnhub_key()
    if not key:
        return None
    url = "https://finnhub.io/api/v1/quote"
    resp = requests.get(url, params={"symbol": symbol, "token": key}, timeout=10)
    if resp.status_code != 200:
        return None
    payload = resp.json()
    if not payload or payload.get("c") is None:
        return None
    return {
        "symbol": symbol,
        "regularMarketPrice": payload.get("c"),
        "regularMarketPreviousClose": payload.get("pc"),
        "regularMarketOpen": payload.get("o"),
        "regularMarketHigh": payload.get("h"),
        "regularMarketLow": payload.get("l"),
        "timestamp": datetime.now().isoformat(),
    }


def fetch_ticker(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = {}
    try:
        fast = ticker.fast_info
    except Exception:
        fast = {}
    result = {
        "symbol": symbol,
        "regularMarketPrice": fast.get("last_price"),
        "currency": fast.get("currency"),
        "exchange": fast.get("exchange"),
        "regularMarketChange": fast.get("change"),
        "regularMarketChangePercent": fast.get("percent_change"),
        "regularMarketPreviousClose": fast.get("previous_close"),
        "regularMarketOpen": fast.get("open"),
        "regularMarketDayHigh": fast.get("day_high"),
        "regularMarketDayLow": fast.get("day_low"),
        "timestamp": datetime.now().isoformat(),
    }
    if not result["regularMarketPrice"]:
        hist = ticker.history(period="1m")
        if not hist.empty:
            latest = hist.iloc[-1]
            result["regularMarketPrice"] = latest.get("Close")
    if not result["regularMarketPrice"]:
        fh_quote = fetch_finnhub_quote(symbol)
        if fh_quote:
            for key in (
                "regularMarketPrice",
                "regularMarketPreviousClose",
                "regularMarketOpen",
                "regularMarketDayHigh",
                "regularMarketDayLow",
            ):
                if fh_quote.get(key) is not None:
                    result[key] = fh_quote[key]
            result["timestamp"] = fh_quote.get("timestamp", result["timestamp"])
    if not result["currency"]:
        info = ticker.info or {}
        result["currency"] = info.get("currency")
    return result


def collect_market_data(config: dict, categories: Optional[Iterable[str]] = None) -> dict:
    allowed = None if not categories else {cat for cat in categories}
    snapshot = {"retrieved_at": datetime.now().isoformat(), "data": {}}
    for category, items in config.get("watchlist", {}).items():
        if allowed and category not in allowed:
            continue
        snapshot["data"].setdefault(category, [])
        for friendly_name, symbol in items.items():
            try:
                quote = fetch_ticker(symbol)
                quote["name"] = friendly_name
                snapshot["data"][category].append(quote)
            except Exception as exc:
                snapshot["data"][category].append({
                    "name": friendly_name,
                    "symbol": symbol,
                    "error": str(exc),
                })
    return snapshot


def save_snapshot(snapshot: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"market_snapshot_{stamp}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch market quotes via Yahoo Finance")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/market_watchlist.json"),
        help="Path to the watchlist configuration (JSON)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports"),
        help="Directory where snapshots will be stored",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="限制從哪些分類抓取（預設抓全部）。例如：--categories 美股期貨",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if not config:
        raise SystemExit("請先建立 config/market_watchlist.json，並填入追蹤標的。")
    snapshot = collect_market_data(config, args.categories)
    output = save_snapshot(snapshot, args.output)
    print(f"已將報價寫入：{output}")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
