#!/usr/bin/env python3
"""
OfflineFeed - Tabler icon batch importer
========================================

WHAT THIS DOES
--------------
Copies just the icons you want out of the (huge) Tabler set into the app's icon
folder, renaming each to a STABLE LOGICAL NAME so QML can use it as
`Icon { name: "web-viewer" }` regardless of Tabler's real filename.

HOW TO ADD AN ICON (the whole workflow)
---------------------------------------
1. Open  tools/icons.manifest.json
2. Add one line:   "logical-name": "tabler-source-filename"   (no .svg)
                   e.g.  "field-rss": "rss"
3. Re-run:         python tools/import_icons.py
4. Use in QML:     Icon { name: "field-rss"; color: Theme.accent; size: 18 }

Re-running is safe and idempotent: it overwrites cleanly and prints exactly what
was imported and which manifest entries had no matching source SVG.

SOURCE / DEST
-------------
Source : the Tabler repo already on disk (default below; override with
         --source PATH or env var TABLER_ICONS_DIR).
Dest   : frontend/qml/assets/icons/  (resolved relative to this script, so it
         works no matter what folder you run it from).
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

# --- Paths -----------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent           # .../OfflineFeed/tools
REPO_ROOT = SCRIPT_DIR.parent                          # .../OfflineFeed
DEST_DIR = REPO_ROOT / "frontend" / "qml" / "assets" / "icons"
MANIFEST_PATH = SCRIPT_DIR / "icons.manifest.json"

# Default Tabler location (override with --source or TABLER_ICONS_DIR).
DEFAULT_SOURCE = os.environ.get(
    "TABLER_ICONS_DIR", r"E:\Projects\2-svg\tabler-icons-main"
)

# Seed manifest, written out the first time you run this if none exists.
# logical name (how QML refers to it)  :  Tabler source filename (no .svg)
DEFAULT_MANIFEST: dict[str, str] = {
    # --- the three this unblocks ---
    "web-viewer": "world-www",      # web / offline reader open button
    "twitter-x": "brand-x",         # Twitter / X source badge
    # --- field / source glyphs the UI needs (extend freely) ---
    "field-link": "link",
    "field-rss": "rss",
    "field-date": "calendar-event",
    "field-time": "clock",
    "field-tag": "tag",
    "field-author": "user",
    "field-title": "heading",
    "source-web": "world",
    "source-telegram": "brand-telegram",
}

# Tabler folder layout, in preference order (outline first so icons stay
# line-style + cleanly tintable). We also fall back to a recursive search.
SEARCH_SUBDIRS = ("icons/outline", "icons/filled", "icons")

CURRENT_COLOR_RE = re.compile(r"currentColor", re.IGNORECASE)


def load_manifest() -> list[tuple[str, str, str | None]]:
    """Return [(logical, source_base, variant_or_None), ...].

    Manifest value may be a string ("rss") or an object
    ({"source": "rss", "variant": "filled"}).
    """
    if not MANIFEST_PATH.exists():
        MANIFEST_PATH.write_text(
            json.dumps(DEFAULT_MANIFEST, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[import_icons] wrote seed manifest -> {MANIFEST_PATH}")
        raw: dict = dict(DEFAULT_MANIFEST)
    else:
        raw = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    entries: list[tuple[str, str, str | None]] = []
    for logical, value in raw.items():
        if isinstance(value, str):
            entries.append((logical, value, None))
        elif isinstance(value, dict) and value.get("source"):
            entries.append((logical, value["source"], value.get("variant")))
        else:
            print(f"[import_icons] WARN bad manifest entry {logical!r}, skipped")
    return entries


def find_source(root: Path, base: str, variant: str | None) -> Path | None:
    name = base if base.endswith(".svg") else base + ".svg"
    if variant:
        cand = root / "icons" / variant / name
        if cand.is_file():
            return cand
    for sub in SEARCH_SUBDIRS:
        cand = root / sub / name
        if cand.is_file():
            return cand
    # Recursive fallback; prefer an 'outline' path if several match.
    matches = sorted(
        root.rglob(name),
        key=lambda p: (0 if "outline" in p.parts else 1, len(p.parts)),
    )
    return matches[0] if matches else None


def normalize_svg(text: str) -> str:
    """Force a solid white stroke/fill so ColorOverlay in Icon.qml can recolor
    the glyph to any theme color. Tabler uses stroke="currentColor", which Qt's
    SVG renderer treats as black; white keeps the same convention as
    gen_assets.py."""
    return CURRENT_COLOR_RE.sub("#ffffff", text)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Batch-import Tabler SVGs into OfflineFeed."
    )
    ap.add_argument("--source", default=DEFAULT_SOURCE,
                    help="Path to tabler-icons-main")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report only; write nothing")
    args = ap.parse_args()

    root = Path(args.source)
    if not root.is_dir():
        print(f"[import_icons] ERROR source not found: {root}")
        print("  Pass --source PATH or set TABLER_ICONS_DIR.")
        return 2

    DEST_DIR.mkdir(parents=True, exist_ok=True)
    entries = load_manifest()

    imported: list[tuple[str, Path]] = []
    missing: list[tuple[str, str]] = []
    for logical, base, variant in entries:
        src = find_source(root, base, variant)
        if src is None:
            missing.append((logical, base))
            continue
        if not args.dry_run:
            svg = normalize_svg(src.read_text(encoding="utf-8"))
            (DEST_DIR / f"{logical}.svg").write_text(svg, encoding="utf-8")
        imported.append((logical, src.relative_to(root)))

    print()
    print(f"[import_icons] source : {root}")
    print(f"[import_icons] dest   : {DEST_DIR}")
    print(f"[import_icons] manifest entries: {len(entries)}")
    print(f"[import_icons] imported ({len(imported)}):")
    for logical, rel in imported:
        print(f"    {logical}.svg   <- {rel}")
    if missing:
        print(f"[import_icons] MISSING ({len(missing)}) - no source SVG found:")
        for logical, base in missing:
            print(f"    {logical}   (looked for {base}.svg)")
    else:
        print("[import_icons] no missing icons")
    if args.dry_run:
        print("[import_icons] (dry-run: no files written)")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
