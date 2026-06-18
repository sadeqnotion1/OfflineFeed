from __future__ import annotations
import os
import re
import urllib.parse
import json
from pathlib import Path
import concurrent.futures

# Try to import optional Pillow for image normalization
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Try to import requests, feedparser, and BeautifulSoup
try:
    import requests
    import feedparser
    from bs4 import BeautifulSoup
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

REPO_ROOT = Path(__file__).resolve().parent.parent
AVATARS_DIR = REPO_ROOT / "data" / "avatars"

def slugify(name: str) -> str:
    """Normalize source name into a safe file slug."""
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug or "channel"

def load_sources_file() -> list:
    """Load sources from custom_sources.json."""
    filepath = REPO_ROOT / "offline_viewer" / "assets" / "custom_sources.json"
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def save_sources_file(sources: list) -> None:
    """Save sources back to custom_sources.json."""
    filepath = REPO_ROOT / "offline_viewer" / "assets" / "custom_sources.json"
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(sources, indent=4, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

def fetch_avatar(source: dict, force: bool = False) -> Path | None:
    """Fetch and resolve an avatar for a source, saving it to data/avatars.

    Checks:
      (a) RSS feed <image> or logo/icon
      (b) HTML link rel="icon" or apple-touch-icon
      (c) HTML Open Graph og:image
      (d) site favicon.ico fallback
      (e) Google favicon service fallback
    """
    if not HAS_LIBS:
        return None

    name = source.get("name", "").strip()
    if not name:
        return None

    slug = slugify(name)

    # Check cached avatar
    if not force:
        for ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"):
            cached_path = AVATARS_DIR / f"{slug}{ext}"
            if cached_path.exists():
                return cached_path

    feed_url = source.get("url") or source.get("feed_url")
    if not feed_url:
        return None

    try:
        parsed = urllib.parse.urlparse(feed_url)
        domain = parsed.netloc
        site_url = f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    def try_download(img_url: str) -> Path | None:
        try:
            res = requests.get(img_url, headers=headers, timeout=5)
            if res.status_code != 200:
                return None

            ct = res.headers.get("Content-Type", "")
            if "html" in ct.lower():
                return None

            AVATARS_DIR.mkdir(parents=True, exist_ok=True)

            if HAS_PILLOW:
                import io
                try:
                    img = Image.open(io.BytesIO(res.content))
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")
                    img = img.resize((128, 128), Image.Resampling.LANCZOS)
                    out_path = AVATARS_DIR / f"{slug}.png"
                    img.save(out_path, "PNG")
                    return out_path
                except Exception:
                    pass

            # Fallback when Pillow is missing or normalization fails: save raw bytes
            ext = ".png"
            if "image/jpeg" in ct or "image/jpg" in ct:
                ext = ".jpg"
            elif "image/gif" in ct:
                ext = ".gif"
            elif "image/x-icon" in ct or "image/vnd.microsoft.icon" in ct:
                ext = ".ico"
            elif "image/svg+xml" in ct:
                ext = ".svg"
            else:
                p_url = urllib.parse.urlparse(img_url)
                u_ext = Path(p_url.path).suffix.lower()
                if u_ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"):
                    ext = u_ext

            out_path = AVATARS_DIR / f"{slug}{ext}"
            out_path.write_bytes(res.content)
            return out_path
        except Exception:
            return None

    # (a) RSS <image> / channel image
    try:
        feed_res = requests.get(feed_url, headers=headers, timeout=5)
        if feed_res.status_code == 200:
            d = feedparser.parse(feed_res.content)
            feed_img_url = None
            if d.feed:
                img_info = d.feed.get("image")
                if img_info and img_info.get("href"):
                    feed_img_url = img_info.get("href")
                elif d.feed.get("logo"):
                    feed_img_url = d.feed.get("logo")
                elif d.feed.get("icon"):
                    feed_img_url = d.feed.get("icon")

            if feed_img_url:
                feed_img_url = urllib.parse.urljoin(feed_url, feed_img_url)
                p = try_download(feed_img_url)
                if p:
                    return p
    except Exception:
        pass

    # Fetch site HTML for (b) link rel icon and (c) og:image
    site_html = None
    try:
        site_res = requests.get(site_url, headers=headers, timeout=5)
        if site_res.status_code == 200:
            site_html = site_res.content
    except Exception:
        pass

    if site_html:
        try:
            soup = BeautifulSoup(site_html, "html.parser")

            # (b) site <link rel="icon"> / apple-touch icon
            icon_urls = []
            for link in soup.find_all("link"):
                rel = [r.lower() for r in (link.get("rel") or [])]
                if any("icon" in r or "apple-touch" in r for r in rel):
                    href = link.get("href")
                    if href:
                        icon_urls.append(urllib.parse.urljoin(site_url, href))

            for url in icon_urls:
                p = try_download(url)
                if p:
                    return p

            # (c) Open Graph og:image
            og_urls = []
            for meta in soup.find_all("meta"):
                prop = meta.get("property") or ""
                m_name = meta.get("name") or ""
                if prop.lower() == "og:image" or m_name.lower() == "og:image":
                    content = meta.get("content")
                    if content:
                        og_urls.append(urllib.parse.urljoin(site_url, content))

            for url in og_urls:
                p = try_download(url)
                if p:
                    return p
        except Exception:
            pass

    # (d) favicon.ico
    favicon_url = f"{site_url}/favicon.ico"
    p = try_download(favicon_url)
    if p:
        return p

    # (e) Favicon service fallback
    fallback_url = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
    p = try_download(fallback_url)
    if p:
        return p

    return None

def backfill_avatars(refresh_avatars: bool = False) -> None:
    """Iterate persisted sources, fetch missing avatars, and save to sources.json.

    Runs fetches in parallel using ThreadPoolExecutor for fast non-blocking startup.
    """
    try:
        import debug
        log = debug.get_logger()
    except Exception:
        class DummyLogger:
            def info(self, *a, **k): print("[INFO]", *a)
            def error(self, *a, **k): print("[ERROR]", *a)
            def warning(self, *a, **k): print("[WARNING]", *a)
        log = DummyLogger()

    if not HAS_LIBS:
        log.warning("Required packages for avatar fetching are not installed.")
        return

    log.info("Starting channel avatar backfill pass...")
    sources = load_sources_file()
    if not sources:
        log.info("No sources found to backfill.")
        return

    updated = False
    targets = []

    for s in sources:
        name = s.get("name", "").strip()
        if not name:
            continue

        ap = s.get("avatar_path") or ""
        slug = slugify(name)

        cached_exists = False
        for ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"):
            if (AVATARS_DIR / f"{slug}{ext}").exists():
                cached_exists = True
                break

        needs_fetch = refresh_avatars or (not ap and not cached_exists)

        if needs_fetch:
            targets.append(s)
        elif not ap and cached_exists:
            # If no avatar_path in json but cached image exists, associate it
            for ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"):
                p = AVATARS_DIR / f"{slug}{ext}"
                if p.exists():
                    rel_path = p.relative_to(REPO_ROOT)
                    s["avatar_path"] = str(rel_path).replace("\\", "/")
                    updated = True
                    log.info("Associated cached avatar for %s -> %s", name, s["avatar_path"])
                    break

    if targets:
        log.info("Fetching %d avatars in parallel...", len(targets))
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(fetch_avatar, s, refresh_avatars): s for s in targets
            }
            for future in concurrent.futures.as_completed(future_to_source):
                s = future_to_source[future]
                name = s.get("name", "")
                try:
                    res_path = future.result()
                    if res_path:
                        rel_path = res_path.relative_to(REPO_ROOT)
                        s["avatar_path"] = str(rel_path).replace("\\", "/")
                        updated = True
                        log.info("Fetched avatar for %s -> %s", name, s["avatar_path"])
                    else:
                        log.warning("Could not resolve avatar for %s", name)
                except Exception as e:
                    log.error("Error fetching avatar for %s: %s", name, e)

    if updated:
        save_sources_file(sources)
        log.info("Sources file updated with avatars.")
    else:
        log.info("No avatars updated in this pass.")
