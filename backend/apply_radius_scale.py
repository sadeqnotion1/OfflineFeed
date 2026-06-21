#!/usr/bin/env python3
"""
apply_radius_scale.py - OfflineFeed corner-radius normalization (additive, safe).

WHAT IT DOES (never changes component sizes - only corner radii):
  1. Adds ONE radius scale to the Theme singleton
     (frontend/qml/themes/Theme.qml) if it isn't already there:
         readonly property var radius: ({ "sm": 8, "md": 12, "lg": 18, "pill": 9999 })
  2. Replaces the *verified* literal `radius:` values in the components that
     were audited with the matching Theme.radius.<tier> token.
  3. Greps every .qml under frontend/qml for any remaining literal radius
     numbers and prints them with a recommended tier, so the pass can be
     finished on files that were not part of the audited set.

SAFETY:
  * Run it from the OfflineFeed repo root (the folder with run_offlinefeed.py).
  * It writes a `.bak` next to every file it edits (in addition to the full
    repo backup you should take first - see APPLY.md step 1).
  * It refuses to write a change whose anchor count does not match what was
    audited, so it can NOT silently corrupt a file.
  * It is idempotent: running it twice is safe (already-applied edits are
    detected and skipped).

USAGE:
    python apply_radius_scale.py            # apply
    python apply_radius_scale.py --check    # dry run: report only, write nothing
"""
from __future__ import annotations

import re
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QML = ROOT / "frontend" / "qml"
THEME = QML / "themes" / "Theme.qml"

CHECK = "--check" in sys.argv[1:]

# ----------------------------------------------------------------------------
# 1) Theme.radius scale - inserted right after the existing bubbleRadius metric.
# ----------------------------------------------------------------------------
THEME_ANCHOR = "    readonly property int bubbleRadius: 13\n"
RADIUS_BLOCK = (
    "\n"
    "    // ----- Corner radius scale (single source of truth) -----\n"
    "    // Bind components to these tokens instead of hard-coding literal radius\n"
    "    // numbers, so corner rounding stays consistent across cards, inputs,\n"
    "    // chips, badges and avatars. (Sizes are unchanged - only corner radii.)\n"
    "    //   sm   -> small chips / tags\n"
    "    //   md   -> inputs / search fields\n"
    "    //   lg   -> cards / message bubbles\n"
    "    //   pill -> fully rounded (badges, avatars, pill buttons, toasts)\n"
    "    // `pill` is a large constant; Qt clamps radius to min(w,h)/2, so it\n"
    "    // yields a perfect pill for any height and a circle for square items.\n"
    '    readonly property var radius: ({ "sm": 8, "md": 12, "lg": 18, "pill": 9999 })\n'
)

# ----------------------------------------------------------------------------
# 2) Verified component edits.  file -> list of (old, new, expected_count)
#    Only files that were actually read are listed here. Everything else is
#    surfaced by the grep report in step 3.
# ----------------------------------------------------------------------------
EDITS = {
    "components/ChatList.qml": [
        # Search field (input) -> md
        ("radius: 18", "radius: Theme.radius.md", 1),
    ],
    "components/ChatView.qml": [
        # Pinned-post accent bar (2px) -> pill (clamps to 1px end; identical)
        ("width: 2; height: 18; radius: 1; color: Theme.accent",
         "width: 2; height: 18; radius: Theme.radius.pill; color: Theme.accent", 1),
        # In-channel search field (input) -> md
        ("radius: 18; color: Theme.panelAlt",
         "radius: Theme.radius.md; color: Theme.panelAlt", 1),
        # Forward-channel + Empty-Bin pill buttons (h=38) -> pill (identical)
        ("radius: 19", "radius: Theme.radius.pill", 2),
    ],
    "components/SearchResultsView.qml": [
        # Source + section label chips (h=20) -> sm  (slightly squarer: 10 -> 8)
        ("radius: 10", "radius: Theme.radius.sm", 2),
        # Read/Viewer/Open pill action buttons (h=28) -> pill (identical)
        ("radius: 14", "radius: Theme.radius.pill", 3),
    ],
    "components/Avatar.qml": [
        # Gradient disc + clipped image -> pill (circle; identical to width/2)
        ("radius: width / 2", "radius: Theme.radius.pill", 2),
    ],
    "Main.qml": [
        # Toast pill (h=40) -> pill (identical)
        ("radius: 20", "radius: Theme.radius.pill", 1),
    ],
}


