from __future__ import annotations
import os
import re
import sys
import json
import ast
import argparse
import urllib.parse
import shutil
import tempfile
from pathlib import Path

# Try to import Pillow for image normalization
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Try to import requests and BeautifulSoup
try:
    import requests
    from bs4 import BeautifulSoup
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

REPO_ROOT = Path(__file__).resolve().parent.parent
DIRECTORY = REPO_ROOT / "offline_viewer"
AVATARS_DIR = DIRECTORY / "assets" / "avatars"

def slugify(name: str) -> str:
    """Normalize source name into a safe file slug."""
    slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug or "channel"

def get_clean_site_name(name: str) -> str:
    """Standardized name cleaning mirroring gui_server.py."""
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
    return name

def get_default_sources_ast() -> list:
    """Statically parse gui_server.py using AST to find hardcoded default sources."""
    gui_server_path = REPO_ROOT / "gui_server.py"
    if not gui_server_path.exists():
        return []
    try:
        content = gui_server_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "fetch_and_aggregate_news":
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Name) and target.id == "sources":
                                return ast.literal_eval(stmt.value)
    except Exception as e:
        print(f"Error parsing default sources from gui_server.py: {e}")
    return []

def load_custom_sources() -> list:
    """Load custom sources from custom_sources.json."""
    filepath = DIRECTORY / "assets" / "custom_sources.json"
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def save_custom_sources_atomic(sources: list) -> None:
    """Atomically write custom sources to custom_sources.json, keeping a .bak backup."""
    filepath = DIRECTORY / "assets" / "custom_sources.json"
    if filepath.exists():
        shutil.copy2(filepath, filepath.with_suffix(".json.bak"))
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    dir_name = filepath.parent
    fd, temp_path_str = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=4, ensure_ascii=False)
        shutil.move(temp_path_str, filepath)
    except Exception as e:
        if os.path.exists(temp_path_str):
            os.remove(temp_path_str)
        raise e

def load_defaults_index() -> dict:
    """Load default sources avatar mapping index.json."""
    filepath = AVATARS_DIR / "index.json"
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def save_defaults_index_atomic(mapping: dict) -> None:
    """Atomically write default sources avatar mapping index.json."""
    filepath = AVATARS_DIR / "index.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    dir_name = filepath.parent
    fd, temp_path_str = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=4, ensure_ascii=False)
        shutil.move(temp_path_str, filepath)
    except Exception as e:
        if os.path.exists(temp_path_str):
            os.remove(temp_path_str)
        raise e

def check_image_usability(content: bytes, content_type: str) -> bool:
    """Reject tiny, empty, or non-image content."""
    if "html" in content_type.lower() or "text" in content_type.lower():
        return False
    if len(content) < 500:
        return False
    
    if HAS_PILLOW:
        import io
        try:
            img = Image.open(io.BytesIO(content))
            w, h = img.size
            if w < 48 or h < 48:
                return False
            return True
        except Exception:
            return False
    return True

def crop_and_resize(img_bytes: bytes, target_size=(128, 128)) -> bytes | None:
    """Center-crop to square and resize to target_size using Pillow."""
    if not HAS_PILLOW:
        return img_bytes
    import io
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))
        
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception:
        return None

def fetch_best_logo(url: str) -> tuple[bytes, str] | None:
    """Try various methods in order to resolve the best high-quality logo."""
    if not HAS_LIBS:
        return None

    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if "bbci.co.uk" in domain:
            domain = "bbc.com"
            site_url = "https://www.bbc.com/sport"
        else:
            parts = domain.split(".")
            if len(parts) > 2 and parts[0] in ("feeds", "feed", "rss"):
                domain = ".".join(parts[1:])
            site_url = f"{parsed.scheme}://{domain}"
    except Exception:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    def try_url(candidate_url: str) -> tuple[bytes, str] | None:
        try:
            res = requests.get(candidate_url, headers=headers, timeout=5)
            if res.status_code == 200:
                ct = res.headers.get("Content-Type", "")
                if check_image_usability(res.content, ct):
                    return res.content, ct
        except Exception:
            pass
        return None

    # Fetch site HTML for links
    soup = None
    try:
        site_res = requests.get(site_url, headers=headers, timeout=6)
        if site_res.status_code == 200:
            soup = BeautifulSoup(site_res.content, "html.parser")
    except Exception:
        pass

    if soup:
        # (a) apple-touch-icon (sorted largest first)
        apple_icons = []
        for link in soup.find_all("link"):
            rel = [r.lower() for r in (link.get("rel") or [])]
            if "apple-touch-icon" in rel or "apple-touch-icon-precomposed" in rel:
                href = link.get("href")
                if href:
                    sizes = link.get("sizes") or ""
                    width = 0
                    if sizes:
                        parts = sizes.split("x")
                        if len(parts) == 2:
                            try:
                                width = int(parts[0])
                            except ValueError:
                                pass
                    apple_icons.append((width, urllib.parse.urljoin(site_url, href)))
        apple_icons.sort(key=lambda x: x[0], reverse=True)
        for _, icon_url in apple_icons:
            res = try_url(icon_url)
            if res:
                return res

        # (b) Open Graph og:image / twitter:image
        og_urls = []
        for meta in soup.find_all("meta"):
            prop = meta.get("property") or meta.get("name") or ""
            if prop.lower() in ("og:image", "twitter:image"):
                content = meta.get("content")
                if content:
                    og_urls.append(urllib.parse.urljoin(site_url, content))
        for img_url in og_urls:
            res = try_url(img_url)
            if res:
                return res

        # (c) link icon / manifest icons
        favicons = []
        for link in soup.find_all("link"):
            rel = [r.lower() for r in (link.get("rel") or [])]
            if "icon" in rel or "shortcut icon" in rel:
                href = link.get("href")
                if href:
                    sizes = link.get("sizes") or ""
                    width = 0
                    if sizes:
                        parts = sizes.split("x")
                        if len(parts) == 2:
                            try:
                                width = int(parts[0])
                            except ValueError:
                                pass
                    favicons.append((width, urllib.parse.urljoin(site_url, href)))
        favicons.sort(key=lambda x: x[0], reverse=True)
        for _, icon_url in favicons:
            res = try_url(icon_url)
            if res:
                return res

    # (d) Logo services
    logo_services = [
        f"https://logo.clearbit.com/{domain}",
        f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
    ]
    for service_url in logo_services:
        res = try_url(service_url)
        if res:
            return res

    # (e) Last resort favicon.ico
    res = try_url(f"{site_url}/favicon.ico")
    if res:
        return res

    return None

