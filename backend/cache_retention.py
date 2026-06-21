"""
cache_retention.py  --  OfflineFeed 14-day cached-post archiver (additive).

Goal: reclaim disk space by zipping cached posts whose REAL posting time is
older than N days (default 14), then deleting the loose originals -- while
keeping them retrievable (transparent restore when a post is reopened).

What is a "cached post"?
  * Article reader text : offline_viewer/assets/cached_articles/<md5>.json
  * Its images          : offline_viewer/assets/cached_images/<name>
                          (the feed thumbnail + any in-article images cached by
                           download_and_cache_image / media_cache)

How "posting time" is determined (per your choice):
  Join the cached article's url to the live feed snapshot (feed_cache.json),
  archived_posts.json and saved_posts.json, and use the same 'timestamp' the
  app already computes from each post's publish date. Falls back to the cache
  file's modified time only when no timestamp is known.

Safety:
  * A list thumbnail (any image referenced as an article 'thumbnail' in the
    feed/archived/saved stores) is NEVER deleted, so list views never break.
  * An image shared by a still-active (< N days) cached post is never deleted.
  * Reopening an archived post transparently restores it from the zip.
  * Everything is defensive (never raises into the caller) and dependency-free
    (stdlib zipfile/json/os only).

Drop this file next to gui_server.py (repo root) and wire it per WIRING.md.
"""
import os
import json
import time
import hashlib
import zipfile
import threading

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_BASE_DIR, "offline_viewer", "assets")
CACHED_ARTICLES_DIR = os.path.join(ASSETS_DIR, "cached_articles")
CACHED_IMAGES_DIR = os.path.join(ASSETS_DIR, "cached_images")
ARCHIVE_DIR = os.path.join(ASSETS_DIR, "cache_archive")
ARCHIVE_ZIP = os.path.join(ARCHIVE_DIR, "archived_posts.zip")

SNAPSHOT_PATH = os.path.join(ASSETS_DIR, "feed_cache.json")
ARCHIVED_POSTS_PATH = os.path.join(ASSETS_DIR, "archived_posts.json")
SAVED_POSTS_PATH = os.path.join(ASSETS_DIR, "saved_posts.json")

ARC_ARTICLES = "cached_articles"
ARC_IMAGES = "cached_images"

_retention_lock = threading.Lock()


def _clean(u):
    return (u or "").strip().lower()


def _md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _safe_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _iso_to_ts(s):
    if not s:
        return 0.0
    try:
        import datetime
        clean = str(s).split("+")[0].split("Z")[0].strip()
        return datetime.datetime.fromisoformat(clean).timestamp()
    except Exception:
        return 0.0


def _iter_articles_from(obj):
    """snapshot is {"articles":[...]}; archived/saved are bare lists."""
    if isinstance(obj, dict):
        arr = obj.get("articles") or []
    elif isinstance(obj, list):
        arr = obj
    else:
        arr = []
    for a in arr:
        if isinstance(a, dict):
            yield a


def _build_indexes():
    """Return (ts_by_url, thumb_by_url) gathered from all known article stores."""
    ts_by_url = {}
    thumb_by_url = {}
    for path in (SNAPSHOT_PATH, ARCHIVED_POSTS_PATH, SAVED_POSTS_PATH):
        data = _safe_load_json(path, None)
        for a in _iter_articles_from(data):
            url = _clean(a.get("url"))
            if not url:
                continue
            ts = a.get("timestamp")
            try:
                ts = float(ts) if ts else 0.0
            except Exception:
                ts = 0.0
            if not ts:
                ts = _iso_to_ts(a.get("archived_at"))
            if ts and ts > ts_by_url.get(url, 0.0):
                ts_by_url[url] = ts
            thumb = a.get("thumbnail")
            if thumb and url not in thumb_by_url:
                thumb_by_url[url] = thumb
    return ts_by_url, thumb_by_url


def _image_name_from(value):
    """If value points at assets/cached_images/<name>, return <name>, else None."""
    if not value or not isinstance(value, str):
        return None
    v = value.strip()
    if "cached_images/" in v and not v.startswith("http"):
        return os.path.basename(v)
    return None


def _images_for_post(article_json, url, thumb_by_url):
    names = set()
    n = _image_name_from(thumb_by_url.get(_clean(url)))
    if n:
        names.add(n)
    for b in (article_json.get("blocks") or []):
        if isinstance(b, dict) and b.get("type") == "img":
            n = _image_name_from(b.get("content"))
            if n:
                names.add(n)
    return names