def info(msg: str) -> None:
    print(msg)


def backup(path: Path) -> None:
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(path, bak)


def patch_theme() -> None:
    if not THEME.exists():
        info(f"[SKIP] Theme not found: {THEME}")
        return
    text = THEME.read_text(encoding="utf-8")
    if "property var radius" in text:
        info("[ok]   Theme.qml: radius scale already present - nothing to do.")
        return
    if THEME_ANCHOR not in text:
        info("[WARN] Theme.qml: could not find the bubbleRadius anchor; "
             "add the radius block manually (see RADIUS_SCALE.md).")
        return
    new = text.replace(THEME_ANCHOR, THEME_ANCHOR + RADIUS_BLOCK, 1)
    if CHECK:
        info("[plan] Theme.qml: would add Theme.radius scale.")
        return
    backup(THEME)
    THEME.write_text(new, encoding="utf-8")
    info("[done] Theme.qml: added Theme.radius scale.")


def patch_file(rel: str, edits) -> None:
    path = QML / rel
    if not path.exists():
        info(f"[SKIP] {rel}: file not found.")
        return
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new, expected in edits:
        count = text.count(old)
        if count == 0:
            if new in text:
                info(f"[ok]   {rel}: '{old}' already applied.")
                continue
            info(f"[WARN] {rel}: anchor not found: '{old}' "
                 f"(expected {expected}). Skipped - verify manually.")
            return
        if count != expected:
            info(f"[WARN] {rel}: anchor '{old}' found {count}x "
                 f"(expected {expected}). Skipped this FILE to stay safe.")
            return
        text = text.replace(old, new)
    if text == original:
        return
    if CHECK:
        info(f"[plan] {rel}: would apply {len(edits)} radius edit(s).")
        return
    backup(path)
    path.write_text(text, encoding="utf-8")
    info(f"[done] {rel}: radius tokens applied.")


# Lowercase `radius:` only (so `bubbleRadius:`/`Radius:` are ignored), and skip
# any value that already points at the Theme.radius scale.
LITERAL_RADIUS = re.compile(r"(?<![A-Za-z])radius:\s*(?!Theme\.radius)([^\n;{]+)")


def recommend(value: str) -> str:
    v = value.strip().rstrip(";").strip()
    if "/ 2" in v or "/2" in v:
        return "pill (currently fully rounded)"
    try:
        n = float(v)
    except ValueError:
        return "review (dynamic expression)"
    if n <= 2:
        return "pill or sm (tiny indicator)"
    if n <= 9:
        return "sm (small chip)"
    if n <= 14:
        return "md (input) or pill if it equals height/2"
    return "lg (card/bubble) or pill if it equals height/2"


def grep_report() -> None:
    info("\n=== Remaining literal radius values under frontend/qml ===")
    info("(Theme.qml is excluded; finish these using the tier table in "
         "RADIUS_SCALE.md.)\n")
    found = 0
    for qml in sorted(QML.rglob("*.qml")):
        if qml.resolve() == THEME.resolve():
            continue
        for i, line in enumerate(qml.read_text(encoding="utf-8").splitlines(), 1):
            for m in LITERAL_RADIUS.finditer(line):
                val = m.group(1).strip()
                # Ignore values that are already tokens or bindings to Theme.
                if val.startswith("Theme."):
                    continue
                rel = qml.relative_to(QML)
                info(f"  {rel}:{i}: radius: {val}")
                info(f"      -> suggest: {recommend(val)}")
                found += 1
    if found == 0:
        info("  None - every component now uses a Theme.radius token. \u2713")
    else:
        info(f"\n  {found} literal radius value(s) still need a tier decision.")


def main() -> int:
    if not QML.exists():
        info(f"ERROR: {QML} not found. Run this from the OfflineFeed repo root "
             "(the folder that contains run_offlinefeed.py).")
        return 2
    info("OfflineFeed radius-scale pass" + ("  [--check dry run]" if CHECK else ""))
    info("-" * 60)
    patch_theme()
    for rel, edits in EDITS.items():
        patch_file(rel, edits)
    grep_report()
    info("\nDone. Now run:  python run_offlinefeed.py")
    if CHECK:
        info("(dry run - no files were modified.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