def is_avatar_usable(file_path: Path) -> bool:
    """Check if avatar file exists and is usable."""
    if not file_path.exists():
        return False
    try:
        if HAS_PILLOW:
            img = Image.open(file_path)
            w, h = img.size
            return w >= 48 and h >= 48
        else:
            return file_path.stat().st_size > 1000
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="Fix and fetch high-quality news channel avatars.")
    parser.add_argument("--force", "--overwrite", action="store_true", help="Refetch and replace existing avatars.")
    parser.add_argument("--only", type=str, help="Fix only a single source by name.")
    parser.add_argument("--set", type=str, help="Set a specific source avatar manually from a local file.")
    parser.add_argument("--file", type=str, help="Path to local file (used with --set).")
    parser.add_argument("--list", action="store_true", help="List all channels, their domains, and status.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing to disk.")
    args = parser.parse_args()

    if not HAS_LIBS:
        print("Error: Missing required packages requests and beautifulsoup4.")
        sys.exit(1)

    # 1. Enumerate sources
    custom_sources = load_custom_sources()
    default_sources_raw = get_default_sources_ast()

    unified_sources = {}

    # Parse default sources
    for item in default_sources_raw:
        raw_name = item[0]
        cleaned_name = get_clean_site_name(raw_name)
        url = item[1]
        
        # Deduplicate defaults under cleaned name
        if cleaned_name not in unified_sources:
            unified_sources[cleaned_name] = {
                "name": cleaned_name,
                "url": url,
                "is_custom": False,
                "avatar_path": ""
            }

    # Parse custom sources (taking precedence / merging)
    for s in custom_sources:
        name = s.get("name", "").strip()
        if not name:
            continue
        cleaned_name = name # custom names are kept as-is
        url = s.get("url") or s.get("feed_url") or ""
        ap = s.get("avatar_path") or ""
        
        unified_sources[cleaned_name] = {
            "name": cleaned_name,
            "url": url,
            "is_custom": True,
            "avatar_path": ap
        }

    # If --only filter is set
    if args.only:
        filtered = {k: v for k, v in unified_sources.items() if k.lower() == args.only.lower()}
        if not filtered:
            print(f"Source '{args.only}' not found.")
            sys.exit(1)
        unified_sources = filtered

    # If --set manual override
    if args.set:
        if not args.file:
            print("Error: --file <path> is required when using --set.")
            sys.exit(1)
        local_path = Path(args.file)
        if not local_path.exists():
            print(f"Error: Local file '{local_path}' does not exist.")
            sys.exit(1)

        source_name = args.set
        matching_source = None
        for name, src in unified_sources.items():
            if name.lower() == source_name.lower():
                matching_source = src
                break

        if not matching_source:
            # Create a custom source placeholder
            matching_source = {
                "name": source_name,
                "url": "",
                "is_custom": True,
                "avatar_path": ""
            }
            unified_sources[source_name] = matching_source

        slug = slugify(matching_source["name"])
        target_rel_path = f"assets/avatars/{slug}.png"
        target_abs_path = DIRECTORY / target_rel_path

        print(f"Setting avatar for '{matching_source['name']}' from local file '{local_path}'...")
        if not args.dry_run:
            try:
                target_abs_path.parent.mkdir(parents=True, exist_ok=True)
                img_bytes = local_path.read_bytes()
                normalized = crop_and_resize(img_bytes)
                if normalized:
                    target_abs_path.write_bytes(normalized)
                    print(f"Normalized and saved to {target_abs_path}")
                else:
                    shutil.copy2(local_path, target_abs_path)
                    print(f"Copied raw file to {target_abs_path}")

                # Update data model
                if matching_source["is_custom"]:
                    # Update custom_sources.json
                    sources_json = load_custom_sources()
                    for cs in sources_json:
                        if cs.get("name", "").lower() == matching_source["name"].lower():
                            cs["avatar_path"] = target_rel_path
                            break
                    save_custom_sources_atomic(sources_json)
                else:
                    # Update index.json
                    index_map = load_defaults_index()
                    index_map[matching_source["name"].lower()] = target_rel_path
                    save_defaults_index_atomic(index_map)
                print("Successfully updated avatar mapping.")
            except Exception as e:
                print(f"Error saving avatar: {e}")
                sys.exit(1)
        else:
            print(f"[DRY-RUN] Would save '{local_path}' to '{target_abs_path}'")
        sys.exit(0)

    # If --list flag
    if args.list:
        print(f"{'Source Name':<30} | {'Domain':<25} | {'Custom':<8} | {'Avatar Status'}")
        print("-" * 80)
        index_map = load_defaults_index()
        for name, src in sorted(unified_sources.items()):
            domain = urllib.parse.urlparse(src["url"]).netloc if src["url"] else "N/A"
            ap = src["avatar_path"]
            if not src["is_custom"]:
                ap = index_map.get(name.lower()) or ""
            
            status = "No avatar"
            if ap:
                file_path = DIRECTORY / ap
                if file_path.exists():
                    status = f"Usable ({ap})" if is_avatar_usable(file_path) else f"Unusable ({ap})"
                else:
                    status = f"Missing file ({ap})"
            print(f"{name:<30} | {domain:<25} | {str(src['is_custom']):<8} | {status}")
        sys.exit(0)

    # Main avatar-fixing pass
    print("Running news avatar-fixing pass...")
    index_map = load_defaults_index()
    
    summary = {
        "fetched": 0,
        "replaced": 0,
        "kept": 0,
        "failed": 0
    }

    custom_updated = False
    defaults_updated = False

    for name, src in sorted(unified_sources.items()):
        url = src["url"]
        domain = urllib.parse.urlparse(url).netloc if url else ""
        slug = slugify(name)
        
        target_rel_path = f"assets/avatars/{slug}.png"
        target_abs_path = DIRECTORY / target_rel_path

        # Determine current avatar path
        curr_rel = src["avatar_path"] if src["is_custom"] else index_map.get(name.lower(), "")
        curr_abs = DIRECTORY / curr_rel if curr_rel else None

        # Check if already has a usable avatar
        has_usable = False
        if curr_abs and curr_abs.exists() and is_avatar_usable(curr_abs):
            has_usable = True

        # Decide whether to fetch
        should_fetch = args.force or not has_usable

        if not should_fetch:
            print(f"[=] kept     '{name}' (already has usable avatar: {curr_rel})")
            summary["kept"] += 1
            continue

        if not url:
            print(f"[-] failed   '{name}' (no feed/site URL available)")
            summary["failed"] += 1
            continue

        print(f"Fetching avatar for '{name}' ({domain})...")
        logo_res = fetch_best_logo(url)
        
        if logo_res:
            img_bytes, ct = logo_res
            normalized = crop_and_resize(img_bytes)
            
            if normalized:
                if not args.dry_run:
                    try:
                        AVATARS_DIR.mkdir(parents=True, exist_ok=True)
                        target_abs_path.write_bytes(normalized)
                    except Exception as e:
                        print(f"[-] failed   '{name}' (error writing file: {e})")
                        summary["failed"] += 1
                        continue
                
                action = "replaced" if has_usable else "fetched"
                print(f"[+] {action:<8} '{name}' -> {target_rel_path}")
                summary[action] += 1

                # Update maps
                if src["is_custom"]:
                    for cs in custom_sources:
                        if cs.get("name", "").lower() == name.lower():
                            cs["avatar_path"] = target_rel_path
                            custom_updated = True
                            break
                else:
                    index_map[name.lower()] = target_rel_path
                    defaults_updated = True
            else:
                print(f"[-] failed   '{name}' (normalization failed)")
                summary["failed"] += 1
        else:
            print(f"[-] failed   '{name}' (could not find or download usable logo)")
            summary["failed"] += 1

    # Persist updates
    if not args.dry_run:
        if custom_updated:
            try:
                save_custom_sources_atomic(custom_sources)
                print("Atomic custom sources JSON saved.")
            except Exception as e:
                print(f"Error saving custom sources: {e}")
        
        if defaults_updated:
            try:
                save_defaults_index_atomic(index_map)
                print("Atomic default sources index JSON saved.")
            except Exception as e:
                print(f"Error saving defaults index: {e}")
    else:
        print("[DRY-RUN] Completed. No files written.")

    print("\nSummary:")
    print(f"  Fetched:  {summary['fetched']}")
    print(f"  Replaced: {summary['replaced']}")
    print(f"  Kept:     {summary['kept']}")
    print(f"  Failed:   {summary['failed']}")

if __name__ == "__main__":
    main()
