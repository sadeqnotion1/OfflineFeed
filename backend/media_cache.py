"""
media_cache.py  --  OfflineFeed in-article image caching (additive, drop-in).

Companion to the feed-thumbnail cache already in gui_server.py
(download_and_cache_image / download_feed_thumbnails_async). Where that one
caches the small list thumbnail, THIS one caches the images that appear INSIDE
an article body (the reader view), so an opened post renders fully offline.

Design goals:
  * Same on-disk scheme & filename as gui_server.download_and_cache_image, so the
    two caches share files and never duplicate work.
  * Hardened vs the original: atomic writes (tmp + os.replace), content-type and
    size validation, and it NEVER raises (failures fall back to the remote URL).
  * Zero new dependencies (uses 'requests', already used across gui_server.py).

Drop this file next to gui_server.py (repo root) and wire it per WIRING.md.
"""
import os
import hashlib
import urllib.parse

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_BASE_DIR, "offline_viewer", "assets")
CACHED_IMAGES_DIR = os.path.join(ASSETS_DIR, "cached_images")
REL_PREFIX = "assets/cached_images"

_IMG_EXTS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
_MAX_BYTES = 15 * 1024 * 1024  # 15 MB safety cap per image
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}


def _filename_for(url):
    """md5(url) + extension, mirroring gui_server.download_and_cache_image."""
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    parsed = urllib.parse.urlparse(url)
    ext = os.path.splitext(parsed.path)[1].lower()
    if ext not in _IMG_EXTS:
        ext = ".jpg"
    return "{}{}".format(url_hash, ext)


def _looks_like_image(data):
    """Cheap magic-byte sniff so we don't store HTML error pages as .jpg."""
    head = data[:16]
    sigs = (
        b"\xff\xd8\xff",            # jpeg
        b"\x89PNG\r\n\x1a\n",      # png
        b"GIF87a", b"GIF89a",       # gif
        b"RIFF",                    # webp (RIFF....WEBP)
        b"<svg", b"<?xml",          # svg
        b"BM",                      # bmp
    )
    return any(head.startswith(s) or s in head for s in sigs)


def download_and_cache_image(url, timeout=10):
    """Download one remote image; return its local relative path.

    Returns the ORIGINAL url unchanged on any failure, so callers/UI can still
    fall back to loading it online. Filename matches gui_server's scheme exactly,
    so the feed-thumbnail cache and this cache share the same files.
    """
    if not url or not url.startswith("http"):
        return url
    try:
        import requests
    except Exception:
        return url

    tmp_path = None
    try:
        filename = _filename_for(url)
        rel = "{}/{}".format(REL_PREFIX, filename)
        os.makedirs(CACHED_IMAGES_DIR, exist_ok=True)
        local_path = os.path.join(CACHED_IMAGES_DIR, filename)

        # Already cached (and non-empty) -> reuse, no network.
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            return rel

        r = requests.get(url, headers=_HEADERS, timeout=timeout)
        if r.status_code != 200:
            return url
        data = r.content or b""
        if not data:
            return url
        ctype = (r.headers.get("Content-Type") or "").lower()
        if not (ctype.startswith("image/") or _looks_like_image(data)):
            return url  # not actually an image (e.g. HTML error page)
        if len(data) > _MAX_BYTES:
            return url  # too big; keep streaming it online instead

        # Atomic write: never leave a half-written file that would be treated
        # as 'cached' forever.
        tmp_path = local_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(data)
        os.replace(tmp_path, local_path)
        tmp_path = None
        return rel
    except Exception as e:
        print("[media_cache] failed to cache image {}: {}".format(url, e))
        return url
    finally:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def localize_article_blocks(blocks):
    """Rewrite img blocks in-place to local cached paths; return the blocks.

    Each rewritten img block keeps its original remote URL under 'remote', so
    the UI can fall back online if a cached file is ever missing. Non-image and
    already-local blocks are left untouched. Never raises.
    """
    if not blocks:
        return blocks
    for b in blocks:
        try:
            if not isinstance(b, dict) or b.get("type") != "img":
                continue
            src = (b.get("content") or "").strip()
            if not src.startswith("http"):
                continue  # already local, or a data: URI -- leave as-is
            local = download_and_cache_image(src)
            if local and local != src:
                b["remote"] = src
                b["content"] = local
        except Exception:
            continue
    return blocks
