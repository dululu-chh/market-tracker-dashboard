#!/bin/bash
set -euo pipefail
cd /Users/crab/.openclaw/workspace
.venv/bin/python scripts/fetch_news.py --output reports/news
.venv/bin/python scripts/fetch_market_data.py --config config/market_watchlist.json --output reports/us --categories 美股期貨
