"""Fetches Polymarket markets and outcomes for reference."""
import json
from pathlib import Path
from typing import Dict, List

import requests

CONFIG_PATH = Path("config/polymarket.json")
OUTPUT_PATH = Path("reports/polymarket_latest.json")


def load_config() -> Dict[str, str]:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def fetch_markets(api_key: str, base_url: str) -> List[Dict[str, str]]:
    response = requests.get(
        f"{base_url}/markets",
        headers={"Authorization": api_key},
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def fetch_outcomes(api_key: str, base_url: str, market_id: str) -> List[Dict[str, str]]:
    response = requests.get(
        f"{base_url}/markets/{market_id}/outcomes",
        headers={"Authorization": api_key},
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("data", [])


def main(lookups: int = 3) -> None:
    config = load_config()
    markets = fetch_markets(config["api_key"], config["base_url"])
    snapshot = {"updated_at": Path(".").absolute().name, "markets": []}
    for market in markets[:lookups]:
        outcomes = fetch_outcomes(config["api_key"], config["base_url"], market["id"])
        snapshot["markets"].append(
            {
                "id": market["id"],
                "title": market.get("title"),
                "liquidity": market.get("liquidity"),
                "volume": market.get("volume"),
                "outcomes": outcomes,
            }
        )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Polymarket snapshot saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
