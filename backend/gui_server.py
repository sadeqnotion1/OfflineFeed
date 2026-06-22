import os
import json
import time
import re
import hashlib
import threading
import urllib.parse
import webbrowser
import email.utils
import datetime
import concurrent.futures
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import feed_store
import media_cache       # NEW: caches in-article images for true offline reading
import cache_retention   # NEW: 14-day cached-post archiver

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_viewer")

# Global Cache for Aggregated News
news_cache = {
    "data": [],
    "last_fetched": 0,
    "source_status": {}
}
news_cache_lock = threading.Lock()

def resolve_image_url(url_str, base_host):
    if not url_str:
        return ""
    url_str = url_str.strip()
    if url_str.startswith('data:'):
        return ""
    if url_str.startswith('//'):
        return 'https:' + url_str
    if url_str.startswith('/'):
        return base_host.rstrip('/') + '/' + url_str.lstrip('/')
    return url_str


def download_and_cache_image(url):
    if not url or not url.startswith("http"):
        return url
    try:
        import hashlib
        import urllib.parse
        import requests
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Determine extension
        parsed = urllib.parse.urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
            ext = '.jpg'  # fallback
            
        filename = f"{url_hash}{ext}"
        cache_dir = os.path.join(DIRECTORY, "assets", "cached_images")
        os.makedirs(cache_dir, exist_ok=True)
        local_path = os.path.join(cache_dir, filename)
        
        # If already exists, return local path
        if os.path.exists(local_path):
            return f"assets/cached_images/{filename}"
            
        # Download the image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            return f"assets/cached_images/{filename}"
    except Exception as e:
        print(f"[Image Cache] Failed to download image {url}: {e}")
    return url


def download_feed_thumbnails_async(articles, status_map):
    def worker():
        updated = False
        for art in articles:
            thumb = art.get("thumbnail")
            if thumb and thumb.startswith("http"):
                local_thumb = media_cache.download_and_cache_image(thumb)
                if local_thumb != thumb:
                    art["thumbnail"] = local_thumb
                    updated = True
        if updated:
            feed_store.save_feed_snapshot(articles, status_map)
            
    threading.Thread(target=worker, daemon=True).start()


def extract_img_url(img_el):
    if not img_el:
        return ""
    for attr in ['data-lazy-src', 'data-src', 'data-original', 'data-srcset', 'srcset', 'src']:
        val = img_el.get(attr)
        if val:
            val = val.strip()
            if attr in ['srcset', 'data-srcset']:
                parts = val.split(',')
                if parts:
                    val = parts[0].strip().split(' ')[0]
            if val and not val.startswith('data:') and not any(p in val.lower() for p in ['fallback.gif', 'placeholder.gif', 'placeholder.png', 'spacer.gif', 'pixel.gif']):
                return val
    return ""

def extract_title_for_anchor(a):
    title = ""
    heading = a.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if heading:
        title = heading.get_text().strip()
    if not title:
        parent_heading = a.find_parent(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if parent_heading:
            title = parent_heading.get_text().strip()
    if not title:
        headline_el = a.find(class_=lambda c: c and ('title' in c or 'headline' in c.lower()))
        if headline_el:
            title = headline_el.get_text().strip()
    if not title:
        img = a.find('img')
        if img and img.get('alt'):
            title = img.get('alt').strip()
    if not title:
        title = a.get_text().strip()
    if title:
        title = " ".join(title.split())
    return title

def find_thumbnail_for_anchor(a):
    img = a.find('img')
    if img:
        val = extract_img_url(img)
        if val:
            return val
    curr = a
    for _ in range(5):
        curr = curr.parent
        if not curr:
            break
        img = curr.find('img')
        if img:
            val = extract_img_url(img)
            if val:
                return val
        source = curr.find('source')
        if source:
            val = source.get('srcset') or source.get('data-srcset')
            if val:
                val = val.strip().split(',')[0].strip().split(' ')[0]
                if val and not val.startswith('data:'):
                    return val
    return ""

def parse_date_to_timestamp(date_str):
    if not date_str:
        return 0
    date_str = date_str.strip()
    
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        return int(dt.timestamp())
    except:
        pass
        
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d %H:%M:%S"]:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return int(dt.timestamp())
        except:
            pass
            
    return 0

def parse_xml_rss(content, source_name, category_default, feed_url=None):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'xml')
    
    base_host = "https://variety.com"
    if feed_url:
        parsed = urllib.parse.urlparse(feed_url)
        if parsed.scheme and parsed.netloc:
            base_host = f"{parsed.scheme}://{parsed.netloc}"
    else:
        channel_link = soup.find('channel')
        if channel_link:
            link_tag = channel_link.find('link')
            if link_tag and link_tag.text.strip():
                lnk = link_tag.text.strip()
                if lnk.startswith('http'):
                    parsed = urllib.parse.urlparse(lnk)
                    if parsed.scheme and parsed.netloc:
                        base_host = f"{parsed.scheme}://{parsed.netloc}"
        else:
            feed_el = soup.find('feed')
            if feed_el:
                link_tag = feed_el.find('link')
                if link_tag:
                    lnk = link_tag.get('href', '').strip() or link_tag.text.strip()
                    if lnk.startswith('http'):
                        parsed = urllib.parse.urlparse(lnk)
                        if parsed.scheme and parsed.netloc:
                            base_host = f"{parsed.scheme}://{parsed.netloc}"

    items = []
    for item in soup.find_all('item'):
        title_el = item.find('title')
        link_el = item.find('link')
        pub_el = item.find('pubDate') or item.find('dc:date')
        cat_el = item.find('category')
        
        title = title_el.text.strip() if title_el else ""
        link = link_el.text.strip() if link_el else ""
        pub_str = pub_el.text.strip() if pub_el else ""
        category = cat_el.text.strip() if cat_el else category_default
        
        if title.startswith("<![CDATA[") and title.endswith("]]>"):
            title = title[9:-3].strip()
        if category.startswith("<![CDATA[") and category.endswith("]]>"):
            category = category[9:-3].strip()
            
        thumbnail = ""
        media_content = item.find('media:content') or item.find('content')
        if media_content and media_content.get('url'):
            thumbnail = media_content.get('url')
        if not thumbnail:
            media_thumbnail = item.find('media:thumbnail')
            if media_thumbnail and media_thumbnail.get('url'):
                thumbnail = media_thumbnail.get('url')
        if not thumbnail:
            enclosure = item.find('enclosure')
            if enclosure and enclosure.get('url') and 'image' in (enclosure.get('type') or ''):
                thumbnail = enclosure.get('url')
        if not thumbnail:
            desc_el = item.find('description') or item.find('content:encoded')
            if desc_el:
                desc_text = desc_el.text
                if "<img" in desc_text:
                    try:
                        desc_soup = BeautifulSoup(desc_text, 'html.parser')
                        img = desc_soup.find('img')
                        if img and img.get('src'):
                            thumbnail = img.get('src')
                    except:
                        pass
        thumbnail = resolve_image_url(thumbnail, base_host)
        
        if title and link:
            items.append({
                "title": title,
                "url": link,
                "published": pub_str,
                "timestamp": parse_date_to_timestamp(pub_str),
                "source": source_name,
                "category": category or category_default,
                "thumbnail": thumbnail
            })
            
    if not items:
        for entry in soup.find_all('entry'):
            title_el = entry.find('title')
            link_el = entry.find('link')
            pub_el = entry.find('published') or entry.find('updated')
            cat_el = entry.find('category')
            
            title = title_el.text.strip() if title_el else ""
            link = ""
            if link_el:
                link = link_el.get('href', '').strip() or link_el.text.strip()
            pub_str = pub_el.text.strip() if pub_el else ""
            category = category_default
            if cat_el:
                category = cat_el.get('term', '').strip() or cat_el.text.strip()
                
            thumbnail = ""
            media_content = entry.find('media:content') or entry.find('content')
            if media_content and media_content.get('url'):
                thumbnail = media_content.get('url')
            if not thumbnail:
                media_thumbnail = entry.find('media:thumbnail')
                if media_thumbnail and media_thumbnail.get('url'):
                    thumbnail = media_thumbnail.get('url')
            if not thumbnail:
                for l in entry.find_all('link', rel='enclosure'):
                    if 'image' in (l.get('type') or ''):
                        thumbnail = l.get('href')
                        break
            if not thumbnail:
                sum_el = entry.find('summary') or entry.find('content')
                if sum_el:
                    sum_text = sum_el.text
                    if "<img" in sum_text:
                        try:
                            sum_soup = BeautifulSoup(sum_text, 'html.parser')
                            img = sum_soup.find('img')
                            if img and img.get('src'):
                                thumbnail = img.get('src')
                        except:
                            pass
            thumbnail = resolve_image_url(thumbnail, base_host)
            
            if title and link:
                items.append({
                    "title": title,
                    "url": link,
                    "published": pub_str,
                    "timestamp": parse_date_to_timestamp(pub_str),
                    "source": source_name,
                    "category": category or category_default,
                    "thumbnail": thumbnail
                })
    return items

def scrape_vulture_html(content, category_default):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    items_by_url = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/article/' in href and href.endswith('.html') and not 'about-us' in href:
            url = href
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://www.vulture.com' + url
                
            title = extract_title_for_anchor(a)
            if not title:
                continue
                
            thumbnail = find_thumbnail_for_anchor(a)
            thumbnail = resolve_image_url(thumbnail, "https://www.vulture.com")
            
            if url in items_by_url:
                existing = items_by_url[url]
                if len(title) > len(existing["title"]):
                    existing["title"] = title
                if thumbnail and not existing["thumbnail"]:
                    existing["thumbnail"] = thumbnail
            else:
                items_by_url[url] = {
                    "title": title,
                    "url": url,
                    "published": "",
                    "timestamp": 0,
                    "source": "Vulture",
                    "category": category_default,
                    "thumbnail": thumbnail
                }
    return [item for item in items_by_url.values() if len(item["title"]) > 5]

