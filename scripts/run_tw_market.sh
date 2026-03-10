#!/bin/bash
set -euo pipefail
cd /Users/crab/.openclaw/workspace
.venv/bin/python scripts/fetch_market_data.py --config config/market_watchlist.json --output reports/tw
