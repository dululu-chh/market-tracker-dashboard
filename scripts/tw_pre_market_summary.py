"""Fetches TW/US macro data for Taiwan pre-market analysis."""
from datetime import datetime
from typing import Dict

import yfinance as yf

TARGETS: Dict[str, str] = {
    "Nasdaq": "^NDX",
    "S&P500": "^GSPC",
    "Dow Jones": "^DJI",
    "SOX": "^SOX",
    "VIX": "^VIX",
    "US10Y": "^TNX",
    "DXY": "DX-Y.NYB",
    "原油": "CL=F",
    "台指期": "^TXF",
    "富台期": "TFX=F",
    "台積電ADR": "TSM",
    "台積電": "2330.TW",
    "聯發科": "2454.TW",
    "鴻海": "2317.TW",
    "廣達": "2382.TW",
    "緯創": "3231.TW",
    "緯穎": "6669.TW",
    "技嘉": "2376.TW",
    "英業達": "2356.TW",
    "雙鴻": "3324.TW",
    "奇鋐": "3325.TW",
}




def safe_get(obj, key):
    try:
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return None


def fetch(symbol: str) -> Dict[str, float]:
    ticker = yf.Ticker(symbol)
    data = {
        "price": None,
        "change": None,
        "percent": None,
        "currency": None,
    }
    fast = {}
    try:
        fast = ticker.fast_info
    except Exception:
        fast = {}
    data["price"] = safe_get(fast, "last_price")
    data["change"] = safe_get(fast, "change")
    data["percent"] = safe_get(fast, "percent_change")
    data["currency"] = safe_get(fast, "currency")
    hist = None
    try:
        hist = ticker.history(period="2d")
    except Exception:
        hist = None
    if hist is not None and not hist.empty:
        data_price = data["price"]
        last = hist.iloc[-1]["Close"]
        if data_price is None:
            data["price"] = last
        if len(hist) >= 2:
            prev = hist.iloc[-2]["Close"]
            data["change"] = data["price"] - prev
            if prev:
                data["percent"] = (data["change"] / prev) * 100
    return data


def main() -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"抓取時間：{stamp}")
    print("名稱, 價格, 漲跌, 漲跌幅, 單位")
    for name, symbol in TARGETS.items():
        try:
            info = fetch(symbol)
            print(
                f"{name}({symbol}): {info['price']} {info['change']} {info['percent']} {info['currency']}"
            )
        except Exception as exc:
            print(f"{name}({symbol}): error {exc}")

if __name__ == "__main__":
    main()
