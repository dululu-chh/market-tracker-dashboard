# 市場自動化排程

此排程透過 workspace 中的腳本（`scripts/fetch_market_data.py`、`scripts/fetch_news.py`、以及封裝好的 shell 腳本）自動在指定時段抓取新聞與市價快照，方便我依照台灣與美股節奏回報即時資訊。

## 共同前置作業
1. 確認先前已建立虛擬環境並安裝 `yfinance`、`feedparser`：
   ```bash
   cd /Users/crab/.openclaw/workspace
   source .venv/bin/activate
   pip install -r requirements（無此檔則手動安裝）
   ```
2. 將命令寫進定時排程（建議使用 `crontab -e` 編輯），或用你習慣的 scheduler（launchd、systemd timer）來呼叫下方的 shell 腳本。所有腳本都會先切到 workspace 再執行，並直接使用 `.venv` 裡的 Python。
3. `reports/` 會自動產生子資料夾 `news/`、`tw/`、`us/` 來區隔不同來源結果。

---

## 排程 1：台股（Asia/Taipei）
- **目的**：8:30/8:50 抓台股期貨 + 國際新聞，9:05 起每 30 分鐘抓一次台股與你關心的 AI/半導體個股，最後於 13:30 收盤時再拉一次。
- **使用腳本**：
  - `scripts/run_tw_pre_market.sh`（新聞 + `台股期貨`）
  - `scripts/run_tw_market.sh`（完整 watchlist 包含台股與美股個股）
- **範例 cron 設定**（請用 `crontab -e` 加入，若要改用 launchd 可用相同指令）：
  ```cron
  TZ=Asia/Taipei
  30 8 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_pre_market.sh'
  50 8 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_pre_market.sh'
  5 9 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  35 9 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  5 10 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  35 10 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  5 11 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  35 11 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  5 12 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  35 12 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  5 13 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'
  30 13 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_tw_market.sh'   # 收盤快照
  ```
  > 若想抓 13:35 的盤後資訊也可再加一行。

## 排程 2：美股（America/New_York）
- **目的**：開盤前 1 小時（08:30）與 30 分鐘（09:00）分別抓期貨 + 新聞，開盤後每 30 分鐘抓一次美股報價直到台北時間凌晨收盤。
- **注意**：`cron` 使用 `TZ=America/New_York` 會自動配合夏令/冬令時間，無需手動刷新。
- **使用腳本**：
  - `scripts/run_us_pre_market.sh`（新聞 + `美股期貨`）
  - `scripts/run_us_market.sh`（美股 watchlist）
- **範例 cron 設定（NY 時區）**：
  ```cron
  TZ=America/New_York
  30 8 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_pre_market.sh'
  0 9 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_pre_market.sh'
  30 9 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 10 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 10 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 11 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 11 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 12 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 12 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 13 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 13 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 14 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 14 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 15 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  30 15 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  0 16 * * 1-5 /bin/bash -lc 'cd /Users/crab/.openclaw/workspace && ./scripts/run_us_market.sh'
  ```
  > 這樣每個 30 分鐘都會拉一次報價；若想要貼近收盤再多一筆 16:30 的話再加一行即可。

---

## 後續建議
1. 把 `reports/tw/`、`reports/us/`、`reports/news/` 的 JSON 快照交給我整理摘要，我可以轉變成你習慣的盤前/即時簡報。
2. 若要將資料推送到 Telegram 等通道，可再用 `cron` 觸發一段整理腳本，或讓我讀 `reports/` 裡的最新檔案並發送。
