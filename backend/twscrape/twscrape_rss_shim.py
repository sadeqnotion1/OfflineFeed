#!/usr/bin/env python3
"""
twscrape_rss_shim.py  --  local RSS bridge for OfflineFeed (Path B).

What it does
------------
Exposes  GET /<handle>/rss  on http://127.0.0.1:8081 and returns a standard
RSS 2.0 feed of that account's LATEST, reverse-chronological tweets, fetched via
twscrape (X GraphQL UserTweets, using your own burner-account pool).

To OfflineFeed this looks identical to a Nitter host, so NO app change is needed:
the resolver already calls {host}/{handle}/rss and rewrites permalinks to x.com.
Just keep OFFLINEFEED_NITTER_HOSTS = http://127.0.0.1:8081 (the default).

Setup & run: see README_PATH_B.md.

Deps: pip install twscrape   (Python 3.10+). Standard library otherwise.

FIX (X images cut off / only 1 of 2 showing):
  * _fetch_items now collects EVERY photo on a tweet (not just photos[0]).
  * _full_res_twimg() upgrades pbs.twimg.com URLs to name=orig so the picture
    is the FULL, uncropped original instead of a resized/cropped variant.
  * render_rss emits one <media:content> per image (+ all <img> in the
    description), so multi-photo tweets keep all their pictures.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, urlsplit, urlunsplit, parse_qsl, urlencode
from xml.sax.saxutils import escape

HOST = os.environ.get("TWSCRAPE_SHIM_HOST", "127.0.0.1")
PORT = int(os.environ.get("TWSCRAPE_SHIM_PORT", "8081"))
# Accounts DB created by `twscrape` (see README). Defaults to ./accounts.db.
ACCOUNTS_DB = os.environ.get("TWSCRAPE_ACCOUNTS_DB", "accounts.db")
LIMIT = int(os.environ.get("TWSCRAPE_SHIM_LIMIT", "40"))

import json

USER_ID_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(ACCOUNTS_DB)), "user_id_cache.json")
user_id_cache = {}

def load_user_id_cache():
    global user_id_cache
    if os.path.exists(USER_ID_CACHE_FILE):
        try:
            with open(USER_ID_CACHE_FILE, "r", encoding="utf-8") as f:
                user_id_cache = json.load(f)
            print(f"[shim] Loaded {len(user_id_cache)} user IDs from cache.")
        except Exception as e:
            print(f"[shim] Error loading user ID cache: {e}")

def save_user_id_cache():
    try:
        with open(USER_ID_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(user_id_cache, f, indent=4)
    except Exception as e:
        print(f"[shim] Error saving user ID cache: {e}")

load_user_id_cache()


def _full_res_twimg(url):
    """Return the FULL-resolution original for a pbs.twimg.com image URL.

    X serves cropped/resized variants via a `name=` query (e.g. name=small,
    name=360x360). Requesting name=orig yields the uncropped original. Non-twimg
    URLs are returned unchanged. Never raises.
    """
    try:
        if not url or "pbs.twimg.com" not in url:
            return url
        parts = urlsplit(url)
        q = dict(parse_qsl(parts.query))
        path = parts.path
        fmt = q.get("format")
        if not fmt:
            dot = path.rfind(".")
            if dot != -1:
                ext = path[dot + 1:].lower()
                if ext in ("jpg", "jpeg", "png", "webp"):
                    fmt = "jpg" if ext == "jpeg" else ext
                    path = path[:dot]
        q["name"] = "orig"
        if fmt:
            q["format"] = fmt
        return urlunsplit((parts.scheme, parts.netloc, path, urlencode(q), parts.fragment))
    except Exception:
        return url


async def get_user_id(api, handle):
    handle_key = handle.lower().strip()
    if handle_key in user_id_cache:
        return user_id_cache[handle_key]
    user = await api.user_by_login(handle)
    if user is None:
        return None
    user_id = user.id
    user_id_cache[handle_key] = user_id
    save_user_id_cache()
    return user_id


import threading
LOOP = asyncio.new_event_loop()

def _run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=_run_loop, args=(LOOP,), daemon=True).start()


def render_rss(handle, items):
    """Pure function: build an RSS 2.0 string from a list of normalized dicts.

    Each item dict: {id, text, url, date (aware datetime), thumb (str|None),
    thumbs (list[str])}. Kept dependency-free so it can be unit-tested offline.
    """
    now = format_datetime(datetime.now(timezone.utc))
    channel_link = "https://x.com/" + escape(handle)
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">',
        "  <channel>",
        "    <title>" + escape(handle) + " (X)</title>",
        "    <link>" + channel_link + "</link>",
        "    <description>Latest tweets from @" + escape(handle) + " via twscrape</description>",
        "    <lastBuildDate>" + now + "</lastBuildDate>",
    ]
    for it in items:
        text = it.get("text") or ""
        title = text.strip().replace("\n", " ")
        if len(title) > 140:
            title = title[:139] + "\u2026"
        if not title:
            title = "Tweet " + str(it.get("id", ""))
        url = it.get("url") or ("https://x.com/" + handle + "/status/" + str(it.get("id", "")))
        pub = it.get("date")
        pub_str = format_datetime(pub) if isinstance(pub, datetime) else now
        desc = escape(text or title)
        # FIX (multi-image): keep EVERY photo, not just the first one.
        imgs = it.get("thumbs")
        if not imgs:
            single = it.get("thumb")
            imgs = [single] if single else []
        if imgs:
            imgs_html = ""
            for im in imgs:
                if not im:
                    continue
                parts.append('      <media:content url="' + escape(im) + '" medium="image"/>')
                imgs_html += '&lt;img src="' + escape(im) + '"/&gt; '
            desc = imgs_html + desc
        parts.append("    <item>")
        parts.append("      <title>" + escape(title) + "</title>")
        parts.append("      <link>" + escape(url) + "</link>")
        parts.append('      <guid isPermaLink="true">' + escape(url) + "</guid>")
        parts.append("      <pubDate>" + pub_str + "</pubDate>")
        parts.append("      <description>" + desc + "</description>")
        parts.append("    </item>")
    parts.append("  </channel>")
    parts.append("</rss>")
    return "\n".join(parts)


async def _fetch_items(handle):
    """Fetch and normalize tweets for a handle via twscrape. Returns list|None."""
    from twscrape import API  # imported lazily so render_rss stays testable

    api = API(ACCOUNTS_DB)
    
    # 1. Resolve User ID
    user_id = await get_user_id(api, handle)
    if user_id is None:
        return None
        
    # 2. Check if any account is available for the UserTweets queue
    # If not, fail fast to avoid blocking the server / timing out!
    account = await api.pool.get_for_queue("UserTweets")
    if account is None:
        print(f"[shim] @{handle} -> No twscrape account available (rate limit). Failing fast.")
        return None
    # Unlock so the subsequent fetch can use it
    await api.pool.unlock(account.username, "UserTweets")

    # 3. Fetch tweets
    raw = []
    async for tweet in api.user_tweets(user_id, limit=LIMIT):
        # FIX (X images): capture ALL photos at FULL resolution (uncropped),
        # not just the first cropped thumbnail.
        imgs = []
        media = getattr(tweet, "media", None)
        photos = getattr(media, "photos", None) if media else None
        if photos:
            for p in photos:
                u = getattr(p, "url", None)
                if u:
                    imgs.append(_full_res_twimg(u))
        raw.append(
            {
                "id": getattr(tweet, "id", ""),
                "text": getattr(tweet, "rawContent", "") or "",
                "url": getattr(tweet, "url", "") or "",
                "date": getattr(tweet, "date", None),
                "thumb": imgs[0] if imgs else None,
                "thumbs": imgs,
            }
        )
    # Newest first (defensive: pinned/retweets can arrive out of order).
    raw.sort(
        key=lambda x: x["date"] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return raw


import time

rss_cache = {}  # maps handle.lower() -> (timestamp, body_bytes)
FETCH_LOCK = asyncio.Lock()

async def get_rss_feed_data(handle):
    handle_key = handle.lower()
    now = time.time()
    
    # 1. Check cache first
    if handle_key in rss_cache:
        ts, body = rss_cache[handle_key]
        if now - ts < 900:  # 15 minutes cache
            print(f"[shim] @{handle} -> CACHE HIT")
            return body
            
    # 2. Acquire lock to serialize fetching
    async with FETCH_LOCK:
        # Check cache again inside lock
        now = time.time()
        if handle_key in rss_cache:
            ts, body = rss_cache[handle_key]
            if now - ts < 900:
                print(f"[shim] @{handle} -> CACHE HIT (after lock)")
                return body
                
        print(f"[shim] @{handle} -> Fetching from Twitter...")
        items = await _fetch_items(handle)
        if items is None:
            return None
            
        body = render_rss(handle, items).encode("utf-8")
        rss_cache[handle_key] = (time.time(), body)
        print(f"[shim] @{handle} -> OK ({len(items)} tweets)")
        return body


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        segs = [p for p in path.split("/") if p]
        if len(segs) == 2 and segs[1].lower() == "rss":
            handle = segs[0]
            try:
                coro = get_rss_feed_data(handle)
                future = asyncio.run_coroutine_threadsafe(coro, LOOP)
                body = future.result()
            except Exception as e:  # surface as 502 so the resolver tries next host
                self._text(502, "twscrape error for @" + handle + ": " + str(e))
                print("[shim] @" + handle + " -> ERROR " + str(e), file=sys.stderr)
                return
            if body is None:
                self._text(404, "user @" + handle + " not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/rss+xml; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._text(404, "usage: GET /<handle>/rss")

    def _text(self, code, msg):
        body = msg.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # quiet; we print our own concise lines


def main():
    base = "http://" + HOST + ":" + str(PORT)
    print("twscrape RSS shim listening on " + base)
    print("  accounts db: " + ACCOUNTS_DB + "   per-feed limit: " + str(LIMIT))
    print("  try: curl " + base + "/nasa/rss")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
