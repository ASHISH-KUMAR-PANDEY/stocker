#!/usr/bin/env bash
# Refresh the free NSE data that powers Discover. Wire into cron (see DEPLOY.md).
#   - quotes + news: daily after market close
#   - history (heavy: ~90 daily files): weekly is plenty
set -euo pipefail
APP=/home/ubuntu/stocker/stock-match
PY=/home/ubuntu/stocker/.venv/bin/python
cd "$APP"

case "${1:-daily}" in
  daily)  "$PY" fetch_bhavcopy.py; "$PY" fetch_news.py ;;
  weekly) "$PY" fetch_history.py ;;
  all)    "$PY" fetch_bhavcopy.py; "$PY" fetch_history.py; "$PY" fetch_news.py ;;
esac
echo "refresh ($1) done: $(date)"
