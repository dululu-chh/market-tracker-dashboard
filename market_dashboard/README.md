# Market Dashboard Site

這個專案會讀取 `reports/` 目錄中最新的美股與台股快照，並產生兩個靜態網頁：`site/us.html` 和 `site/tw.html`，分別提供美股與台股的標的價格概覽與新聞。你可以將整個 `market_dashboard` 目錄推送到 GitHub，然後透過 GitHub Pages 或任意靜態網站主機發佈。

## 快速啟動

1. 確保 `reports/` 下已有最新的快照（透過 `scripts/fetch_market_data.py` / `scripts/fetch_news.py` 產生）。
2. 執行網站產生器：
   ```bash
   source .venv/bin/activate
   python scripts/build_market_site.py
   ```
3. 成功後會在 `market_dashboard/site/` 看到 `us.html`、`tw.html` 與 `style.css`。
4. 若要預覽，可用 `python -m http.server --directory market_dashboard/site 8000`，然後在瀏覽器開啟 `http://localhost:8000/us.html`。

## 更新與部署

- 只要更新 `reports/` 資料，再跑一次 `scripts/build_market_site.py` 即可刷新網頁。
- 要把這個專案推到你自己的 GitHub：
  ```bash
  git init
  git add market_dashboard
  git commit -m "Init market dashboard"
  git remote add origin <你的 GitHub repo URL>
  git branch -M main
  git push -u origin main
  ```
- 若想用 GitHub Pages，請將 `market_dashboard/site` 整個目錄設為 Pages 根目錄，或將檔案複製到 `gh-pages` 分支。

## 其他說明

- `build_market_site.py` 只是個簡單 generator；你可以依實際需求加入更多數據、圖表或 memo。報表每次都會以最新的 JSON 內容為基礎。
- 靜態頁面依賴 `style.css`，如果想修改視覺風格可直接編輯 `market_dashboard/site/style.css`。
