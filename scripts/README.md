# 市場資料擷取範例腳本

這個範例會使用 `yfinance` 連到 Yahoo Finance，抓取你在 `config/market_watchlist.json` 裡定義的個股與期貨報價。

## 預備作業
1. 先啟動剛建立的虛擬環境：
   ```bash
   source .venv/bin/activate
   ```
2. 確認 `yfinance` 已安裝（應該已在 `.venv` 內）：
   ```bash
   pip show yfinance
   ```
3. 編輯 `config/market_watchlist.json`，把你想追蹤的代號加進去。每個分類下是「顯示名稱」→「Yahoo Finance 代號」。

## 執行腳本
```bash
python scripts/fetch_market_data.py --config config/market_watchlist.json --output reports
```

- `--config`：自訂 watchlist 路徑。
- `--output`：輸出報價快照的資料夾（預設 `reports/`），每次會寫入 `market_snapshot_YYYYMMDD_HHmmss.json`。
- `--categories`：只抓特定分類，例如 `--categories 美股期貨`，多個分類以空格分隔。

## 輸出格式（JSON 範例）
```json
{
  "retrieved_at": "2026-03-09T20:15:01.123456",
  "data": {
    "美股AI/半導體": [
      {
        "symbol": "NVDA",
        "name": "NVIDIA",
        "regularMarketPrice": 125.63,
        "currency": "USD",
        "exchange": "NMS",
        "regularMarketChangePercent": 1.3,
        "timestamp": "2026-03-09T20:15:01.123456"
      }
    ]
  }
}
```

## 未來可擴充
- 把報價格式整理成報告模板（例如台股/美股分段）再交給我整理成文。
- 加入每分鐘的排程（cron 或 cloud scheduler），再用我整理後發送 Telegram 或 Email 報告。
- 用 `yfinance` 的 history 撈技術面資料，或用其他 API 補充最新期貨價差。
- 加入新聞 RSS 摘要：透過 `python scripts/fetch_news.py` 把 `config/news_feeds.json` 裡的來源抓下來並輸出到 `reports/news/news_snapshot_YYYYMMDD_HHmmss.json`。