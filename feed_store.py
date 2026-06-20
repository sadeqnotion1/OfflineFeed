"""
feed_store.py  -  Durable local persistence for the OfflineFeed live feed.

WHY THIS EXISTS
---------------
OfflineFeed already persists saved/archived/ignored/sent posts to JSON files,
but the LIVE FEED itself (`news_cache["data"]` in gui_server.py) lives ONLY in
memory and is wiped to [] on every launch.

`archive_removed_posts(old, new)` is supposed to keep posts that leave the
source feed, but it uses the in-memory cache as its "old" baseline. Because the
cache is empty on a fresh start, the FIRST refresh of every session compares
against [] and archives nothing -- so posts that roll off the RSS between app
restarts are lost forever.

This module adds a durable on-disk snapshot of the live feed so that:
  1. Every fetched post is written to a local store (feed_cache.json).
  2. The "removed from feed" baseline survives app restarts, so
     archive_removed_posts() actually captures posts that leave the feed.
  3. The feed remains viewable offline (fallback when the network fetch fails).

The snapshot is written atomically (tmp + os.replace) so a crash mid-write can
never leave a truncated/corrupt file.

This file is ADDITIVE: it introduces no behavioural change on its own. The
three small call sites in gui_server.py wire it in (see README).
"""

import os
import json
import threading
import datetime

# Resolve <repo>/offline_viewer/assets exactly like gui_server.py's DIRECTORY.
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_BASE_DIR, "offline_viewer", "assets")
SNAPSHOT_PATH = os.path.join(ASSETS_DIR, "feed_cache.json")

_feed_snapshot_lock = threading.Lock()


def load_feed_snapshot():
    """Return the last persisted live-feed article list (or [] if none).

    Accepts both the wrapped {"articles": [...]} payload written by
    save_feed_snapshot() and a bare list, for forward/backward safety.
    """
    with _feed_snapshot_lock:
        if not os.path.exists(SNAPSHOT_PATH):
            return []
        try:
            with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[feed_store] Error loading feed snapshot: {e}")
            return []
        if isinstance(data, dict):
            return data.get("articles", []) or []
        if isinstance(data, list):
            return data
        return []


def save_feed_snapshot(articles, status_map=None):
    """Persist the current live feed atomically to feed_cache.json."""
    with _feed_snapshot_lock:
        try:
            os.makedirs(ASSETS_DIR, exist_ok=True)
            payload = {
                "saved_at": datetime.datetime.now().isoformat(),
                "source_status": status_map or {},
                "articles": articles or [],
            }
            tmp_path = SNAPSHOT_PATH + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
            os.replace(tmp_path, SNAPSHOT_PATH)  # atomic swap
        except Exception as e:
            print(f"[feed_store] Error saving feed snapshot: {e}")


def snapshot_count():
    """Convenience: number of posts currently kept in the local store."""
    return len(load_feed_snapshot())
