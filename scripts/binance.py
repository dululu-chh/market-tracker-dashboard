"""Binance client helpers for fetching market data."""
import json
from pathlib import Path
from typing import Dict

import requests

CONFIG_PATH = Path("config/binance.json")
OUTPUT_PATH = Path("reports/binance_latest.json")


def load_config() -> Dict[str, str]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_ticker(config: Dict[str, str]) -> Dict[str, str]:
    url = f"{config['base_url']}/api/v3/ticker/24hr"
    params = {"symbol": config["symbol"]}
    headers = {"X-MBX-APIKEY": config["api_key"]}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    payload = response.json()
    return {
        "symbol": payload.get("symbol"),
        "price": payload.get("lastPrice"),
        "open": payload.get("openPrice"),
        "high": payload.get("highPrice"),
        "low": payload.get("lowPrice"),
        "volume": payload.get("volume"),
        "quote_volume": payload.get("quoteVolume"),
        "percent": payload.get("priceChangePercent"),
    }


def save_snapshot(data: Dict[str, str]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {"updated_at": data.get("timestamp"), "ticker": data}
    OUTPUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def response_timestamp() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat()


def main() -> None:
    config = load_config()
    ticker = fetch_ticker(config)
    ticker["timestamp"] = response_timestamp()
    save_snapshot(ticker)
    print("Binance ticker saved to", OUTPUT_PATH)


def response_timestamp() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat()


if __name__ == "__main__":
    main()