def run_retention(max_age_days=14, now=None, log=None):
    """Zip + remove cached posts older than max_age_days. Returns a stats dict.

    log (optional): a callable(activity_type, details) -- pass
    gui_server.log_system_activity to surface progress in the Activity log.
    """
    stats = {"scanned": 0, "archived": 0, "zipped_images": 0,
             "freed_bytes": 0, "errors": 0}
    if not os.path.isdir(CACHED_ARTICLES_DIR):
        return stats

    with _retention_lock:
        now = now or time.time()
        cutoff = now - (max_age_days * 86400)
        ts_by_url, thumb_by_url = _build_indexes()

        loaded = {}   # filename -> json dict
        ages = {}     # filename -> resolved posting timestamp
        for fn in os.listdir(CACHED_ARTICLES_DIR):
            if not fn.endswith(".json"):
                continue
            stats["scanned"] += 1
            path = os.path.join(CACHED_ARTICLES_DIR, fn)
            data = _safe_load_json(path, None)
            if not isinstance(data, dict):
                continue
            loaded[fn] = data
            ts = ts_by_url.get(_clean(data.get("url") or ""), 0.0)
            if not ts:
                try:
                    ts = os.path.getmtime(path)
                except Exception:
                    ts = now  # unknown -> treat as fresh; never delete blindly
            ages[fn] = ts

        candidates = [fn for fn in loaded if ages.get(fn, now) < cutoff]
        if not candidates:
            return stats
        candidate_set = set(candidates)
        survivors = [fn for fn in loaded if fn not in candidate_set]

        # Images we must keep: referenced by a surviving cached post, OR used as
        # any list thumbnail (feed/archived/saved views).
        survivor_images = set()
        for fn in survivors:
            survivor_images |= _images_for_post(
                loaded[fn], loaded[fn].get("url", ""), thumb_by_url)
        for url, thumb in thumb_by_url.items():
            n = _image_name_from(thumb)
            if n:
                survivor_images.add(n)

        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        try:
            existing = set()
            if os.path.exists(ARCHIVE_ZIP):
                with zipfile.ZipFile(ARCHIVE_ZIP, "r") as zf:
                    existing = set(zf.namelist())

            with zipfile.ZipFile(ARCHIVE_ZIP, "a",
                                 compression=zipfile.ZIP_DEFLATED) as zf:
                for fn in candidates:
                    apath = os.path.join(CACHED_ARTICLES_DIR, fn)
                    arc_json = "{}/{}".format(ARC_ARTICLES, fn)
                    try:
                        img_names = _images_for_post(
                            loaded[fn], loaded[fn].get("url", ""), thumb_by_url)

                        # 1) write text json into the archive
                        if arc_json not in existing and os.path.exists(apath):
                            zf.write(apath, arc_json)
                            existing.add(arc_json)

                        # 2) write its images into the archive
                        for name in img_names:
                            ipath = os.path.join(CACHED_IMAGES_DIR, name)
                            arc_img = "{}/{}".format(ARC_IMAGES, name)
                            if os.path.exists(ipath) and arc_img not in existing:
                                zf.write(ipath, arc_img)
                                existing.add(arc_img)
                                stats["zipped_images"] += 1

                        # 3) delete loose json
                        try:
                            stats["freed_bytes"] += os.path.getsize(apath)
                        except Exception:
                            pass
                        if os.path.exists(apath):
                            os.remove(apath)
                        stats["archived"] += 1

                        # 4) delete loose images unique to archived posts
                        for name in img_names:
                            if name in survivor_images:
                                continue
                            ipath = os.path.join(CACHED_IMAGES_DIR, name)
                            try:
                                if os.path.exists(ipath):
                                    stats["freed_bytes"] += os.path.getsize(ipath)
                                    os.remove(ipath)
                            except Exception:
                                stats["errors"] += 1
                    except Exception:
                        stats["errors"] += 1
        except Exception as e:
            if log:
                try:
                    log("Cache Retention", "Archive failed: {}".format(e))
                except Exception:
                    pass
            return stats

        if log and stats["archived"]:
            try:
                log("Cache Retention",
                    "Archived {} posts (+{} images) older than {}d; freed ~{} KB".format(
                        stats["archived"], stats["zipped_images"],
                        max_age_days, stats["freed_bytes"] // 1024))
            except Exception:
                pass
        return stats


def restore_article(article_url):
    """If a post's loose cache was archived, extract it (and its images) back.

    Returns True if the loose cache json exists afterwards (already present or
    just restored), False otherwise. Safe + cheap to call on every open.
    """
    try:
        if not article_url:
            return False
        fn = "{}.json".format(_md5(article_url))
        loose = os.path.join(CACHED_ARTICLES_DIR, fn)
        if os.path.exists(loose):
            return True
        if not os.path.exists(ARCHIVE_ZIP):
            return False
        arc_json = "{}/{}".format(ARC_ARTICLES, fn)
        with zipfile.ZipFile(ARCHIVE_ZIP, "r") as zf:
            names = set(zf.namelist())
            if arc_json not in names:
                return False
            os.makedirs(CACHED_ARTICLES_DIR, exist_ok=True)
            data_bytes = zf.read(arc_json)
            with open(loose, "wb") as f:
                f.write(data_bytes)
            try:
                data = json.loads(data_bytes.decode("utf-8"))
            except Exception:
                data = {}
            os.makedirs(CACHED_IMAGES_DIR, exist_ok=True)
            for b in (data.get("blocks") or []):
                if isinstance(b, dict) and b.get("type") == "img":
                    n = _image_name_from(b.get("content"))
                    if not n:
                        continue
                    arc_img = "{}/{}".format(ARC_IMAGES, n)
                    dest = os.path.join(CACHED_IMAGES_DIR, n)
                    if arc_img in names and not os.path.exists(dest):
                        try:
                            with open(dest, "wb") as imf:
                                imf.write(zf.read(arc_img))
                        except Exception:
                            pass
        return True
    except Exception:
        return False