def scrape_screendaily_html(content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    items_by_url = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.article' in href:
            url = href
            if url.startswith('/'):
                url = 'https://www.screendaily.com' + url
            category = "Film"
            if '/reviews/' in href:
                category = "Reviews"
            elif '/features/' in href:
                category = "Features"
            elif '/news/' in href:
                category = "News"
                
            title = extract_title_for_anchor(a)
            if not title:
                continue
                
            thumbnail = find_thumbnail_for_anchor(a)
            thumbnail = resolve_image_url(thumbnail, "https://www.screendaily.com")
            
            if url in items_by_url:
                existing = items_by_url[url]
                if len(title) > len(existing["title"]):
                    existing["title"] = title
                if thumbnail and not existing["thumbnail"]:
                    existing["thumbnail"] = thumbnail
            else:
                items_by_url[url] = {
                    "title": title,
                    "url": url,
                    "published": "",
                    "timestamp": 0,
                    "source": "Screen Daily",
                    "category": category,
                    "thumbnail": thumbnail
                }
    return [item for item in items_by_url.values() if len(item["title"]) > 10 and not any(w in item["title"].lower() for w in ['subscribe', 'register', 'sign in'])]

def scrape_rt_html(content, category_default):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    items_by_url = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/article/' in href and not href.endswith('/article/app'):
            url = href
            if url.startswith('/'):
                url = 'https://editorial.rottentomatoes.com' + url
                
            title = extract_title_for_anchor(a)
            if not title:
                continue
                
            pub_date = ""
            text = a.get_text().strip()
            parts = [p.strip() for p in text.split('\n') if p.strip()]
            for part in parts:
                if re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', part):
                    pub_date = part
                    break
            if not pub_date:
                parent = a.parent
                if parent:
                    parent_text = parent.get_text()
                    date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', parent_text)
                    if date_match:
                        pub_date = date_match.group(0)
                        
            thumbnail = find_thumbnail_for_anchor(a)
            thumbnail = resolve_image_url(thumbnail, "https://editorial.rottentomatoes.com")
            
            if url in items_by_url:
                existing = items_by_url[url]
                if len(title) > len(existing["title"]):
                    existing["title"] = title
                if pub_date and not existing["published"]:
                    existing["published"] = pub_date
                    existing["timestamp"] = parse_date_to_timestamp(pub_date)
                if thumbnail and not existing["thumbnail"]:
                    existing["thumbnail"] = thumbnail
            else:
                items_by_url[url] = {
                    "title": title,
                    "url": url,
                    "published": pub_date,
                    "timestamp": parse_date_to_timestamp(pub_date),
                    "source": "Rotten Tomatoes",
                    "category": category_default,
                    "thumbnail": thumbnail
                }
    return [item for item in items_by_url.values() if len(item["title"]) > 5 and item["title"] != "RT App"]

def scrape_ew_html(content, category_default):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    items_by_url = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if any(p in href for p in ['/article/', '/movies/', '/tv/', '/music/', '/celebrity/']) and len(href) > 30:
            url = href
            if url.startswith('/'):
                url = 'https://ew.com' + url
                
            title = extract_title_for_anchor(a)
            if not title:
                continue
                
            thumbnail = find_thumbnail_for_anchor(a)
            thumbnail = resolve_image_url(thumbnail, "https://ew.com")
            
            if url in items_by_url:
                existing = items_by_url[url]
                if len(title) > len(existing["title"]):
                    existing["title"] = title
                if thumbnail and not existing["thumbnail"]:
                    existing["thumbnail"] = thumbnail
            else:
                items_by_url[url] = {
                    "title": title,
                    "url": url,
                    "published": "",
                    "timestamp": 0,
                    "source": "Entertainment Weekly",
                    "category": category_default,
                    "thumbnail": thumbnail
                }
    return [item for item in items_by_url.values() if len(item["title"]) > 10]

def scrape_telegram_html(content, category_default):
    from bs4 import BeautifulSoup
    import re
    import datetime
    soup = BeautifulSoup(content, 'html.parser')
    items = []
    
    messages = soup.find_all('div', class_='tgme_widget_message')
    for msg in messages:
        link_el = msg.find('a', class_='tgme_widget_message_date')
        url = link_el.get('href') if link_el else ""
        if not url:
            continue
            
        time_el = msg.find('time')
        published = time_el.get('datetime') if time_el else ""
        
        timestamp = 0
        if published:
            try:
                clean_date = published.split('+')[0].split('Z')[0]
                dt = datetime.datetime.fromisoformat(clean_date)
                timestamp = dt.timestamp()
            except:
                pass
                
        text_el = msg.find('div', class_='tgme_widget_message_text')
        if not text_el:
            continue
            
        full_text = text_el.text.strip()
        title = full_text.split('\n')[0].strip()
        if len(title) > 80:
            title = title[:77] + "..."
            
        description = full_text
        
        thumbnail = ""
        photo_el = msg.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_el:
            style = photo_el.get('style', '')
            m = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
            if m:
                thumbnail = m.group(1)
                
        if not thumbnail:
            lp_el = msg.find(class_='link_preview_image')
            if lp_el:
                style = lp_el.get('style', '')
                m = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                if m:
                    thumbnail = m.group(1)
                    
        if not thumbnail:
            for tag in msg.find_all(lambda t: t.has_attr('style') and 'background-image' in t['style']):
                if 'emoji' not in tag.get('class', []):
                    style = tag.get('style', '')
                    m = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
                    if m:
                        thumbnail = m.group(1)
                        break
                
        items.append({
            "title": title,
            "description": description,
            "url": url,
            "published": published,
            "timestamp": timestamp,
            "source": "Telegram",
            "category": category_default,
            "thumbnail": thumbnail
        })
    return items

def scrape_twitter_syndication(content, category_default):
    from bs4 import BeautifulSoup
    import json
    import email.utils
    
    soup = BeautifulSoup(content, 'html.parser')
    next_data_script = soup.find('script', id='__NEXT_DATA__')
    if not next_data_script:
        return []
        
    try:
        data = json.loads(next_data_script.string)
    except:
        return []
        
    page_props = data.get('props', {}).get('pageProps', {})
    timeline = page_props.get('timeline', {})
    entries = timeline.get('entries', [])
    
    items = []
    for entry in entries:
        if entry.get('type') != 'tweet':
            continue
            
        tweet = entry.get('content', {}).get('tweet', {})
        id_str = tweet.get('id_str')
        if not id_str:
            continue
            
        text = tweet.get('text') or tweet.get('full_text') or ""
        created_at = tweet.get('created_at')
        
        timestamp = 0
        published = ""
        if created_at:
            try:
                dt = email.utils.parsedate_to_datetime(created_at)
                timestamp = dt.timestamp()
                published = dt.isoformat()
            except:
                pass
                
        user = tweet.get('user', {})
        screen_name = user.get('screen_name') or "TwitterUser"
        tweet_url = f"https://x.com/{screen_name}/status/{id_str}"
        
        title = text.strip().split('\n')[0].strip()
        if len(title) > 80:
            title = title[:77] + "..."
        if not title:
            title = "Tweet by " + (user.get('name') or screen_name)
            
        description = text
        
        thumbnail = ""
        ext_entities = tweet.get('extended_entities', {})
        media_list = ext_entities.get('media', [])
        if not media_list:
            entities = tweet.get('entities', {})
            media_list = entities.get('media', [])
            
        if media_list:
            thumbnail = media_list[0].get('media_url_https') or media_list[0].get('media_url') or ""
            
        items.append({
            "title": title,
            "description": description,
            "url": tweet_url,
            "published": published,
            "timestamp": timestamp,
            "source": user.get('name') or "Twitter",
            "category": category_default,
            "thumbnail": thumbnail
        })
    return items

# ---------------------------------------------------------------------------
# X / Twitter timeline resolver
#
# Execution order (this matches the code below -- read it literally):
#   1. Nitter RSS FIRST: loop over each configured host and fetch
#      <nitter_host>/<handle>/rss, parsed with the EXISTING parse_xml_rss().
#      The first host that returns a non-empty feed wins; Nitter permalinks
#      are rewritten back to https://x.com/<path>.
#   2. Legacy syndication endpoint LAST (best-effort fallback only):
#      syndication.twitter.com/srv/timeline-profile/screen-name/<user> is
#      deprecated and almost always returns 0 tweets, so it is tried only
#      after every Nitter host has failed.
#
# Hosts come from the env var OFFLINEFEED_NITTER_HOSTS (comma-separated).
# Default = local self-hosted instance only; the public https://nitter.net is
# permanently dead and is intentionally NOT included by default.
# Per-host network timeout = OFFLINEFEED_NITTER_TIMEOUT seconds (default 8).
# ---------------------------------------------------------------------------
DEFAULT_NITTER_HOSTS = "http://127.0.0.1:8081"

def _parse_nitter_hosts(raw):
    """Trim, strip trailing slashes, drop blanks, and de-duplicate
    (order-preserving) a comma-separated list of Nitter hosts."""
    seen = set()
    hosts = []
    for h in (raw or "").split(","):
        h = h.strip().rstrip('/')
        if h and h not in seen:
            seen.add(h)
            hosts.append(h)
    return hosts

NITTER_HOSTS = _parse_nitter_hosts(
    os.environ.get("OFFLINEFEED_NITTER_HOSTS", DEFAULT_NITTER_HOSTS)
)

try:
    NITTER_TIMEOUT = float(os.environ.get("OFFLINEFEED_NITTER_TIMEOUT", "8"))
except (TypeError, ValueError):
    NITTER_TIMEOUT = 8.0

def twitter_screen_name(url):
    """Extract the @handle (screen name) from a twitter.com / x.com URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        parts = [p for p in parsed.path.split('/') if p]
        return parts[0] if parts else ""
    except Exception:
        return ""

def fetch_twitter_timeline(screen_name, headers, category_default):
    """
    Resolve an X timeline into the standard article-dict list.

    Strategy (listed in the order actually executed below):
      (a) PRIMARY  -- Nitter RSS: <nitter_host>/<handle>/rss for each configured
                      host, parsed with the EXISTING parse_xml_rss(). Nitter
                      permalinks are rewritten back to https://x.com so the UI
                      links to the real post. First non-empty host wins.
      (b) FALLBACK -- legacy syndication endpoint + scrape_twitter_syndication(),
                      tried only as a last resort (deprecated; usually empty).

    Each returned dict has keys: title, url, published, timestamp, source,
    category, thumbnail. Returns [] (with one clear log line) if all sources fail.
    """
    import requests

    if not screen_name:
        return []

    # (a) Nitter RSS FIRST (for live, up-to-date tweets).
    for host in NITTER_HOSTS:
        rss_url = f"{host}/{screen_name}/rss"
        try:
            r = requests.get(rss_url, headers=headers, timeout=NITTER_TIMEOUT)
            # 429 / 403 / 5xx / any non-200 is NOT fatal -- just try the next host.
            if r.status_code != 200:
                print(f"[Twitter] {host} -> HTTP {r.status_code} (trying next host)")
                continue
            items = parse_xml_rss(r.text, f"{screen_name} (X)", category_default, feed_url=rss_url)
            # Rewrite nitter permalinks back to the canonical x.com URL.
            for it in items:
                link = it.get("url", "")
                if link:
                    parsed = urllib.parse.urlparse(link)
                    it["url"] = "https://x.com" + parsed.path
            if items:
                print(f"[Twitter] @{screen_name} -> {host}: OK ({len(items)} tweets)")
                return items
            # Reachable host but no posts -> treat like a failure, try next host.
            print(f"[Twitter] {host} -> empty feed (trying next host)")
        except Exception as e:
            print(f"[Twitter] {host} -> {e} (trying next host)")
            continue

    # (b) Legacy syndication endpoint -- fallback best effort (may be stale).
    try:
        syn_url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{screen_name}"
        r = requests.get(syn_url, headers=headers, timeout=NITTER_TIMEOUT)
        if r.status_code == 200:
            items = scrape_twitter_syndication(r.text, category_default)
            if items:
                print(f"[Twitter] @{screen_name} -> syndication (fallback): OK ({len(items)} tweets)")
                return items
            print("[Twitter] syndication -> empty (deprecated endpoint)")
        else:
            print(f"[Twitter] syndication -> HTTP {r.status_code}")
    except Exception as e:
        print(f"[Twitter] syndication endpoint -> {e}")

    print(f"[Twitter] @{screen_name}: ALL sources FAILED "
          f"(Nitter hosts tried: {NITTER_HOSTS or 'none configured'}); 0 tweets.")
    return []

def scrape_thr_html(content, category_default):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    items_by_url = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if ('hollywoodreporter.com/' in href or href.startswith('/')) and any(x in href for x in ['/movies/', '/tv/', '/business/', '/lifestyle/', '/news/']) and len(href) > 50:
            url = href
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://www.hollywoodreporter.com' + url
                
            title = extract_title_for_anchor(a)
            if not title:
                continue
                
            thumbnail = find_thumbnail_for_anchor(a)
            thumbnail = resolve_image_url(thumbnail, "https://www.hollywoodreporter.com")
            
            if url in items_by_url:
                existing = items_by_url[url]
                if len(title) > len(existing["title"]):
                    existing["title"] = title
                if thumbnail and not existing["thumbnail"]:
                    existing["thumbnail"] = thumbnail
            else:
                items_by_url[url] = {
                    "title": title,
                    "url": url,
                    "published": "",
                    "timestamp": 0,
                    "source": "The Hollywood Reporter",
                    "category": category_default,
                    "thumbnail": thumbnail
                }
    return [item for item in items_by_url.values() if len(item["title"]) > 10 and not any(w in item["title"].lower() for w in ['subscribe', 'sign in', 'register', 'features', 'reviews', 'videos', 'news'])]

def scrape_generic_html_index(content, base_url, category_default):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    parsed_base = urllib.parse.urlparse(base_url)
    base_host = f"{parsed_base.scheme}://{parsed_base.netloc}"
    
    items_by_url = {}
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
            
        url = resolve_image_url(href, base_host)
        
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.netloc != parsed_base.netloc:
            continue
            
        path = parsed_url.path.rstrip('/')
        path_lower = path.lower()
        
        # Skip typical non-article pages
        skip_keywords = [
            '/category/', '/tag/', '/author/', '/search', '/page/', '/about', '/contact', 
            '/privacy', '/terms', '/cookies', '/wp-admin', '/wp-login', '/subscribe', 
            '/register', '/member', '/login', '/signup', '/sign-in', '/sign-out'
        ]
        if any(kw in path_lower for kw in skip_keywords):
            continue
            
        segments = [s for s in path.split('/') if s]
        if not segments:
            continue
            
        title = extract_title_for_anchor(a)
        if not title:
            continue
            
        words = title.split()
        if len(words) < 3 or len(title) < 15:
            continue
            
        if any(w in title.lower() for w in ['subscribe', 'sign in', 'log in', 'register', 'privacy policy', 'terms of use']):
            continue
            
        pub_date = ""
        parent = a.parent
        if parent:
            parent_text = parent.get_text()
            date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', parent_text)
            if not date_match:
                date_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', parent_text)
            if date_match:
                pub_date = date_match.group(0)
                
        thumbnail = find_thumbnail_for_anchor(a)
        thumbnail = resolve_image_url(thumbnail, base_host)
        
        if url in items_by_url:
            existing = items_by_url[url]
            if len(title) > len(existing["title"]):
                existing["title"] = title
            if pub_date and not existing["published"]:
                existing["published"] = pub_date
                existing["timestamp"] = parse_date_to_timestamp(pub_date)
            if thumbnail and not existing["thumbnail"]:
                existing["thumbnail"] = thumbnail
        else:
            items_by_url[url] = {
                "title": title,
                "url": url,
                "published": pub_date,
                "timestamp": parse_date_to_timestamp(pub_date),
                "source": "Custom HTML Source",
                "category": category_default,
                "thumbnail": thumbnail
            }
            
    res_list = list(items_by_url.values())
    res_list = res_list[:25]
    return res_list

def load_custom_sources():
    filepath = os.path.join(DIRECTORY, "assets", "custom_sources.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading custom sources: {e}")
    return []

def load_default_sources_avatars_map():
    filepath = os.path.join(DIRECTORY, "assets", "avatars", "index.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_custom_sources(sources):
    filepath = os.path.join(DIRECTORY, "assets", "custom_sources.json")
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving custom sources: {e}")

def get_default_activities():
    now = time.time()
    return [
        {
            "timestamp": now - 3600,
            "type": "Feed Aggregator",
            "details": "Aggregator initialized. Default cinema feeds loaded."
        }
    ]

log_lock = threading.Lock()

def log_system_activity(activity_type, details):
    print(f"[{activity_type}] {details}")
    log_file = os.path.join(DIRECTORY, "assets", "activity_log.json")
    with log_lock:
        history = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                pass
                
        if not history:
            history = get_default_activities()
            
        history.insert(0, {
            "timestamp": time.time(),
            "type": activity_type,
            "details": details
        })
        
        history = history[:100]
        
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4)
        except Exception as e:
            print(f"Error logging activity: {e}")

def get_clean_site_name(name):
    name_lower = name.lower()
    if "variety" in name_lower:
        return "Variety"
    if "hollywood reporter" in name_lower or "thr" in name_lower:
        return "The Hollywood Reporter"
    if "vulture" in name_lower:
        return "Vulture"
    if "entertainment weekly" in name_lower or "ew.com" in name_lower:
        return "Entertainment Weekly"
    if "screen daily" in name_lower:
        return "Screen Daily"
    if "rotten tomatoes" in name_lower:
        return "Rotten Tomatoes"
    if "deadline" in name_lower:
        return "Deadline Hollywood"
    if "collider" in name_lower:
        return "Collider"
    if "rogerebert" in name_lower or "roger ebert" in name_lower:
        return "RogerEbert.com"
    if "avclub" in name_lower or "av club" in name_lower or "a.v. club" in name_lower:
        return "The A.V. Club"
    if "letterboxd" in name_lower:
        return "Letterboxd Journal"
    if "little white lies" in name_lower or "lwlies" in name_lower:
        return "Little White Lies"
    if "empireonline" in name_lower or "empire magazine" in name_lower:
        return "Empire Magazine"
    if "cinemablend" in name_lower:
        return "CinemaBlend"
    if "espn" in name_lower:
        return "ESPN News"
    if "bbc" in name_lower:
        return "BBC Sport"
    if "sky sports" in name_lower:
        return "Sky Sports News"
    if "techcrunch" in name_lower:
        return "TechCrunch"
    if "wired" in name_lower:
        return "Wired Tech"
    if "the verge" in name_lower:
        return "The Verge"
    return name

def fetch_single_source(source_tuple):
    import requests
    import time
    
    if len(source_tuple) == 5:
        name, url, category_default, is_rss, section = source_tuple
    elif len(source_tuple) == 4:
        name, url, category_default, is_rss = source_tuple
        section = "Entertainment"
    else:
        name, url, category_default = source_tuple
        is_rss = True
        section = "Entertainment"
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    fetch_url = url
    # X / Twitter sources are resolved through fetch_twitter_timeline(), which
    # tries the legacy syndication endpoint and then falls back to Nitter RSS.
    if "twitter.com/" in fetch_url or "x.com/" in fetch_url:
        screen_name = twitter_screen_name(fetch_url)
        items = fetch_twitter_timeline(screen_name, headers, category_default)
        clean_name = get_clean_site_name(name)
        # Phase 2 - Task 4 (correct X/Twitter avatar): resolve the avatar from the
        # specific @handle rather than the generic x.com site favicon. unavatar
        # maps a handle deterministically to its real profile image.
        avatar_url = f"https://unavatar.io/x/{screen_name}" if screen_name else ""
        for item in items:
            item["source"] = clean_name
            item["topic"] = item.get("category") or category_default
            item["section"] = section
            if avatar_url:
                item["handle"] = screen_name
                item["avatar"] = avatar_url
        status_type = "Twitter" if items else "Failed (no tweets)"
        return {"source": clean_name, "status": status_type, "items": items}
            
    if name == "Vulture main feed" and url == "https://www.vulture.com/feed/":
        fetch_url = "https://feeds.feedburner.com/nymag/vulture"
        
    try:
        r = requests.get(fetch_url, headers=headers, timeout=8)
        print(f"[News Aggregator] Fetched {name} ({fetch_url}) -> Status Code: {r.status_code}")
        
        if r.status_code in [403, 401]:
            print(f"[News Aggregator] Blocked ({r.status_code}) for {name}.")
        
        if r.status_code != 200:
            clean_name = get_clean_site_name(name)
            return {"source": clean_name, "status": f"Failed (HTTP {r.status_code})", "items": []}
            
        content_str = r.text
        if is_rss:
            items = parse_xml_rss(content_str, name, category_default, feed_url=fetch_url)
            status_type = "RSS"
        else:
            if "t.me/s/" in fetch_url:
                items = scrape_telegram_html(content_str, category_default)
            elif "vulture.com" in fetch_url:
                items = scrape_vulture_html(content_str, category_default)
            elif "screendaily.com" in fetch_url:
                items = scrape_screendaily_html(content_str)
            elif "rottentomatoes.com" in fetch_url:
                items = scrape_rt_html(content_str, category_default)
            elif "ew.com" in fetch_url:
                items = scrape_ew_html(content_str, category_default)
            elif "hollywoodreporter.com" in fetch_url:
                items = scrape_thr_html(content_str, category_default)
            else:
                items = scrape_generic_html_index(content_str, fetch_url, category_default)
            status_type = "HTML"
            
        clean_name = get_clean_site_name(name)
        for item in items:
            item["source"] = clean_name
            item["topic"] = item.get("category") or category_default
            item["section"] = section
            
        return {"source": clean_name, "status": status_type, "items": items}
            
    except Exception as e:
        print(f"[News Aggregator] Error fetching {name}: {e}")
        clean_name = get_clean_site_name(name)
        return {"source": clean_name, "status": f"Failed ({str(e)})", "items": []}

def load_ignored_posts():
    filepath = os.path.join(DIRECTORY, "assets", "ignored_posts.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                urls = json.load(f)
                return {u.lower().strip() for u in urls if isinstance(u, str)}
        except Exception as e:
            print(f"Error loading ignored posts: {e}")
    return set()

def save_ignored_post(url):
    filepath = os.path.join(DIRECTORY, "assets", "ignored_posts.json")
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        ignored = load_ignored_posts()
        ignored.add(url.lower().strip())
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(list(ignored), f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving ignored post: {e}")

def load_telegram_config():
    filepath = os.path.join(DIRECTORY, "assets", "telegram_config.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading Telegram config: {e}")
    return {"bot_token": "", "default_chat_id": "", "category_threads": {}}

def save_telegram_config(config):
    filepath = os.path.join(DIRECTORY, "assets", "telegram_config.json")
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving Telegram config: {e}")

saved_posts_lock = threading.Lock()
archived_posts_lock = threading.Lock()

def get_article_key(art):
    url = art.get("url") or ""
    url_clean = url.strip()
    if url_clean:
        return url_clean
    title = art.get("title") or ""
    import hashlib
    return "hash:" + hashlib.sha256(title.encode('utf-8')).hexdigest()

def load_saved_posts():
    with saved_posts_lock:
        filepath = os.path.join(DIRECTORY, "assets", "saved_posts.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading saved posts: {e}")
        return []

def save_saved_posts(posts):
    with saved_posts_lock:
        filepath = os.path.join(DIRECTORY, "assets", "saved_posts.json")
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving saved posts: {e}")

def load_archived_posts():
    with archived_posts_lock:
        filepath = os.path.join(DIRECTORY, "assets", "archived_posts.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading archived posts: {e}")
        return []

def save_archived_posts(posts):
    with archived_posts_lock:
        filepath = os.path.join(DIRECTORY, "assets", "archived_posts.json")
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving archived posts: {e}")

def archive_removed_posts(old_articles, new_articles):
    if not old_articles:
        return
        
    new_urls = {art.get("url", "").lower().strip() for art in new_articles if art.get("url")}
    new_titles = {art.get("title", "").lower().strip() for art in new_articles if art.get("title")}
    
    removed_posts = []
    
    for art in old_articles:
        url = art.get("url", "").lower().strip()
        title = art.get("title", "").lower().strip()
        
        if not url and not title:
            continue
            
        is_removed = False
        if url and url not in new_urls:
            is_removed = True
        elif not url and title and title not in new_titles:
            is_removed = True
            
        if is_removed:
            removed_posts.append(art)
            
    if removed_posts:
        archived = load_archived_posts()
        archived_keys = {get_article_key(p) for p in archived}
        
        import datetime
        now_str = datetime.datetime.now().isoformat()
        
        added_count = 0
        for art in removed_posts:
            art_key = get_article_key(art)
            if art_key not in archived_keys:
                archived_art = art.copy()
                archived_art["archived_at"] = now_str
                archived_art["reason"] = "removed_from_feed"
                archived.insert(0, archived_art)
                archived_keys.add(art_key)
                added_count += 1
                
        if added_count > 0:
            save_archived_posts(archived)
            log_system_activity("Feed Harvester", f"Archived {added_count} posts removed from the feed")

sent_posts_lock = threading.Lock()

def load_sent_posts():
    with sent_posts_lock:
        filepath = os.path.join(DIRECTORY, "assets", "sent_posts.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    urls = json.load(f)
                    return {u.lower().strip() for u in urls if isinstance(u, str)}
            except Exception as e:
                print(f"Error loading sent posts: {e}")
        return set()

def save_sent_post(url):
    filepath = os.path.join(DIRECTORY, "assets", "sent_posts.json")
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with sent_posts_lock:
            sent = set()
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        urls = json.load(f)
                        sent = {u.lower().strip() for u in urls if isinstance(u, str)}
                except:
                    pass
            sent.add(url.lower().strip())
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(list(sent), f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving sent post: {e}")

def telegram_post_request(api_url, payload):
    import requests
    import time
    max_retries = 10
    for attempt in range(max_retries):
        try:
            r = requests.post(api_url, json=payload, timeout=15)
            res = r.json()
            if res.get("ok"):
                return res
            
            error_code = res.get("error_code")
            description = res.get("description", "")
            
            if error_code == 429 or "too many requests" in description.lower():
                retry_after = res.get("parameters", {}).get("retry_after", 5)
                if not retry_after and "retry after" in description.lower():
                    try:
                        retry_after = int(re.search(r'retry after (\d+)', description.lower()).group(1))
                    except:
                        retry_after = 5
                
                print(f"[Telegram poster] Rate limit hit. Sleeping for {retry_after + 1}s before retry (Attempt {attempt+1}/{max_retries})...")
                time.sleep(retry_after + 1)
                continue
            else:
                return res
        except Exception as e:
            if attempt == max_retries - 1:
                return {"ok": False, "description": f"Network exception: {str(e)}"}
            time.sleep(2)
    return {"ok": False, "description": "Max rate-limit retries exceeded"}

import queue

telegram_job_queue = queue.Queue()
telegram_worker_thread = None
telegram_queue_lock = threading.Lock()

TELEGRAPH_API = "https://api.telegra.ph"
_telegraph_token = None

def get_telegraph_token():
    global _telegraph_token
    if _telegraph_token:
        return _telegraph_token
    
    token_file = os.path.join(DIRECTORY, "assets", "telegraph_token.json")
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _telegraph_token = data.get("access_token")
                if _telegraph_token:
                    return _telegraph_token
        except Exception as e:
            log_system_activity("Telegraph", f"Failed to load telegraph token from file: {e}")
            
    import requests
    try:
        url = f"{TELEGRAPH_API}/createAccount"
        payload = {
            "short_name": "OfflineFeed",
            "author_name": "OfflineFeed"
        }
        r = requests.post(url, json=payload, timeout=15)
        res = r.json()
        if res.get("ok"):
            _telegraph_token = res["result"].get("access_token")
            try:
                os.makedirs(os.path.dirname(token_file), exist_ok=True)
                with open(token_file, 'w', encoding='utf-8') as f:
                    json.dump({"access_token": _telegraph_token}, f, indent=4)
            except Exception as e:
                log_system_activity("Telegraph", f"Failed to save telegraph token to file: {e}")
            return _telegraph_token
        else:
            log_system_activity("Telegraph", f"createAccount API error: {res.get('description')}")
    except Exception as e:
        log_system_activity("Telegraph", f"Network error during telegraph createAccount: {str(e)}")
        
    return None

def blocks_to_telegraph_nodes(blocks, source_url=""):
    nodes = []
    if blocks:
        for b in blocks:
            b_type = b.get("type")
            b_content = b.get("content", "").strip()
            if not b_content:
                continue
                
            if b_type == "p":
                nodes.append({"tag": "p", "children": [b_content]})
            elif b_type == "h":
                nodes.append({"tag": "h3", "children": [b_content]})
            elif b_type == "quote":
                nodes.append({"tag": "blockquote", "children": [b_content]})
            elif b_type == "img":
                nodes.append({
                    "tag": "figure",
                    "children": [
                        {
                            "tag": "img",
                            "attrs": {"src": b_content}
                        }
                    ]
                })
                
    if source_url:
        nodes.append({
            "tag": "p",
            "children": [
                {
                    "tag": "a",
                    "attrs": {"href": source_url},
                    "children": ["Original Article"]
                }
            ]
        })
    return nodes

def create_telegraph_page(title, blocks, author_name, source_url):
    token = get_telegraph_token()
    if not token:
        log_system_activity("Telegraph", "Cannot create page: no access token available")
        return None
        
    nodes = blocks_to_telegraph_nodes(blocks, source_url)
    
    # Check if nodes is empty or only contains the source_url link
    has_content = False
    if blocks:
        for b in blocks:
            if b.get("content", "").strip():
                has_content = True
                break
    if not has_content or not nodes:
        log_system_activity("Telegraph", "Cannot create page: empty content nodes")
        return None
        
    import requests
    try:
        if len(title) > 256:
            title = title[:256]
            
        payload = {
            "access_token": token,
            "title": title,
            "author_name": author_name or "OfflineFeed",
            "content": json.dumps(nodes),
            "return_content": False
        }
        r = requests.post(f"{TELEGRAPH_API}/createPage", json=payload, timeout=15)
        res = r.json()
        if res.get("ok"):
            return res["result"].get("url")
        else:
            log_system_activity("Telegraph", f"Failed to create page '{title[:40]}...': {res.get('description')}")
    except Exception as e:
        log_system_activity("Telegraph", f"Network error creating page '{title[:40]}...': {str(e)}")
    return None

def process_channel_send_job(channel_name, to_send, bot_token, default_chat_id, sports_chat_id, technology_chat_id, channel_threads, already_sent_count):
    log_system_activity("Telegram poster", f"Starting broadcast of {len(to_send)} new posts from {channel_name} ({already_sent_count} skipped as already sent)")
    sent_count = 0
    error_count = 0
    
    for art in to_send:
        title = art.get("title", "")
        description = art.get("description", "")
        url = art.get("url", "")
        thumbnail_url = art.get("thumbnail", "")
        category = art.get("category", "")
        section = art.get("section", "Entertainment").strip().lower()
        
        chat_id = default_chat_id
        if section == "sports" and sports_chat_id:
            chat_id = sports_chat_id
        elif section == "technology" and technology_chat_id:
            chat_id = technology_chat_id
            
        thread_id = None
        
        if channel_name and channel_threads.get(channel_name):
            thread_id = channel_threads[channel_name].strip()
            
        import html
        
        title_esc = html.escape(title)
        category_esc = html.escape(category) if category else ""
        description_esc = html.escape(description) if description else ""
        url_esc = html.escape(url)
        
        caption = f"📣 <b>{title_esc}</b>\n"
        if category_esc:
            caption += f"#{category_esc.replace(' ', '_')}\n"
        caption += "\n"
        if description_esc:
            caption += f"{description_esc}\n\n"
        caption += f"🔗 <a href=\"{url_esc}\">Read Article</a>"
        
        # Fetch the offline content blocks first to collect all inline images
        log_system_activity("Telegram poster", f"Fetching full offline content for '{title[:40]}...'")
        blocks = get_article_content_blocks(url)
        
        # Create telegraph page and append link
        telegraph_url = create_telegraph_page(title, blocks, author_name=channel_name, source_url=url)
        if telegraph_url:
            telegraph_html = f"\n\n <a href=\"{telegraph_url}\">Read full post</a>"
            if len(caption) + len(telegraph_html) > 1024:
                caption = caption[:(1020 - len(telegraph_html))] + "..."
            caption += telegraph_html
        else:
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
        
        # Collect all unique images
        inline_images = []
        if blocks:
            for b in blocks:
                if b.get("type") == "img" and b.get("content"):
                    img_url = b.get("content").strip()
                    if img_url.startswith("http") and img_url not in inline_images:
                        inline_images.append(img_url)
                        
        all_images = []
        seen_clean = set()
        if thumbnail_url and thumbnail_url.startswith("http"):
            thumb_strip = thumbnail_url.strip()
            all_images.append(thumb_strip)
            parsed = urllib.parse.urlparse(thumb_strip)
            clean_url = (parsed.netloc + parsed.path).lower()
            seen_clean.add(clean_url)
            
        for img in inline_images:
            parsed = urllib.parse.urlparse(img)
            clean_url = (parsed.netloc + parsed.path).lower()
            if clean_url not in seen_clean:
                all_images.append(img)
                seen_clean.add(clean_url)
                
        # Limit to 10 photos max (Telegram sendMediaGroup limit)
        all_images = all_images[:10]
        
        main_message_id = None
        success = False
        sent_successfully = False
        sent_as_media_group = False
        last_error = "No attempt made"
        
        # Try sending as media group if we have 2 or more images
        if len(all_images) >= 2:
            media_group = []
            for i, img in enumerate(all_images):
                media_item = {
                    "type": "photo",
                    "media": img
                }
                if i == 0:
                    media_item["caption"] = caption
                    media_item["parse_mode"] = "HTML"
                media_group.append(media_item)
                
            payload = {
                "chat_id": chat_id,
                "media": media_group
            }
            if thread_id:
                try:
                    payload["message_thread_id"] = int(thread_id)
                except ValueError:
                    pass
            
            api_url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
            try:
                res = telegram_post_request(api_url, payload)
                if res.get("ok"):
                    success = True
                    sent_successfully = True
                    sent_as_media_group = True
                    sent_count += 1
                    save_sent_post(url)
                    # For sendMediaGroup, the result is an array of messages. We reply to the first message.
                    main_message_id = res.get("result", [{}])[0].get("message_id")
                    log_system_activity("Telegram poster", f"Sent post as media group with {len(all_images)} images: '{title[:40]}...'")
                else:
                    last_error = res.get("description", "Unknown API error")
                    log_system_activity("Telegram poster", f"sendMediaGroup failed for '{title[:40]}...': {last_error}. Retrying with sendPhoto fallback...")
            except Exception as e:
                last_error = str(e)
                log_system_activity("Telegram poster", f"sendMediaGroup error for '{title[:40]}...': {last_error}. Retrying with sendPhoto fallback...")

        # If not sent as media group, try single photo sendPhoto fallback
        if not success and thumbnail_url and thumbnail_url.startswith("http"):
            payload = {
                "chat_id": chat_id,
                "parse_mode": "HTML",
                "photo": thumbnail_url,
                "caption": caption
            }
            if thread_id:
                try:
                    payload["message_thread_id"] = int(thread_id)
                except ValueError:
                    pass
            api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            try:
                res = telegram_post_request(api_url, payload)
                if res.get("ok"):
                    success = True
                    sent_successfully = True
                    sent_count += 1
                    save_sent_post(url)
                    main_message_id = res.get("result", {}).get("message_id")
                    log_system_activity("Telegram poster", f"Sent post with single image: '{title[:40]}...'")
                else:
                    last_error = res.get("description", "Unknown API error")
            except Exception as e:
                last_error = str(e)
                
        # If still not successful, try text fallback
        if not success:
            payload = {
                "chat_id": chat_id,
                "parse_mode": "HTML",
                "text": caption
            }
            if thread_id:
                try:
                    payload["message_thread_id"] = int(thread_id)
                except ValueError:
                    pass
            api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            try:
                res = telegram_post_request(api_url, payload)
                if res.get("ok"):
                    sent_successfully = True
                    sent_count += 1
                    save_sent_post(url)
                    main_message_id = res.get("result", {}).get("message_id")
                    log_system_activity("Telegram poster", f"Sent post (text fallback): '{title[:40]}...'")
                else:
                    error_msg = res.get("description", last_error)
                    log_system_activity("Telegram poster", f"Failed to send '{title[:40]}...': {error_msg}")
                    error_count += 1
            except Exception as e:
                log_system_activity("Telegram poster", f"Network error sending '{title[:40]}...': {str(e)}")
                error_count += 1
                
        if sent_successfully:
            # Save markdown backup locally
            save_markdown_backup(channel_name, title, url, thumbnail_url, blocks)
        time.sleep(0.5)
        
    log_system_activity("Telegram poster", f"Finished broadcast for {channel_name}: Sent {sent_count} successfully, {error_count} failed.")

def telegram_queue_worker_loop():
    print("[Telegram Queue] Worker thread started.")
    while True:
        try:
            job = telegram_job_queue.get()
            if job is None:
                break
            
            channel_name = job.get("channel_name")
            to_send = job.get("to_send")
            bot_token = job.get("bot_token")
            default_chat_id = job.get("default_chat_id")
            sports_chat_id = job.get("sports_chat_id")
            technology_chat_id = job.get("technology_chat_id")
            channel_threads = job.get("channel_threads")
            already_sent_count = job.get("already_sent_count")
            
            process_channel_send_job(channel_name, to_send, bot_token, default_chat_id, sports_chat_id, technology_chat_id, channel_threads, already_sent_count)
            
            telegram_job_queue.task_done()
        except Exception as e:
            print(f"[Telegram Queue] Error in loop: {e}")
            time.sleep(2)

def start_telegram_queue_worker():
    global telegram_worker_thread
    with telegram_queue_lock:
        if telegram_worker_thread is None or not telegram_worker_thread.is_alive():
            telegram_worker_thread = threading.Thread(target=telegram_queue_worker_loop, daemon=True)
            telegram_worker_thread.start()

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

def save_markdown_backup(channel_name, title, url, thumbnail_url, blocks):
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_backups", sanitize_filename(channel_name))
        os.makedirs(backup_dir, exist_ok=True)
        
        # Limit title to 60 characters for filename safety
        safe_title = sanitize_filename(title)[:60]
        filename = f"{int(time.time())}_{safe_title}.md"
        filepath = os.path.join(backup_dir, filename)
        
        md_content = f"# {title}\n\n"
        md_content += f"- **Original URL:** {url}\n"
        md_content += f"- **Backup Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if thumbnail_url:
            md_content += f"![Cover Image]({thumbnail_url})\n\n"
            
        md_content += "## Article Content\n\n"
        
        for b in blocks:
            b_type = b.get("type")
            b_content = b.get("content", "").strip()
            if not b_content:
                continue
                
            if b_type == "p":
                md_content += f"{b_content}\n\n"
            elif b_type == "h":
                md_content += f"## {b_content}\n\n"
            elif b_type == "quote":
                md_content += f"> {b_content}\n\n"
            elif b_type == "img":
                md_content += f"![Article Image]({b_content})\n\n"
                
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        log_system_activity("Telegram poster", f"Saved markdown backup for '{title[:30]}...' to backups")
    except Exception as e:
        log_system_activity("Telegram poster", f"Failed to save markdown backup for '{title[:30]}...': {str(e)}")

def get_article_content_blocks(article_url):
    import requests
    from bs4 import BeautifulSoup
    import hashlib
    import urllib.parse
    
    cache_dir = os.path.join(DIRECTORY, "assets", "cached_articles")
    url_hash = hashlib.md5(article_url.encode('utf-8')).hexdigest()
    cache_path = os.path.join(cache_dir, f"{url_hash}.json")
    
    try:
        cache_retention.restore_article(article_url)  # NEW: re-inflate if archived
    except Exception:
        pass
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                if cached_data.get("blocks"):
                    return cached_data.get("blocks", [])
        except:
            pass
            
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        r = requests.get(article_url, headers=headers, timeout=10)
        if r.status_code in [403, 401]:
            cache_fallback_url = f"https://webcache.googleusercontent.com/search?q=cache:{urllib.parse.quote(article_url)}"
            try:
                r_fallback = requests.get(cache_fallback_url, headers=headers, timeout=10)
                if r_fallback.status_code == 200:
                    r = r_fallback
            except:
                pass
                
        if r.status_code != 200:
            return []
            
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(["script", "style", "iframe", "form", "noscript", "nav", "footer", "header"]):
            tag.decompose()
            
        main_body = None
        class_regex = re.compile(r'article-body|content-body|c-content|a-content|entry-content|post-content|main-content|story-content|article-content|core-layout')
        id_regex = re.compile(r'article-body|story-body|main-content|article-content')
        
        high_priority_candidates = [
            soup.find('article'),
            soup.find(class_=class_regex),
            soup.find(id=id_regex)
        ]
        
        for candidate in high_priority_candidates:
            if candidate and candidate.name not in ['body', 'html']:
                main_body = candidate
                break
                
        if not main_body:
            best_element = None
            best_score = -999999
            for el in soup.find_all(['div', 'article', 'section', 'main']):
                classes = el.get('class', [])
                class_str = " ".join(classes) if isinstance(classes, list) else str(classes)
                el_id = el.get('id', '') or ''
                class_id_lower = (class_str + " " + el_id).lower()
                if any(w in class_id_lower for w in ['comment', 'footer', 'header', 'nav', 'sidebar', 'ad-', 'advertisement', 'promo', 'popular', 'trending']):
                    continue
                text = el.get_text()
                p_count = len(el.find_all('p'))
                text_len = len(text.strip())
                if text_len < 100:
                    continue
                links = el.find_all('a')
                link_text_len = sum(len(a.get_text().strip()) for a in links)
                link_density = link_text_len / text_len if text_len > 0 else 0
                if link_density > 0.5:
                    continue
                score = p_count * 15 + (text_len // 40)
                if any(w in class_id_lower for w in ['article', 'body', 'content', 'story', 'post']):
                    score += 50
                if el.name == 'article':
                    score += 100
                elif el.name == 'main':
                    score += 50
                if score > best_score:
                    best_score = score
                    best_element = el
            if best_element and best_score > 30:
                main_body = best_element
                
        if not main_body:
            main_body = soup.find('main') or soup.find('body') or soup
            
        junk_selectors = [
            '.ad', '.ads', '.advertisement', '.ad-container', '.ad-wrapper', '.commercial', '.sponsored',
            '[class*="ad-"]', '[id*="ad-"]', '[class*="advertisement"]', '[class*="sponsored"]',
            '.related', '.related-posts', '.related-articles', '.related-stories', '.related-links',
            '.c-related-stories', '.c-related-links', '[class*="related-"]', '[id*="related-"]',
            '.newsletter', '.newsletter-signup', '.subscribe', '.signup-box', '.subscription',
            '[class*="newsletter"]', '[id*="newsletter"]', '[class*="signup"]', '[id*="signup"]',
            '[class*="subscribe"]', '.share', '.sharing', '.social-share', '.share-bar', '.social-links',
            '[class*="share-"]', '[id*="share-"]', '[class*="sharing-"]', '.popular', '.trending',
            '.most-popular', '.most-read', '.trending-stories', '[class*="popular"]', '[id*="popular"]',
            '[class*="trending"]', 'aside', '.sidebar', '.widget', '.comments', '#comments', '.disqus',
            '.post-navigation', '.prev-next', '.pagination', '.nav-links', '.author-bio', '.author-profile',
            '.author-info', '.byline', '[class*="byline"]', '[class*="author-"]', '.survey', '.feedback',
            '.pmc-fallback-img', '.c-tag', '.c-tags', '.tags', '.tag-list', '.lazyload-fallback',
            '[class*="story-grid"]', '#vulture-newsletter-widget', '.newsletter-widget',
            '.vulture-signup-modal', '.vulture-related-stories', '.thr-newsletter-widget', '.thr-related-stories'
        ]
        for selector in junk_selectors:
            try:
                for element in main_body.select(selector):
                    element.decompose()
            except:
                pass
                
        content_blocks = []
        
        def is_junk_text(text):
            text_clean = text.lower().strip()
            if not text_clean:
                return True
            junk_substrings = [
                "related stories", "popular on variety", "sign up for", "by submitting your email",
                "terms and privacy notice", "receive email correspondence", "thr newsletters",
                "newsletter signup", "read more:", "read more on ", "follow us on", "click here", "subscribe to"
            ]
            for junk in junk_substrings:
                if junk in text_clean:
                    return True
            junk_exact_or_starts = [
                "related", "tags", "tags:", "latest", "trending", "popular", "newsletter", "advertisement",
                "share", "byline", "nav"
            ]
            for word in junk_exact_or_starts:
                if text_clean == word or text_clean.startswith(word + " ") or text_clean.endswith(" " + word):
                    return True
            return False
            
        for element in main_body.find_all(['p', 'h2', 'h3', 'h4', 'img', 'blockquote']):
            if element.find_parent('blockquote'):
                continue
            if element.name == 'p':
                text = re.sub(r'\s+', ' ', element.text).strip()
                if len(text) > 20 and not is_junk_text(text):
                    content_blocks.append({"type": "p", "content": text})
            elif element.name in ('h2', 'h3', 'h4'):
                text = re.sub(r'\s+', ' ', element.text).strip()
                if text and not is_junk_text(text):
                    content_blocks.append({"type": "h", "level": int(element.name[1]), "content": text})
            elif element.name == 'img':
                src = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
                if src and not src.startswith('data:'):
                    src = src.strip()
                    if src.startswith('//'):
                        src = 'https:' + src
                    if not any(p in src.lower() for p in ['fallback.gif', 'placeholder.gif', 'placeholder.png', 'spacer.gif', 'pixel.gif', 'lazyload']):
                        content_blocks.append({"type": "img", "content": src})
            elif element.name == 'blockquote':
                text = re.sub(r'\s+', ' ', element.text).strip()
                if text and not is_junk_text(text):
                    content_blocks.append({"type": "quote", "content": text})
                    
        if not content_blocks:
            for p in main_body.find_all('p'):
                text = p.text.strip()
                if len(text) > 10:
                    content_blocks.append({"type": "p", "content": text})
                    
        title = ""
        h1_main = soup.find('h1')
        if h1_main:
            title = h1_main.text.strip()
        if not title and soup.title:
            title = soup.title.string
            
        try:
            content_blocks = media_cache.localize_article_blocks(content_blocks)  # NEW
        except Exception as _e:
            print(f"[Image Cache] article image localize failed: {_e}")
        try:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({"title": title, "url": article_url, "blocks": content_blocks}, f, indent=4)
        except:
            pass
            
        return content_blocks
    except Exception as e:
        print(f"Error scraping article content: {e}")
        return []

def _detect_and_build_source(raw, defaults=None):
    """
    Normalize ONE source definition into the on-disk record schema used
    everywhere: {name, url, category, avatar_path, is_rss, section}.

    `raw` may be a dict or a bare string (a single line / URL / @handle).
    Accepts BOTH key spellings: url|feed_url and avatar_base64|logo_base64.
    Auto-detects the source type:
      * bare "@handle" (or a single bare token) -> Twitter/X
      * twitter.com / x.com URL                 -> Twitter/X
      * t.me / t.me/s/ URL                      -> Telegram
      * anything else                           -> RSS / site feed

    Twitter/X handles are stored in the canonical https://x.com/<handle> form
    (is_rss=False), identical to the existing built-in X channels, so they are
    resolved by the EXISTING fetch_twitter_timeline()/scrape_twitter_syndication()
    path and each becomes its own channel.

    Returns (record, error). On failure record is None and error is a str.
    """
    defaults = defaults or {}
    if not isinstance(raw, dict):
        raw = {"url": str(raw or "")}

    name = (raw.get("name") or "").strip()
    url = (raw.get("url") or raw.get("feed_url") or "").strip()
    category = (raw.get("category") or defaults.get("category") or "General").strip()
    section = (raw.get("section") or defaults.get("section") or "Entertainment").strip()
    is_rss = raw.get("is_rss", None)

    if not url:
        return None, "URL is required"

    lower = url.lower()

    if url.startswith("@") or ("." not in url and "/" not in url and ":" not in url):
        # Bare @handle (or a single bare token) -> Twitter/X
        handle = url.lstrip("@").strip().strip("/")
        if not handle:
            return None, "Empty Twitter/X handle"
        url = "https://x.com/" + handle
        if not name:
            name = handle + " (X)"
        is_rss = False
    elif "twitter.com/" in lower or "x.com/" in lower:
        normalized = url if lower.startswith("http") else "https://" + url
        handle = twitter_screen_name(normalized)
        if handle:
            url = "https://x.com/" + handle
            if not name:
                name = handle + " (X)"
        elif not name:
            name = "X feed"
        is_rss = False
    elif "t.me/" in lower:
        if not lower.startswith("http"):
            url = "https://" + url
            lower = url.lower()
        if "t.me/s/" not in lower:
            url = url.replace("t.me/", "t.me/s/", 1)
        if not name:
            channel = url.rstrip("/").split("/")[-1]
            name = (channel + " (Telegram)") if channel else "Telegram"
        is_rss = False
    else:
        if not lower.startswith("http://") and not lower.startswith("https://"):
            url = "https://" + url
        if is_rss is None:
            is_rss = True
        if not name:
            name = clean_site_name("", url)

    if is_rss is None:
        is_rss = True
    if not name:
        name = url

    record = {
        "name": name,
        "url": url,
        "category": category,
        "avatar_path": "",
        "is_rss": bool(is_rss),
        "section": section,
    }
    return record, None


def fetch_and_aggregate_news():
    global news_cache
    sources = [
        ("Variety main feed", "https://variety.com/feed", "General", True, "Entertainment"),
        ("Variety TV", "https://variety.com/v/tv/feed", "TV", True, "Entertainment"),
        ("Variety Film", "https://variety.com/v/film/feed", "Movies", True, "Entertainment"),
        ("Variety Music", "https://variety.com/v/music/feed/", "Music", True, "Entertainment"),
        ("Variety Digital", "https://variety.com/v/digital/feed/", "Digital", True, "Entertainment"),
        ("Variety Awards", "https://variety.com/v/awards/feed/", "Awards", True, "Entertainment"),
        ("The Hollywood Reporter main feed", "https://www.hollywoodreporter.com/feed", "General", True, "Entertainment"),
        ("The Hollywood Reporter Movies section", "https://www.hollywoodreporter.com/c/movies/feed/", "Movies", True, "Entertainment"),
        ("The Hollywood Reporter TV section", "https://www.hollywoodreporter.com/c/tv/feed/", "TV", True, "Entertainment"),
        ("The Hollywood Reporter Business section", "https://www.hollywoodreporter.com/c/business/feed/", "General", True, "Entertainment"),
        ("The Hollywood Reporter Lifestyle section", "https://www.hollywoodreporter.com/c/lifestyle/feed/", "General", True, "Entertainment"),
        ("The Hollywood Reporter Awards section", "https://www.hollywoodreporter.com/c/awards/feed/", "General", True, "Entertainment"),
        ("Vulture main feed", "https://www.vulture.com/feed/", "General", True, "Entertainment"),
        ("Vulture TV section", "https://www.vulture.com/tv/", "TV", False, "Entertainment"),
        ("Vulture Movies section", "https://www.vulture.com/movies/", "Movies", False, "Entertainment"),
        ("Vulture Music section", "https://www.vulture.com/music/", "General", False, "Entertainment"),
        ("Vulture Books section", "https://www.vulture.com/books/", "General", False, "Entertainment"),
        ("Vulture Comedy section", "https://www.vulture.com/comedy/", "General", False, "Entertainment"),
        ("Entertainment Weekly main site", "https://ew.com", "General", False, "Entertainment"),
        ("Entertainment Weekly TV", "https://ew.com/tv/", "TV", False, "Entertainment"),
        ("Entertainment Weekly Movies", "https://ew.com/movies/", "Movies", False, "Entertainment"),
        ("Entertainment Weekly Music", "https://ew.com/music/", "General", False, "Entertainment"),
        ("Entertainment Weekly Celebrity", "https://ew.com/celebrity/", "General", False, "Entertainment"),
        ("Screen Daily RSS/start page", "https://www.screendaily.com/full-rss", "Movies", False, "Entertainment"),
        ("Deadline Hollywood main feed", "https://deadline.com/feed/", "General", True, "Entertainment"),
        ("Deadline Hollywood Film", "https://deadline.com/v/film/feed/", "Movies", True, "Entertainment"),
        ("Deadline Hollywood TV", "https://deadline.com/v/tv/feed/", "TV", True, "Entertainment"),
        ("Deadline Hollywood Box Office", "https://deadline.com/v/box-office/feed/", "Movies", True, "Entertainment"),
        ("Deadline Hollywood Awards", "https://deadline.com/v/awards/feed/", "General", True, "Entertainment"),
        ("Deadline Hollywood Celebrity", "https://deadline.com/v/celebrity/feed/", "General", True, "Entertainment"),
        ("Collider main feed", "https://collider.com/feed/", "General", True, "Entertainment"),
        ("Collider TV", "https://collider.com/television/feed/", "TV", True, "Entertainment"),
        ("RogerEbert.com", "https://www.rogerebert.com/feed", "Movies", True, "Entertainment"),
        ("The A.V. Club main feed", "https://www.avclub.com/rss", "General", True, "Entertainment"),
        ("Letterboxd Journal", "https://letterboxd.com/journal/feed/", "Movies", True, "Entertainment"),
        ("Little White Lies", "https://lwlies.com/feed/", "Movies", True, "Entertainment"),
        ("Empire Magazine", "https://www.empireonline.com/movies/feed/", "Movies", True, "Entertainment"),
        ("CinemaBlend main news", "https://www.cinemablend.com/rss/topic/news", "General", True, "Entertainment"),
        ("Rotten Tomatoes News/editorial", "https://editorial.rottentomatoes.com/news", "News", False, "Entertainment"),
        ("Rotten Tomatoes scorecards/editorial", "https://editorial.rottentomatoes.com/movie-tv-scorecards", "Scorecards", False, "Entertainment"),
        ("Rotten Tomatoes binge guide/editorial", "https://editorial.rottentomatoes.com/binge-guide", "Binge Guide", False, "Entertainment"),
        
        # Sports
        ("ESPN News", "https://www.espn.com/espn/rss/news", "Sports", True, "Sports"),
        ("ESPN NFL", "https://www.espn.com/espn/rss/nfl/news", "Sports", True, "Sports"),
        ("ESPN NBA", "https://www.espn.com/espn/rss/nba/news", "Sports", True, "Sports"),
        ("ESPN MLB", "https://www.espn.com/espn/rss/mlb/news", "Sports", True, "Sports"),
        ("ESPN Soccer", "https://www.espn.com/espn/rss/soccer/news", "Sports", True, "Sports"),
        ("ESPN NHL", "https://www.espn.com/espn/rss/nhl/news", "Sports", True, "Sports"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "Sports", True, "Sports"),
        ("BBC Sport Football", "https://feeds.bbci.co.uk/sport/football/rss.xml", "Sports", True, "Sports"),
        ("BBC Sport Formula 1", "https://feeds.bbci.co.uk/sport/formula1/rss.xml", "Sports", True, "Sports"),
        ("BBC Sport Cricket", "https://feeds.bbci.co.uk/sport/cricket/rss.xml", "Sports", True, "Sports"),
        ("BBC Sport Rugby Union", "https://feeds.bbci.co.uk/sport/rugby-union/rss.xml", "Sports", True, "Sports"),
        ("Sky Sports News", "https://www.skysports.com/rss/12040", "News", True, "Sports"),
        ("Sky Sports Football", "https://www.skysports.com/rss/11095", "Sports", True, "Sports"),
        ("Fabrizio Romano", "https://t.me/s/fabrizioromanotg", "Transfers", False, "Sports"),
        # --- X / Twitter channels (resolved via Nitter RSS in fetch_twitter_timeline) ---
        ("Fabrizio Romano (X)", "https://x.com/FabrizioRomano", "Transfers", False, "Sports"),
        ("The Athletic (X)", "https://x.com/TheAthletic", "News", False, "Sports"),
        ("The Madrid Zone (X)", "https://x.com/theMadridZone", "News", False, "Sports"),
        
        # Technology
        ("TechCrunch", "https://techcrunch.com/feed/", "Tech", True, "Technology"),
        ("TechCrunch Startups", "https://techcrunch.com/category/startups/feed/", "Tech", True, "Technology"),
        ("TechCrunch Venture", "https://techcrunch.com/category/venture/feed/", "Tech", True, "Technology"),
        ("TechCrunch Apps", "https://techcrunch.com/category/apps/feed/", "Tech", True, "Technology"),
        ("Wired Tech", "https://www.wired.com/feed/category/gear/latest/rss", "Gear", True, "Technology"),
        ("Wired Science", "https://www.wired.com/feed/category/science/latest/rss", "Science", True, "Technology"),
        ("Wired Business", "https://www.wired.com/feed/category/business/latest/rss", "Business", True, "Technology"),
        ("Wired Culture", "https://www.wired.com/feed/category/culture/latest/rss", "Culture", True, "Technology"),
        ("Wired Security", "https://www.wired.com/feed/category/security/latest/rss", "Security", True, "Technology"),
        ("The Verge", "https://www.theverge.com/rss/index.xml", "General", True, "Technology"),
        ("The Verge Tech", "https://www.theverge.com/rss/tech/index.xml", "Tech", True, "Technology"),
        ("The Verge Reviews", "https://www.theverge.com/rss/reviews/index.xml", "Reviews", True, "Technology"),
        ("The Verge Science", "https://www.theverge.com/rss/science/index.xml", "Science", True, "Technology"),
        ("The Verge Entertainment", "https://www.theverge.com/rss/entertainment/index.xml", "Entertainment", True, "Technology")
    ]
    
    custom_sources = load_custom_sources()
    for cs in custom_sources:
        sources.append((cs["name"], cs["url"], cs.get("category", "General"), cs.get("is_rss", True), cs.get("section", "Entertainment")))
        
    all_articles = []
    status_map = {}
    
    twitter_sources = []
    other_sources = []
    for s in sources:
        url = s[1]
        if "twitter.com/" in url or "x.com/" in url:
            twitter_sources.append(s)
        else:
            other_sources.append(s)
            
    # Fetch non-Twitter sources concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(fetch_single_source, other_sources))
        
    # Fetch Twitter sources sequentially with a rate limit safety delay
    import time
    for ts in twitter_sources:
        res = fetch_single_source(ts)
        results.append(res)
        time.sleep(0.5)
        
    with news_cache_lock:
        old_list = list(news_cache["data"])

    # Durability fix: the in-memory cache is empty on a fresh start, so fall
    # back to the last on-disk snapshot. Without this, posts that leave the
    # source feed between app restarts are never archived (lost forever).
    if not old_list:
        old_list = feed_store.load_feed_snapshot()

    for res in results:
        status_map[res["source"]] = res["status"]
        # If the feed source failed to refresh, preserve its previous articles from the old list
        # so the user doesn't lose them and they are not incorrectly archived/removed.
        if res["status"].startswith("Failed") and old_list:
            old_source_articles = [art for art in old_list if art.get("source") == res["source"]]
            res["items"] = old_source_articles
        all_articles.extend(res["items"])
        
    seen_urls = set()
    seen_titles = set()
    deduped = []
    
    for art in all_articles:
        url = art["url"].lower().strip()
        title_norm = re.sub(r'[^a-z0-9]', '', art["title"].lower())
        
        if url in seen_urls or title_norm in seen_titles:
            continue
            
        seen_urls.add(url)
        seen_titles.add(title_norm)
        deduped.append(art)
        
    dated = [a for a in deduped if a["timestamp"] > 0]
    undated = [a for a in deduped if a["timestamp"] == 0]
    
    dated.sort(key=lambda x: x["timestamp"], reverse=True)
    final_list = dated + undated

    archive_removed_posts(old_list, final_list)

    with news_cache_lock:
        news_cache["data"] = final_list
        news_cache["last_fetched"] = time.time()
        news_cache["source_status"] = status_map

    # Persist the fresh feed so the next run (even after a restart) has a
    # durable baseline and the feed is available offline.
    feed_store.save_feed_snapshot(final_list, status_map)

    # Start background downloading of feed thumbnails
    download_feed_thumbnails_async(final_list, status_map)

    # NEW: archive (zip) cached posts older than 14 days, then free disk space.
    def _retention_worker():
        try:
            cache_retention.run_retention(max_age_days=14, log=log_system_activity)
        except Exception as e:
            log_system_activity("Cache Retention", f"Retention run failed: {e}")
    threading.Thread(target=_retention_worker, daemon=True).start()

    return final_list, status_map

def clean_site_name(title, url):
    if not title:
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[0].capitalize()
            return domain
        except:
            return "Custom Feed"
            
    if title.startswith("<![CDATA[") and title.endswith("]]>"):
        title = title[9:-3].strip()
        
    title = title.strip()
    
    suffixes = [
        " RSS Feed", " RSS", " Feed", " - Feed", " » Feed", " | Feed",
        " - Latest News", " - News", " - Home", " - Latest",
        " | Home", " | News", " - Web Site", " | Website", " - Official Site",
        " - Independent Film News", " - Independent Film", " - Movies", " - Movie News"
    ]
    
    for suffix in suffixes:
        if title.lower().endswith(suffix.lower()):
            title = title[:-len(suffix)].strip()
            
    for sep in [' - ', ' | ', ' » ']:
        if sep in title:
            parts = title.split(sep)
            generic_words = ['feed', 'rss', 'news', 'home', 'latest', 'website', 'official', 'movies', 'tv', 'blog']
            if any(gw in parts[1].lower() for gw in generic_words):
                title = parts[0].strip()
                
    title_lower = title.lower()
    if "variety" in title_lower:
        return "Variety"
    if "hollywood reporter" in title_lower or "thr" in title_lower:
        return "The Hollywood Reporter"
    if "vulture" in title_lower:
        return "Vulture"
    if "entertainment weekly" in title_lower:
        return "Entertainment Weekly"
    if "screen daily" in title_lower or "screendaily" in title_lower:
        return "Screen Daily"
    if "rotten tomatoes" in title_lower:
        return "Rotten Tomatoes"
    if "indiewire" in title_lower:
        return "IndieWire"
    if "slashfilm" in title_lower:
        return "SlashFilm"
        
    return title

def find_site_logo(soup, base_url):
    import urllib.parse
    parsed_base = urllib.parse.urlparse(base_url)
    base_host = f"{parsed_base.scheme}://{parsed_base.netloc}"
    
    logo_candidates = []
    
    for link in soup.find_all('link', rel=lambda r: r and 'apple-touch-icon' in r.lower()):
        href = link.get('href')
        if href:
            sizes = link.get('sizes', '')
            priority = 100
            if sizes:
                try:
                    w = int(sizes.split('x')[0])
                    priority += w
                except:
                    pass
            logo_candidates.append((priority, href))
            
    for link in soup.find_all('link', rel=lambda r: r and 'icon' in r.lower() and 'apple-touch' not in r.lower()):
        href = link.get('href')
        if href:
            sizes = link.get('sizes', '')
            priority = 50
            if sizes:
                try:
                    w = int(sizes.split('x')[0])
                    priority += w
                except:
                    pass
            if 'png' in href.lower() or 'svg' in href.lower():
                priority += 20
            logo_candidates.append((priority, href))
            
    for meta in soup.find_all('meta', property=lambda p: p and p.lower() in ['og:image', 'og:image:secure_url']):
        content = meta.get('content')
        if content:
            logo_candidates.append((40, content))
            
    for meta in soup.find_all('meta', attrs={'name': lambda n: n and n.lower() == 'twitter:image'}):
        content = meta.get('content')
        if content:
            logo_candidates.append((30, content))
            
    logo_candidates.sort(key=lambda x: x[0], reverse=True)
    if logo_candidates:
        return resolve_image_url(logo_candidates[0][1], base_host)
        
    return ""

# --------------------------------------------------------------------------- #
#  System font enumeration for the OFFLINE VIEWER (web UI) font picker.
#  Independent from the PySide6/QML desktop font system. Cross-safe: always
#  returns a non-empty, sorted, de-duplicated list of family names.
# --------------------------------------------------------------------------- #
FONT_FALLBACK_LIST = [
    "Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia",
    "Roboto", "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS",
    "Verdana", "Vazirmatn",
]


def get_system_font_families():
    """Return installed font families for the offline viewer font picker.

    Strategy order (first non-empty wins), all optional/guarded:
      1) matplotlib.font_manager  -> clean family names, cross-platform
      2) Windows font registry    -> reliable on the default Windows target
      3) FONT_FALLBACK_LIST       -> guarantees a usable, non-empty result
    """
    families = set()

    # 1) matplotlib gives clean family names. OPTIONAL dependency: skipped
    #    silently if not installed (never a hard requirement).
    try:
        from matplotlib import font_manager
        for f in font_manager.fontManager.ttflist:
            if getattr(f, "name", ""):
                families.add(f.name)
    except Exception:
        pass

    # 2) Windows font registry (stdlib winreg, no extra deps on Windows).
    if not families:
        try:
            import winreg
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    value_name = winreg.EnumValue(key, i)[0]
                    # "Arial (TrueType)" / "Segoe UI Bold (TrueType)" -> strip tag
                    fam = re.sub(r"\s*\(.*?\)\s*$", "", value_name).strip()
                    if fam:
                        families.add(fam)
        except Exception:
            pass

    # 3) Hard fallback so the endpoint never returns an empty list.
    if not families:
        families = set(FONT_FALLBACK_LIST)

    # Drop private/hidden ('.') families, de-dupe, sort case-insensitively.
    cleaned = sorted({f for f in families if f and not f.startswith(".")},
                     key=lambda s: s.lower())
    return cleaned


class GUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
        
    def send_json_response(self, status_code, data):
        try:
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except (ConnectionError, OSError):
            pass

    def handle_system_fonts(self):
        # Offline-viewer font list endpoint (independent of the desktop app).
        try:
            self.send_json_response(200, {"fonts": get_system_font_families()})
        except Exception as e:  # never break the page; return a usable fallback
            self.send_json_response(200, {"fonts": FONT_FALLBACK_LIST, "error": str(e)})

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json_response(200, {"status": "ok", "app": "OfflineFeed"})
        elif self.path == "/api/system/fonts":
            self.handle_system_fonts()
        elif self.path == "/api/activity_log":
            self.handle_activity_log()
        elif self.path == "/api/telegram/config":
            self.handle_get_telegram_config()
        elif self.path.startswith("/api/news/saved"):
            self.handle_get_saved_posts()
        elif self.path.startswith("/api/news/archived"):
            self.handle_get_archived_posts()
        elif self.path.startswith("/api/news/article"):
            self.handle_news_article()
        elif self.path.startswith("/api/news"):
            self.handle_news()
        elif self.path.startswith("/data/avatars/"):
            repo_root = os.path.dirname(DIRECTORY)
            filename = urllib.parse.unquote(self.path.lstrip("/"))
            file_path = os.path.join(repo_root, filename)
            avatars_dir_abs = os.path.join(repo_root, "data", "avatars")
            if os.path.exists(file_path) and os.path.commonpath([avatars_dir_abs, os.path.abspath(file_path)]) == os.path.abspath(avatars_dir_abs):
                ext = os.path.splitext(file_path)[1].lower()
                content_type = "image/png"
                if ext in (".jpg", ".jpeg"):
                    content_type = "image/jpeg"
                elif ext == ".gif":
                    content_type = "image/gif"
                elif ext == ".ico":
                    content_type = "image/x-icon"
                elif ext == ".svg":
                    content_type = "image/svg+xml"
                elif ext == ".webp":
                    content_type = "image/webp"
                
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(content)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_error(500, f"Error reading file: {e}")
                    return
            self.send_error(404, "File not found")
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        print(f"[GUI Server] Incoming POST request to {self.path}")
        if self.path == "/api/news/sources/add":
            self.handle_add_news_source()
        elif self.path == "/api/news/sources/update":
            self.handle_update_news_source()
        elif self.path == "/api/news/sources/delete":
            self.handle_delete_news_source()
        elif self.path == "/api/news/sources/analyze":
            self.handle_analyze_news_source()
        elif self.path == "/api/news/sources/add_batch":
            self.handle_add_news_sources_batch()
        elif self.path == "/api/news/sources/import_opml":
            self.handle_import_opml()
        elif self.path == "/api/cache/clear":
            self.handle_clear_cache()
        elif self.path == "/api/news/ignore":
            self.handle_ignore_post()
        elif self.path == "/api/news/saved/add":
            self.handle_add_saved_post()
        elif self.path == "/api/news/saved/remove":
            self.handle_remove_saved_post()
        elif self.path == "/api/telegram/config":
            self.handle_save_telegram_config()
        elif self.path == "/api/telegram/send_channel":
            self.handle_send_channel_to_telegram()
        elif self.path == "/api/telegram/reset_history":
            self.handle_reset_telegram_history()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_get_saved_posts(self):
        try:
            posts = load_saved_posts()
            self.send_json_response(200, {"status": "success", "articles": posts})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_get_archived_posts(self):
        try:
            posts = load_archived_posts()
            self.send_json_response(200, {"status": "success", "articles": posts})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_add_saved_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            art = json.loads(post_data.decode('utf-8'))
            
            posts = load_saved_posts()
            art_key = get_article_key(art)
            
            # Check already saved
            if any(get_article_key(p) == art_key for p in posts):
                self.send_json_response(200, {
                    "status": "already_saved",
                    "message": "Article is already in Saved Messages!",
                    "saved_articles": posts
                })
                return
                
            posts.insert(0, art)
            save_saved_posts(posts)
            
            log_system_activity("Saved Messages", f"Saved article: {art.get('title', 'No Title')}")
            self.send_json_response(200, {
                "status": "success",
                "message": "Forwarded to Saved Messages!",
                "saved_articles": posts
            })
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_remove_saved_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            art_key = params.get("key") or params.get("url") or ""
            
            posts = load_saved_posts()
            new_posts = [p for p in posts if get_article_key(p) != art_key and p.get("url") != art_key]
            
            if len(new_posts) == len(posts):
                self.send_json_response(200, {
                    "status": "not_found",
                    "message": "Article not found in Saved Messages",
                    "saved_articles": posts
                })
                return
                
            save_saved_posts(new_posts)
            log_system_activity("Saved Messages", "Removed article from Saved Messages")
            self.send_json_response(200, {
                "status": "success",
                "message": "Removed from Saved Messages!",
                "saved_articles": new_posts
            })
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_news(self):
        global news_cache
        current_time = time.time()
        with news_cache_lock:
            cached_data = news_cache["data"]
            last_fetched = news_cache["last_fetched"]
            source_status = news_cache["source_status"]
            
        force_refresh = "refresh=true" in self.path
        ignored_urls = load_ignored_posts()
        
        # 15 minutes cache (900 seconds)
        if cached_data and (current_time - last_fetched < 900) and not force_refresh:
            filtered_cached = [art for art in cached_data if art["url"].lower().strip() not in ignored_urls]
            self.send_json_response(200, {
                "status": "cached",
                "last_fetched": last_fetched,
                "source_status": source_status,
                "articles": filtered_cached,
                "custom_sources": load_custom_sources(),
                "default_sources_avatars": load_default_sources_avatars_map(),
                "saved_articles": load_saved_posts(),
                "archived_articles": load_archived_posts()
            })
        else:
            try:
                articles, status_map = fetch_and_aggregate_news()
                filtered_fresh = [art for art in articles if art["url"].lower().strip() not in ignored_urls]
                self.send_json_response(200, {
                    "status": "fresh",
                    "last_fetched": time.time(),
                    "source_status": status_map,
                    "articles": filtered_fresh,
                    "custom_sources": load_custom_sources(),
                    "default_sources_avatars": load_default_sources_avatars_map(),
                    "saved_articles": load_saved_posts(),
                    "archived_articles": load_archived_posts()
                })
            except Exception as e:
                import sys
                is_shutdown = "interpreter shutdown" in str(e) or "after shutdown" in str(e)
                if not sys.is_finalizing() and not is_shutdown:
                    import traceback
                    traceback.print_exc()
                # Offline fallback: if the network fetch failed but we have a
                # persisted feed snapshot, serve it instead of erroring so the
                # user can still read everything kept locally.
                snapshot = feed_store.load_feed_snapshot()
                if snapshot:
                    filtered_snapshot = [art for art in snapshot if art.get("url", "").lower().strip() not in ignored_urls]
                    self.send_json_response(200, {
                        "status": "offline_cache",
                        "last_fetched": last_fetched,
                        "source_status": source_status,
                        "articles": filtered_snapshot,
                        "custom_sources": load_custom_sources(),
                        "default_sources_avatars": load_default_sources_avatars_map(),
                        "saved_articles": load_saved_posts(),
                        "archived_articles": load_archived_posts()
                    })
                    return
                self.send_json_response(500, {"error": str(e)})

    def handle_ignore_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            url = params.get("url", "").strip()
            if not url:
                self.send_json_response(400, {"error": "URL is required"})
                return
                
            save_ignored_post(url)
            
            # Remove from cached data list in memory as well
            global news_cache
            with news_cache_lock:
                if news_cache["data"]:
                    news_cache["data"] = [art for art in news_cache["data"] if art["url"].lower().strip() != url.lower().strip()]
                    
            self.send_json_response(200, {"status": "success", "message": "Post ignored successfully"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_get_telegram_config(self):
        config = load_telegram_config()
        self.send_json_response(200, config)

    def handle_save_telegram_config(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            config = json.loads(post_data.decode('utf-8'))
            
            save_telegram_config(config)
            
            log_system_activity("Telegram poster", "Updated Telegram configuration settings")
            self.send_json_response(200, {"status": "success", "message": "Telegram settings saved"})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_send_channel_to_telegram(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            channel_name = params.get("channel_name", "").strip()
            articles = params.get("articles", [])
            
            if not articles:
                self.send_json_response(400, {"error": "No articles to send"})
                return
                
            config = load_telegram_config()
            bot_token = config.get("bot_token", "").strip()
            default_chat_id = config.get("default_chat_id", "").strip()
            sports_chat_id = config.get("sports_chat_id", "").strip() or default_chat_id
            technology_chat_id = config.get("technology_chat_id", "").strip() or default_chat_id
            channel_threads = config.get("channel_threads", {})
            
            if not bot_token or not default_chat_id:
                self.send_json_response(400, {"error": "Telegram Bot Token and Chat ID are not configured in settings."})
                return
                
            sent_urls = load_sent_posts()
            ignored_urls = load_ignored_posts()
            
            # Filter articles to only send new ones and respect deleted/ignored articles
            to_send = []
            for art in articles:
                u_clean = art.get("url", "").lower().strip()
                if u_clean not in sent_urls and u_clean not in ignored_urls:
                    to_send.append(art)
                    
            # Reverse order so that oldest posts are sent first (restoring chronological order in Telegram)
            to_send.reverse()
            
            already_sent_count = len(articles) - len(to_send)
            
            if not to_send:
                self.send_json_response(200, {
                    "status": "success",
                    "sent_count": 0,
                    "already_sent_count": already_sent_count,
                    "to_send_count": 0,
                    "all_skipped": True
                })
                return
                
            start_telegram_queue_worker()
            telegram_job_queue.put({
                "channel_name": channel_name,
                "to_send": to_send,
                "bot_token": bot_token,
                "default_chat_id": default_chat_id,
                "sports_chat_id": sports_chat_id,
                "technology_chat_id": technology_chat_id,
                "channel_threads": channel_threads,
                "already_sent_count": already_sent_count
            })
            
            self.send_json_response(200, {
                "status": "success",
                "to_send_count": len(to_send),
                "already_sent_count": already_sent_count
            })
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_news_article(self):
        import requests
        from bs4 import BeautifulSoup
        
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        article_url = params.get('url', [None])[0]
        
        if not article_url:
            self.send_json_response(400, {"error": "Missing url parameter"})
            return
            
        # Get matching article from memory cache
        matching_article = None
        with news_cache_lock:
            for art in news_cache["data"]:
                if art["url"].lower().strip() == article_url.lower().strip():
                    matching_article = art
                    break
                    
        cache_dir = os.path.join(DIRECTORY, "assets", "cached_articles")
        url_hash = hashlib.md5(article_url.encode('utf-8')).hexdigest()
        cache_path = os.path.join(cache_dir, f"{url_hash}.json")
        
        # If it is a social post (Telegram or X/Twitter), return cached summary/description immediately
        if matching_article and (any(domain in article_url.lower() for domain in ["t.me/", "x.com/", "twitter.com/"]) or matching_article.get("section") == "Sports" and matching_article.get("source") == "Fabrizio Romano"):
            blocks = []
            if matching_article.get("thumbnail"):
                local_thumb = download_and_cache_image(matching_article["thumbnail"])
                blocks.append({"type": "img", "content": local_thumb})
            if matching_article.get("description"):
                paragraphs = [p.strip() for p in matching_article["description"].split('\n') if p.strip()]
                for p in paragraphs:
                    blocks.append({"type": "p", "content": p})
            
            result = {
                "title": matching_article.get("title") or "Article",
                "url": article_url,
                "blocks": blocks
            }
            try:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4)
            except:
                pass
            self.send_json_response(200, result)
            return
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    if cached_data.get("blocks"):
                        self.send_json_response(200, cached_data)
                        return
            except:
                pass
                
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/'
            }
            
            fetch_url = article_url
            r = requests.get(fetch_url, headers=headers, timeout=10)
            print(f"[News Aggregator] Scraping article: {fetch_url} -> Status Code: {r.status_code}")
            
            if r.status_code in [403, 401]:
                print(f"[News Aggregator] Blocked ({r.status_code}) for article. Retrying with Google Cache...")
                time.sleep(1.0)
                cache_fallback_url = f"https://webcache.googleusercontent.com/search?q=cache:{urllib.parse.quote(article_url)}"
                try:
                    r_fallback = requests.get(cache_fallback_url, headers=headers, timeout=10)
                    if r_fallback.status_code == 200:
                        r = r_fallback
                        fetch_url = cache_fallback_url
                except Exception as fb_err:
                    print(f"[News Aggregator] Fallback fetch failed: {fb_err}")
            
            if r.status_code != 200:
                self.send_json_response(500, {"error": f"Failed to retrieve article (HTTP {r.status_code})"})
                return
                
            soup = BeautifulSoup(r.text, 'html.parser')
            for tag in soup(["script", "style", "iframe", "form", "noscript", "nav", "footer", "header"]):
                tag.decompose()
                
            main_body = None
            
            # 1. Try high-priority hand-tuned selectors (innermost containers)
            class_regex = re.compile(r'article-body|content-body|c-content|a-content|entry-content|post-content|main-content|story-content|article-content|core-layout')
            id_regex = re.compile(r'article-body|story-body|main-content|article-content')
            
            high_priority_candidates = [
                soup.find('article'),
                soup.find(class_=class_regex),
                soup.find(id=id_regex)
            ]
            
            for candidate in high_priority_candidates:
                if candidate and candidate.name not in ['body', 'html']:
                    main_body = candidate
                    break
                    
            # 2. Heuristic-based auto-detector for new custom feed sources
            if not main_body:
                best_element = None
                best_score = -999999
                
                for el in soup.find_all(['div', 'article', 'section', 'main']):
                    classes = el.get('class', [])
                    class_str = " ".join(classes) if isinstance(classes, list) else str(classes)
                    el_id = el.get('id', '') or ''
                    class_id_lower = (class_str + " " + el_id).lower()
                    
                    # Skip elements inside known layout grids or widgets
                    if any(w in class_id_lower for w in ['comment', 'footer', 'header', 'nav', 'sidebar', 'ad-', 'advertisement', 'promo', 'popular', 'trending']):
                        continue
                        
                    text = el.get_text()
                    p_count = len(el.find_all('p'))
                    text_len = len(text.strip())
                    
                    if text_len < 100:
                        continue
                        
                    # LINK DENSITY check (filters out menu listings and link sidebars)
                    links = el.find_all('a')
                    link_text_len = sum(len(a.get_text().strip()) for a in links)
                    link_density = link_text_len / text_len if text_len > 0 else 0
                    
                    if link_density > 0.5:
                        continue
                        
                    # Calculate content score
                    score = p_count * 15 + (text_len // 40)
                    
                    # Weight indicators
                    if any(w in class_id_lower for w in ['article', 'body', 'content', 'story', 'post']):
                        score += 50
                    if el.name == 'article':
                        score += 100
                    elif el.name == 'main':
                        score += 50
                        
                    if score > best_score:
                        best_score = score
                        best_element = el
                        
                if best_element and best_score > 30:
                    main_body = best_element
                    print(f"[News Parser] Auto-detected main body container: <{main_body.name}> (score={best_score})")
            
            # 3. Last resort fallback
            if not main_body:
                main_body = soup.find('main') or soup.find('body') or soup

            # Clean up junk elements (related stories, news promos, social links, ads, comments, sidebar widgets)
            junk_selectors = [
                '.ad', '.ads', '.advertisement', '.ad-container', '.ad-wrapper', '.commercial', '.sponsored',
                '[class*="ad-"]', '[id*="ad-"]', '[class*="advertisement"]', '[class*="sponsored"]',
                '.related', '.related-posts', '.related-articles', '.related-stories', '.related-links',
                '.c-related-stories', '.c-related-links', '[class*="related-"]', '[id*="related-"]',
                '.newsletter', '.newsletter-signup', '.subscribe', '.signup-box', '.subscription',
                '[class*="newsletter"]', '[id*="newsletter"]', '[class*="signup"]', '[id*="signup"]',
                '[class*="subscribe"]',
                '.share', '.sharing', '.social-share', '.share-bar', '.social-links',
                '[class*="share-"]', '[id*="share-"]', '[class*="sharing-"]',
                '.popular', '.trending', '.most-popular', '.most-read', '.trending-stories',
                '[class*="popular"]', '[id*="popular"]', '[class*="trending"]',
                'aside', '.sidebar', '.widget', '.comments', '#comments', '.disqus',
                '.post-navigation', '.prev-next', '.pagination', '.nav-links',
                '.author-bio', '.author-profile', '.author-info', '.byline',
                '[class*="byline"]', '[class*="author-"]',
                '.survey', '.feedback',
                '.pmc-fallback-img', '.c-tag', '.c-tags', '.tags', '.tag-list',
                '.lazyload-fallback', '[class*="story-grid"]',
                '#vulture-newsletter-widget', '.newsletter-widget',
                '.vulture-signup-modal', '.vulture-related-stories',
                '.thr-newsletter-widget', '.thr-related-stories'
            ]
            
            for selector in junk_selectors:
                try:
                    for element in main_body.select(selector):
                        element.decompose()
                except Exception:
                    pass
                
            content_blocks = []
            title = ""
            h1_main = soup.find('h1')
            if h1_main:
                title = h1_main.text.strip()
            if not title and soup.title:
                title = soup.title.string
                
            # Helper to check for promo/junk text
            def is_junk_text(text):
                text_clean = text.lower().strip()
                if not text_clean:
                    return True
                junk_substrings = [
                    "related stories", "popular on variety", "sign up for", 
                    "by submitting your email", "terms and privacy notice", 
                    "receive email correspondence", "thr newsletters", 
                    "newsletter signup", "read more:", "read more on ", 
                    "follow us on", "click here", "subscribe to"
                ]
                for junk in junk_substrings:
                    if junk in text_clean:
                        return True
                junk_exact_or_starts = [
                    "related", "tags", "tags:", "latest", "trending", 
                    "popular", "newsletter", "advertisement", "share", "byline", "nav"
                ]
                for word in junk_exact_or_starts:
                    if text_clean == word or text_clean.startswith(word + " ") or text_clean.endswith(" " + word):
                        return True
                return False

            for element in main_body.find_all(['p', 'h2', 'h3', 'h4', 'img', 'blockquote']):
                # Skip elements inside blockquote to avoid double processing text
                if element.find_parent('blockquote'):
                    continue
                if element.name == 'p':
                    # Normalize whitespace, strip tabs and multiple newlines
                    text = re.sub(r'\s+', ' ', element.text).strip()
                    if len(text) > 20 and not is_junk_text(text):
                        content_blocks.append({"type": "p", "content": text})
                elif element.name in ('h2', 'h3', 'h4'):
                    text = re.sub(r'\s+', ' ', element.text).strip()
                    if text and not is_junk_text(text):
                        content_blocks.append({"type": "h", "level": int(element.name[1]), "content": text})
                elif element.name == 'img':
                    src = element.get('src') or element.get('data-src') or element.get('data-lazy-src')
                    if src and not src.startswith('data:'):
                        src = src.strip()
                        if src.startswith('//'):
                            src = 'https:' + src
                        # Skip placeholder/fallback images
                        if not any(p in src.lower() for p in ['fallback.gif', 'placeholder.gif', 'placeholder.png', 'spacer.gif', 'pixel.gif', 'lazyload']):
                            local_src = download_and_cache_image(src)
                            content_blocks.append({"type": "img", "content": local_src})
                elif element.name == 'blockquote':
                    text = re.sub(r'\s+', ' ', element.text).strip()
                    if text and not is_junk_text(text):
                        content_blocks.append({"type": "quote", "content": text})
                        
            if not content_blocks:
                for p in main_body.find_all('p'):
                    text = p.text.strip()
                    if len(text) > 10:
                        content_blocks.append({"type": "p", "content": text})
                        
            if not content_blocks and matching_article:
                if matching_article.get("thumbnail"):
                    local_thumb = download_and_cache_image(matching_article["thumbnail"])
                    content_blocks.append({"type": "img", "content": local_thumb})
                if matching_article.get("description"):
                    paragraphs = [p.strip() for p in matching_article["description"].split('\n') if p.strip()]
                    for p in paragraphs:
                        content_blocks.append({"type": "p", "content": p})
                        
            result = {
                "title": title,
                "url": article_url,
                "blocks": content_blocks
            }
            
            try:
                os.makedirs(cache_dir, exist_ok=True)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4)
            except:
                pass
                
            self.send_json_response(200, result)
            
        except Exception as e:
            self.send_json_response(500, {"error": f"Failed to scrape article (you might be offline): {str(e)}"})

    def handle_activity_log(self):
        log_file = os.path.join(DIRECTORY, "assets", "activity_log.json")
        with log_lock:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except:
                    logs = get_default_activities()
            else:
                logs = get_default_activities()
                try:
                    os.makedirs(os.path.dirname(log_file), exist_ok=True)
                    with open(log_file, 'w', encoding='utf-8') as f:
                        json.dump(logs, f, indent=4)
                except:
                    pass
        self.send_json_response(200, logs)

    def handle_add_news_source(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            name = (params.get("name") or "").strip()
            url = (params.get("url") or params.get("feed_url") or "").strip()
            category = (params.get("category") or "General").strip()
            section = (params.get("section") or "Entertainment").strip()
            avatar_base64 = (params.get("avatar_base64") or params.get("logo_base64") or "").strip()

            _record, _err = _detect_and_build_source(
                {"name": name, "url": url, "category": category,
                 "section": section, "is_rss": params.get("is_rss", True)},
                {"category": "General", "section": "Entertainment"})
            if _err or not _record:
                self.send_json_response(400, {"error": _err or "Could not parse source"})
                return
            name = _record["name"]
            url = _record["url"]
            category = _record["category"]
            section = _record["section"]
            
            if not name or not url:
                self.send_json_response(400, {"error": "Name and URL are required"})
                return
                
            sources = load_custom_sources()
            _dup = any(s.get("name", "").lower() == name.lower() for s in sources)
            _dup = _dup or any(s.get("url", "").lower() == url.lower() for s in sources)
            if _dup:
                self.send_json_response(400, {"error": "A news source with this name or URL already exists"})
                return
                
            avatar_path = ""
            if avatar_base64:
                try:
                    import base64
                    header, encoded = avatar_base64.split(",", 1)
                    file_ext = "png"
                    if "image/jpeg" in header or "image/jpg" in header:
                        file_ext = "jpg"
                    elif "image/svg" in header:
                        file_ext = "svg"
                        
                    avatar_filename = f"{hashlib.md5(name.encode('utf-8')).hexdigest()}.{file_ext}"
                    avatar_dir = os.path.join(DIRECTORY, "assets", "custom_avatars")
                    os.makedirs(avatar_dir, exist_ok=True)
                    avatar_fullpath = os.path.join(avatar_dir, avatar_filename)
                    
                    with open(avatar_fullpath, "wb") as fh:
                        fh.write(base64.b64decode(encoded))
                        
                    avatar_path = f"assets/custom_avatars/{avatar_filename}"
                except Exception as e:
                    print(f"Error saving custom avatar: {e}")
                    
            record = {
                "name": name,
                "url": url,
                "category": category,
                "avatar_path": avatar_path,
                "is_rss": _record.get("is_rss", params.get("is_rss", True)),
                "section": section
            }
            sources.append(record)
            save_custom_sources(sources)
            
            global news_cache
            with news_cache_lock:
                news_cache["last_fetched"] = 0
                
            log_system_activity("Custom Feeds", f"Added custom feed '{name}' ({url})")
            self.send_json_response(200, {"success": True, "source": record, "details": f"Custom news source '{name}' added successfully."})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_update_news_source(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            # The source being edited is identified by its CURRENT (original) name.
            original_name = (params.get("original_name") or params.get("name") or "").strip()
            if not original_name:
                self.send_json_response(400, {"error": "Missing source name"})
                return

            sources = load_custom_sources()
            target = next((s for s in sources if s["name"].lower() == original_name.lower()), None)
            if target is None:
                self.send_json_response(404, {"error": "News source not found"})
                return

            # New values; fall back to existing ones when a field is omitted.
            # Accept both "url"/"avatar_base64" and "feed_url"/"logo_base64" key styles.
            new_name = (params.get("new_name") or params.get("name") or target.get("name", "")).strip()
            new_url = (params.get("url") or params.get("feed_url") or target.get("url", "")).strip()
            new_category = (params.get("category") or target.get("category", "General")).strip()
            new_section = (params.get("section") or target.get("section", "Entertainment")).strip()
            avatar_base64 = (params.get("avatar_base64") or params.get("logo_base64") or "").strip()

            if not new_name or not new_url:
                self.send_json_response(400, {"error": "Name and URL are required"})
                return

            # Prevent renaming onto another existing source's name.
            if new_name.lower() != original_name.lower() and any(
                s["name"].lower() == new_name.lower() for s in sources
            ):
                self.send_json_response(400, {"error": "A news source with this name already exists"})
                return

            # Optionally replace the avatar (same logic as handle_add_news_source).
            if avatar_base64:
                try:
                    import base64
                    header, encoded = avatar_base64.split(",", 1)
                    file_ext = "png"
                    if "image/jpeg" in header or "image/jpg" in header:
                        file_ext = "jpg"
                    elif "image/svg" in header:
                        file_ext = "svg"

                    avatar_filename = f"{hashlib.md5(new_name.encode('utf-8')).hexdigest()}.{file_ext}"
                    avatar_dir = os.path.join(DIRECTORY, "assets", "custom_avatars")
                    os.makedirs(avatar_dir, exist_ok=True)
                    avatar_fullpath = os.path.join(avatar_dir, avatar_filename)

                    with open(avatar_fullpath, "wb") as fh:
                        fh.write(base64.b64decode(encoded))

                    target["avatar_path"] = f"assets/custom_avatars/{avatar_filename}"
                except Exception as e:
                    print(f"Error saving custom avatar: {e}")

            # Apply the edits in place.
            target["name"] = new_name
            target["url"] = new_url
            target["category"] = new_category
            target["section"] = new_section
            if "is_rss" in params:
                target["is_rss"] = params.get("is_rss", True)

            save_custom_sources(sources)

            global news_cache
            with news_cache_lock:
                news_cache["last_fetched"] = 0

            log_system_activity("Custom Feeds", f"Updated custom feed '{original_name}' -> '{new_name}'")
            self.send_json_response(200, {"success": True, "details": f"Custom news source '{new_name}' updated successfully."})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_add_news_sources_batch(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            text = params.get("text", "") or ""
            defaults = {
                "category": params.get("category") or "General",
                "section": params.get("section") or "Entertainment",
            }

            sources = load_custom_sources()
            existing_names = {s.get("name", "").lower() for s in sources}
            existing_urls = {s.get("url", "").lower() for s in sources}

            added = 0
            failed = 0
            errors = []

            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "|" in line:
                    nm, _, u = line.partition("|")
                    raw = {"name": nm.strip(), "url": u.strip()}
                elif "," in line and not line.lstrip().startswith("@"):
                    nm, _, u = line.partition(",")
                    raw = {"name": nm.strip(), "url": u.strip()}
                else:
                    raw = {"url": line}

                record, error = _detect_and_build_source(raw, defaults)
                if error or not record:
                    failed += 1
                    errors.append("%s: %s" % (line, error or "could not parse"))
                    continue
                if record["name"].lower() in existing_names or record["url"].lower() in existing_urls:
                    failed += 1
                    errors.append("%s: duplicate" % line)
                    continue

                sources.append(record)
                existing_names.add(record["name"].lower())
                existing_urls.add(record["url"].lower())
                added += 1

            if added:
                save_custom_sources(sources)
                with news_cache_lock:
                    news_cache["last_fetched"] = 0
                log_system_activity("Custom Feeds", f"Batch added {added} custom feed(s)")

            self.send_json_response(200, {"success": True, "added": added, "failed": failed, "errors": errors})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_import_opml(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))

            opml_text = params.get("opml", "") or ""
            defaults = {
                "category": params.get("category") or "General",
                "section": params.get("section") or "Entertainment",
            }

            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(opml_text)
            except Exception as parse_err:
                self.send_json_response(400, {"error": f"Invalid OPML: {parse_err}"})
                return

            sources = load_custom_sources()
            existing_names = {s.get("name", "").lower() for s in sources}
            existing_urls = {s.get("url", "").lower() for s in sources}

            added = 0
            failed = 0

            for outline in root.iter("outline"):
                xml_url = (outline.get("xmlUrl") or outline.get("xmlurl") or "").strip()
                if not xml_url:
                    continue
                title = (outline.get("title") or outline.get("text") or "").strip()
                record, error = _detect_and_build_source(
                    {"name": title, "url": xml_url, "is_rss": True}, defaults)
                if error or not record:
                    failed += 1
                    continue
                if record["name"].lower() in existing_names or record["url"].lower() in existing_urls:
                    failed += 1
                    continue
                sources.append(record)
                existing_names.add(record["name"].lower())
                existing_urls.add(record["url"].lower())
                added += 1

            if added:
                save_custom_sources(sources)
                with news_cache_lock:
                    news_cache["last_fetched"] = 0
                log_system_activity("Custom Feeds", f"Imported {added} source(s) from OPML")

            self.send_json_response(200, {"success": True, "added": added, "failed": failed})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_analyze_news_source(self):
        import requests
        from bs4 import BeautifulSoup
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            url = params.get("url", "").strip()
            if not url:
                self.send_json_response(400, {"error": "URL is required"})
                return
                
            # Add scheme if missing
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url
                
            # Fetch the URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            print(f"[News Analyzer] Fetching URL: {url}")
            r = requests.get(url, headers=headers, timeout=8)
            
            if r.status_code != 200:
                self.send_json_response(400, {"error": f"Could not access website (HTTP {r.status_code})"})
                return
                
            content_type = r.headers.get('Content-Type', '').lower()
            is_xml = 'xml' in content_type or 'rss' in content_type or 'atom' in content_type
            
            is_rss = False
            feed_url = url
            site_title = ""
            html_soup = None
            logo_url = ""
            
            def content_has_xml_tags(text):
                text_snippet = text[:1000].lower()
                return '<rss' in text_snippet or '<feed' in text_snippet or '<xml' in text_snippet
                
            if is_xml or content_has_xml_tags(r.text):
                is_rss = True
                rss_soup = BeautifulSoup(r.text, 'xml')
                channel = rss_soup.find('channel') or rss_soup.find('feed')
                if channel:
                    title_el = channel.find('title')
                    if title_el:
                        site_title = title_el.text.strip()
                    img_el = channel.find('image')
                    if img_el:
                        url_el = img_el.find('url')
                        if url_el:
                            logo_url = url_el.text.strip()
                            
                if channel:
                    link_el = channel.find('link')
                    if link_el:
                        home_url = link_el.text.strip() or link_el.get('href', '').strip()
                        if home_url and home_url.startswith('http'):
                            try:
                                r_home = requests.get(home_url, headers=headers, timeout=5)
                                if r_home.status_code == 200:
                                    html_soup = BeautifulSoup(r_home.text, 'html.parser')
                            except:
                                pass
            else:
                html_soup = BeautifulSoup(r.text, 'html.parser')
                
                title_tag = html_soup.find('title')
                og_site = html_soup.find('meta', property='og:site_name')
                if og_site and og_site.get('content'):
                    site_title = og_site.get('content').strip()
                elif title_tag:
                    site_title = title_tag.text.strip()
                    
                feed_link = html_soup.find('link', rel='alternate', type=lambda t: t and ('rss+xml' in t or 'atom+xml' in t or 'xml' in t))
                if feed_link and feed_link.get('href'):
                    resolved_feed = resolve_image_url(feed_link.get('href').strip(), url)
                    print(f"[News Analyzer] Found alternate RSS link: {resolved_feed}")
                    try:
                        r_feed = requests.get(resolved_feed, headers=headers, timeout=5)
                        if r_feed.status_code == 200 and content_has_xml_tags(r_feed.text):
                            is_rss = True
                            feed_url = resolved_feed
                            rss_soup = BeautifulSoup(r_feed.text, 'xml')
                            channel = rss_soup.find('channel') or rss_soup.find('feed')
                            if channel and channel.find('title'):
                                site_title = channel.find('title').text.strip()
                    except Exception as feed_err:
                        print(f"[News Analyzer] Failed to validate alternate link: {feed_err}")
                        
                if not is_rss:
                    parsed_url = urllib.parse.urlparse(url)
                    base_host = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    common_paths = ['/feed', '/rss', '/feed.xml', '/rss.xml']
                    for path in common_paths:
                        test_url = base_host + path
                        try:
                            r_test = requests.get(test_url, headers=headers, timeout=4)
                            if r_test.status_code == 200 and content_has_xml_tags(r_test.text):
                                is_rss = True
                                feed_url = test_url
                                rss_soup = BeautifulSoup(r_test.text, 'xml')
                                channel = rss_soup.find('channel') or rss_soup.find('feed')
                                if channel and channel.find('title'):
                                    site_title = channel.find('title').text.strip()
                                print(f"[News Analyzer] Found RSS feed at common path: {test_url}")
                                break
                        except:
                            pass
                            
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            cleaned_name = clean_site_name(site_title, url)
            
            if not logo_url and html_soup:
                logo_url = find_site_logo(html_soup, url)
                
            if not logo_url:
                logo_url = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
                
            logo_base64 = ""
            if logo_url:
                try:
                    print(f"[News Analyzer] Fetching site logo: {logo_url}")
                    r_logo = requests.get(logo_url, headers=headers, timeout=5)
                    if r_logo.status_code == 200:
                        import base64
                        content_type_logo = r_logo.headers.get('Content-Type', 'image/png')
                        encoded_body = base64.b64encode(r_logo.content).decode('utf-8')
                        logo_base64 = f"data:{content_type_logo};base64,{encoded_body}"
                except Exception as logo_err:
                    print(f"[News Analyzer] Failed to fetch/encode logo: {logo_err}")
                    
            self.send_json_response(200, {
                "success": True,
                "name": cleaned_name,
                "feed_url": feed_url,
                "is_rss": is_rss,
                "logo_base64": logo_base64
            })
            
        except Exception as e:
            import sys
            if not sys.is_finalizing():
                import traceback
                traceback.print_exc()
            self.send_json_response(500, {"error": str(e)})

    def handle_delete_news_source(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            name = params.get("name", "").strip()
            if not name:
                self.send_json_response(400, {"error": "Missing source name"})
                return
                
            sources = load_custom_sources()
            new_sources = [s for s in sources if s["name"].lower() != name.lower()]
            
            if len(sources) == len(new_sources):
                self.send_json_response(404, {"error": "News source not found"})
                return
                
            deleted_source = next(s for s in sources if s["name"].lower() == name.lower())
            if deleted_source.get("avatar_path"):
                full_avatar_path = os.path.join(DIRECTORY, deleted_source["avatar_path"])
                if os.path.exists(full_avatar_path):
                    try:
                        os.remove(full_avatar_path)
                    except:
                        pass
                        
            save_custom_sources(new_sources)
            
            global news_cache
            with news_cache_lock:
                news_cache["last_fetched"] = 0
                
            log_system_activity("Custom Feeds", f"Deleted custom feed '{name}'")
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_clear_cache(self):
        try:
            cache_dir = os.path.join(DIRECTORY, "assets", "cached_articles")
            deleted_count = 0
            if os.path.exists(cache_dir):
                for f in os.listdir(cache_dir):
                    if f.endswith(".json"):
                        os.remove(os.path.join(cache_dir, f))
                        deleted_count += 1
            
            log_file = os.path.join(DIRECTORY, "assets", "activity_log.json")
            if os.path.exists(log_file):
                os.remove(log_file)
                
            log_system_activity("Feed Aggregator", f"Cleared {deleted_count} offline cached articles and logs.")
            self.send_json_response(200, {"success": True, "deleted_count": deleted_count})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_reset_telegram_history(self):
        try:
            filepath = os.path.join(DIRECTORY, "assets", "sent_posts.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            log_system_activity("Telegram poster", "Reset Telegram forwarding history (sent posts logs cleared).")
            self.send_json_response(200, {"success": True})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

class SafeThreadingHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        import sys
        if sys.is_finalizing():
            return
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_val and isinstance(exc_val, (ConnectionError, OSError)):
            return
        super().handle_error(request, client_address)

_server_instance = None

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(("127.0.0.1", port))
            return True
        except ConnectionRefusedError:
            return False
        except Exception:
            return True

def start_server():
    global _server_instance, PORT

    # Hydrate the in-memory cache from disk so the first refresh has a correct
    # "removed from feed" baseline and the feed is viewable offline at launch.
    try:
        snapshot = feed_store.load_feed_snapshot()
        if snapshot:
            with news_cache_lock:
                if not news_cache["data"]:
                    news_cache["data"] = snapshot
    except Exception as _e:
        print(f"[Server] Feed snapshot hydrate skipped: {_e}")

    settings_path = os.path.join(DIRECTORY, "assets", "ui_settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = data[0] if (isinstance(data, list) and len(data) > 0) else (data if isinstance(data, dict) else {})
            initial_port = loaded.get("advanced", {}).get("backend_port")
            if initial_port:
                PORT = int(initial_port)
        except Exception:
            pass

    max_attempts = 50
    for attempt in range(max_attempts):
        if is_port_in_use(PORT):
            print(f"[Server] Port {PORT} is already in use (active listener), trying next port...")
            PORT += 1
            continue
        try:
            _server_instance = SafeThreadingHTTPServer(("127.0.0.1", PORT), GUIHandler)
            break
        except OSError:
            if attempt < max_attempts - 1:
                print(f"[Server] Port {PORT} is already in use (bind failed), trying next port...")
                PORT += 1
            else:
                raise

    # Save the actual bound port back to ui_settings.json
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            is_list = isinstance(data, list)
            loaded = data[0] if (is_list and len(data) > 0) else (data if isinstance(data, dict) else {})
            if "advanced" not in loaded:
                loaded["advanced"] = {}
            loaded["advanced"]["backend_port"] = PORT
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump([loaded] if is_list else loaded, f, indent=4, ensure_ascii=False)
            print(f"[Server] Updated ui_settings.json backend_port to {PORT}")
        except Exception as e:
            print(f"[Server] Failed to write back new port to ui_settings.json: {e}")

    print(f"=====================================================")
    print(f"            OFFLINEFEED SERVER IS ONLINE             ")
    print(f"=====================================================")
    print(f"   -> App UI:  http://127.0.0.1:{PORT}")
    print(f"   -> Data Root:     {DIRECTORY}")
    print(f"=====================================================")
    print(f"Opening your browser to OfflineFeed...")
    
    threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    
    try:
        _server_instance.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down OfflineFeed...")
        _server_instance.server_close()

def stop_server():
    global _server_instance
    if _server_instance:
        try:
            _server_instance.shutdown()
            _server_instance.server_close()
        except Exception:
            pass

if __name__ == "__main__":
    start_server()
