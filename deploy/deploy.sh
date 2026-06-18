#!/usr/bin/env bash
# Pull latest code, install deps, seed data, restart the service. Run on the VM.
set -euo pipefail
cd /home/ubuntu/stocker
git pull --ff-only
.venv/bin/pip install -q -r stock-match/requirements.txt
# seed data on first deploy (safe to re-run)
( cd stock-match && ../.venv/bin/python fetch_bhavcopy.py && ../.venv/bin/python fetch_news.py )
sudo systemctl restart stocker
echo "✅ deployed — $(date)"
