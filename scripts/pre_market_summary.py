"""Helper script to fetch targeted pre-market tickers and print concise summary."""
from datetime import datetime

import yfinance as yf

TARGETS = {
    "ES1!": "ES=F",
    "NQ1!": "NQ=F",
    "YM1!": "YM=F",
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",
    "US10Y": "^TNX",
    "CL1!": "CL=F",
    "SOX": "^SOX",
    "NVDA": "NVDA",
    "AMD": "AMD",
    "AVGO": "AVGO",
    "MU": "MU",
    "TSM": "TSM",
    "ASML": "ASML",
    "ARM": "ARM",
    "MRVL": "MRVL",
    "PLTR": "PLTR",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "META": "META",
}


def fetch(ticker):
    t = yf.Ticker(ticker)
    fast = {}
    try:
        fast = t.fast_info
    except Exception as exc:
        print(f"fast_info fail for {ticker}: {exc}")
        fast = {}
    data = {
        "symbol": ticker,
        "price": fast.get("last_price"),
        "change": fast.get("change"),
        "percent": fast.get("percent_change"),
        "prev_close": None,
        "trend": fast.get("day_high", "-"),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    hist = None
    try:
        hist = t.history(period="2d")
    except Exception as exc:
        print(f"history fail for {ticker}: {exc}")
    if hist is not None and not hist.empty:
        try:
            if data["price"] is None:
                last = hist.iloc[-1]
                data["price"] = last.get("Close")
            if len(hist) >= 2:
                prev = hist.iloc[-2]
                data["prev_close"] = prev.get("Close")
                if data["price"] is not None:
                    data["change"] = data["price"] - data["prev_close"]
                    if data["prev_close"]:
                        data["percent"] = (data["change"] / data["prev_close"]) * 100
        except Exception as exc:
            print(f"history calc fail for {ticker}: {exc}")
    if data["price"] is None:
        print(f"未取得價格：{ticker}")
    return data


def main():
    rows = []
    for name, symbol in TARGETS.items():
        try:
            rows.append((name, fetch(symbol)))
        except Exception as exc:
            rows.append((name, {"symbol": symbol, "error": str(exc)}))
    report = ""
    report += f"抓取時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += "symbol, price, change, percent\n"
    for name, info in rows:
        if "error" in info:
            report += f"{name}({info['symbol']}): ERROR {info['error']}\n"
        else:
            report += f"{name}({info['symbol']}): {info['price']} {info['change']} {info['percent']}\n"
    print(report)


if __name__ == "__main__":
    main()
