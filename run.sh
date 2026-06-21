#!/usr/bin/env bash
# OfflineFeed launcher - keeps the repo root .py-free
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$DIR/backend/run_offlinefeed.py" "$@"
