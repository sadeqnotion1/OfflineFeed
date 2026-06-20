#!/usr/bin/env python3
"""
apply_telegram_archive.py
=========================
Drop-in patcher that makes OfflineFeed's Archive behave like Telegram:

  1. Archive opens a LIST of the channels you've archived (a folder),
     instead of acting like a single channel.
  2. The Archive entry sits ON TOP of "Saved Messages".
  3. A more Telegram-like archive icon (box + down arrow) + a back arrow.

What it changes (additive, minimal):
  * frontend/bridge.py                       (anchored edits)
  * frontend/qml/components/ChatList.qml      (anchored edits)
  * frontend/qml/components/ChatContextMenu.qml (anchored edit)
  * frontend/qml/assets/icons/archive.svg     (replaced with Telegram-style)
  * frontend/qml/assets/icons/back.svg        (new file)

Safety:
  * STEP 1 makes a timestamped full-repo backup ZIP in the PARENT folder.
  * Edits are idempotent: re-running detects already-applied changes and skips.
  * If any anchor can't be found, NOTHING is written and the run aborts so you
    are never left in a half-patched state.
  * Handles both LF and CRLF line endings.

Usage (from the OfflineFeed repo root):
    python apply_telegram_archive.py
"""
from __future__ import annotations

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BRIDGE = ROOT / "frontend" / "bridge.py"
CHATLIST = ROOT / "frontend" / "qml" / "components" / "ChatList.qml"
CTXMENU = ROOT / "frontend" / "qml" / "components" / "ChatContextMenu.qml"
ICON_DIR = ROOT / "frontend" / "qml" / "assets" / "icons"
ARCHIVE_SVG = ICON_DIR / "archive.svg"
BACK_SVG = ICON_DIR / "back.svg"


# --------------------------------------------------------------------------- #
#  New / replacement icon art (recoloured at runtime via ColorOverlay)
# --------------------------------------------------------------------------- #
ARCHIVE_SVG_CONTENT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
    'viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="5" rx="1.5"/>'
    '<path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8"/>'
    '<path d="M9.5 12.5l2.5 2.5 2.5-2.5"/>'
    '<line x1="12" y1="15" x2="12" y2="11"/>'
    '</svg>\n'
)

BACK_SVG_CONTENT = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
    'viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="19" y1="12" x2="5" y2="12"/>'
    '<polyline points="12 19 5 12 12 5"/>'
    '</svg>\n'
)


# --------------------------------------------------------------------------- #
#  Anchored edits.  Each edit: (label, old, new)
#  Rule: if `new` is already present -> skip; elif `old` present once -> replace;
#  else -> abort (anchor not found).
# --------------------------------------------------------------------------- #

BRIDGE_EDITS = [
    (
        "bridge: signal",
        r'''    customFoldersChanged = Signal()            # item 7: user-defined folders''',
        r'''    customFoldersChanged = Signal()            # item 7: user-defined folders
    archiveOpenChanged = Signal(bool)          # Telegram-style Archive folder open/closed''',
    ),
    (
        "bridge: init state",
        r'''        self._read_unread: set = set()
        self._hidden: set = set()  # archived / deleted channels''',
        r'''        self._read_unread: set = set()
        self._hidden: set = set()  # archived / deleted channels
        # Telegram-style Archive folder: the channels the user has archived.
        # Stored separately from _hidden (delete) and persisted across restarts.
        _arch = self._ui_settings.setdefault("archive", {})
        self._archived_channels: set = set(_arch.get("channels", []) or [])
        self._archive_open: bool = False''',
    ),
    (
        "bridge: property + slots",
        r'''    newsRefreshing = Property(bool, _get_news_refreshing, notify=newsRefreshingChanged)''',
        r'''    newsRefreshing = Property(bool, _get_news_refreshing, notify=newsRefreshingChanged)

    # ----- Telegram-style Archive folder (open = showing archived channels) -----
    def _get_archive_open(self):
        return self._archive_open

    archiveOpen = Property(bool, _get_archive_open, notify=archiveOpenChanged)

    @Slot()
    def openArchive(self):
        if not self._archive_open:
            self._archive_open = True
            self.archiveOpenChanged.emit(True)
        self._rebuild_chat_list()

    @Slot()
    def closeArchive(self):
        if self._archive_open:
            self._archive_open = False
            self.archiveOpenChanged.emit(False)
        self._rebuild_chat_list()

    def _save_archive(self):
        grp = self._ui_settings.setdefault("archive", {})
        grp["channels"] = list(self._archived_channels)
        self._save_ui_settings(self._ui_settings)''',
    ),
    (
        "bridge: close archive on tab switch",
        r'''    def _set_tab(self, value):
        if value != self._active_tab:
            self._active_tab = value
            self.activeTabChanged.emit(value)
            if value not in ("settings",):
                self._rebuild_chat_list()''',
        r'''    def _set_tab(self, value):
        if value != self._active_tab:
            self._active_tab = value
            self.activeTabChanged.emit(value)
            if self._archive_open:
                self._archive_open = False
                self.archiveOpenChanged.emit(False)
            if value not in ("settings",):
                self._rebuild_chat_list()''',
    ),
    (
        "bridge: archiveChat toggle + persist",
        r'''    @Slot(str)
    def archiveChat(self, channel_id):
        self._hidden.add(channel_id)
        if channel_id == self._current_channel_id:
            self._current_channel_id = ""
            self.currentChannelIdChanged.emit("")
            self._message_model.set_items([])
        self._rebuild_chat_list()
        self.toastMessage.emit("ok", "Channel archived")''',
        r'''    @Slot(str)
    def archiveChat(self, channel_id):
        # Telegram-style: toggle a channel in/out of the Archive folder.
        if not channel_id or channel_id in (
            SPECIAL_SAVED, SPECIAL_ARCHIVED, SPECIAL_SEARCH, SPECIAL_LOGS, SPECIAL_BIN
        ):
            return
        if channel_id in self._archived_channels:
            self._archived_channels.discard(channel_id)
            self._save_archive()
            self._rebuild_chat_list()
            self.toastMessage.emit("ok", "Unarchived")
            return
        self._archived_channels.add(channel_id)
        if channel_id == self._current_channel_id:
            self._current_channel_id = ""
            self.currentChannelIdChanged.emit("")
            self._message_model.set_items([])
        self._save_archive()
        self._rebuild_chat_list()
        self.toastMessage.emit("ok", "Archived")''',
    ),
    (
        "bridge: archive-folder branch in _rebuild_chat_list",
        r'''    def _rebuild_chat_list(self):
        rows: List[Dict[str, Any]] = []

        if self._search:''',
        r'''    def _rebuild_chat_list(self):
        rows: List[Dict[str, Any]] = []

        if self._archive_open:
            # Telegram-style Archive folder: a LIST of the channels the user has
            # archived (not a single merged channel). Selecting one opens it.
            arch_rows = []
            for cid in self._channels():
                if cid not in self._archived_channels:
                    continue
                if not self._matches_search(cid):
                    continue
                arts = self._articles_for_channel(cid)
                last = arts[0] if arts else {}
                unread = 0 if cid in self._read_unread else (_hash_code(cid) % 9)
                arch_rows.append({
                    "channelId": cid,
                    "name": cid,
                    "lastMessage": last.get("title", ""),
                    "time": self._short_time(last.get("published") or last.get("timestamp", "")),
                    "unread": unread,
                    "avatarPath": self._avatar_for(cid),
                    "section": self._section_of(cid),
                    "muted": cid in self._muted,
                    "pinned": cid in self._pinned,
                    "matchCount": 0
                })
            arch_rows.sort(key=lambda r: 0 if r.get("pinned") else 1)
            rows.extend(arch_rows)
            self._chat_model.set_items(rows)
            return

        if self._search:''',
    ),
    (
        "bridge: reorder Archive above Saved",
        r'''        else:
            if self._matches_search("Saved Messages"):
                rows.append(self._special_row(SPECIAL_SAVED, "Saved Messages", "bookmark"))
            if self._matches_search("Archived Messages"):
                rows.append(self._special_row(SPECIAL_ARCHIVED, "Archived Messages", "archive"))
            if self._binned_items and self._matches_search("Bin"):
                rows.append(self._special_row(SPECIAL_BIN, "Bin", "trash"))''',
        r'''        else:
            if self._matches_search("Archived chats"):
                rows.append(self._special_row(SPECIAL_ARCHIVED, "Archived chats", "archive"))
            if self._matches_search("Saved Messages"):
                rows.append(self._special_row(SPECIAL_SAVED, "Saved Messages", "bookmark"))
            if self._binned_items and self._matches_search("Bin"):
                rows.append(self._special_row(SPECIAL_BIN, "Bin", "trash"))''',
    ),
    (
        "bridge: hide archived channels from main list",
        r'''            chan_rows = []
            for cid in self._channels():
                if cid in self._hidden:
                    continue
                if not self._passes_active_filter(cid):
                    continue''',
        r'''            chan_rows = []
            for cid in self._channels():
                if cid in self._hidden:
                    continue
                if cid in self._archived_channels:
                    continue
                if not self._passes_active_filter(cid):
                    continue''',
    ),
]

CHATLIST_EDITS = [
    (
        "ChatList: list height accounts for archive header",
        r'''            width: parent.width
            height: parent.height - Theme.searchBarHeight   // fill below the search header''',
        r'''            width: parent.width
            height: parent.height - Theme.searchBarHeight - (bridge.archiveOpen ? Theme.searchBarHeight : 0)   // fill below the search header (+ archive header when open)''',
    ),
    (
        "ChatList: archive header bar",
        r'''    Column {
        anchors.fill: parent
        spacing: 0

        // ---- Search bar ----''',
        r'''    Column {
        anchors.fill: parent
        spacing: 0

        // ---- Archive header (Telegram-style "Archived chats" + back arrow) ----
        Rectangle {
            width: parent.width
            height: bridge.archiveOpen ? Theme.searchBarHeight : 0
            visible: bridge.archiveOpen
            color: Theme.panel
            Row {
                anchors.fill: parent
                anchors.leftMargin: Theme.space.md
                anchors.rightMargin: Theme.space.md
                spacing: Theme.space.md
                LayoutMirroring.enabled: Theme.rtl
                Rectangle {
                    width: 30; height: 30; radius: 15
                    anchors.verticalCenter: parent.verticalCenter
                    color: backArea.containsMouse ? Theme.hover : "transparent"
                    Behavior on color { ColorAnimation { duration: Theme.anim } }
                    Icon {
                        anchors.centerIn: parent
                        name: "back"; size: 20; color: Theme.text
                    }
                    MouseArea {
                        id: backArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: bridge.closeArchive()
                    }
                }
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: qsTr("Archived chats")
                    color: Theme.text
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    font.bold: true
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.hairline }
        }

        // ---- Search bar ----''',
    ),
    (
        "ChatList: open archive folder on row click",
        r'''                onClicked: {
                    list.currentIndex = index
                    root.openChat(model.channelId)
                }''',
        r'''                onClicked: {
                    list.currentIndex = index
                    if (model.channelId === "ArchivedMessages")
                        bridge.openArchive()
                    else
                        root.openChat(model.channelId)
                }''',
    ),
    (
        "ChatList: keyboard open archive folder",
        r'''            Keys.onReturnPressed: if (list.currentItem) root.openChat(list.currentItem.channelId)
            Keys.onEnterPressed: if (list.currentItem) root.openChat(list.currentItem.channelId)''',
        r'''            Keys.onReturnPressed: if (list.currentItem) { if (list.currentItem.channelId === "ArchivedMessages") bridge.openArchive(); else root.openChat(list.currentItem.channelId) }
            Keys.onEnterPressed: if (list.currentItem) { if (list.currentItem.channelId === "ArchivedMessages") bridge.openArchive(); else root.openChat(list.currentItem.channelId) }''',
    ),
    (
        "ChatList: archive-aware empty state",
        r'''                visible: list.count === 0
                text: qsTr("No channels yet.\nRefresh feeds or add a source in Settings.")''',
        r'''                visible: list.count === 0
                text: bridge.archiveOpen
                      ? qsTr("No archived chats.\nRight-click any channel and choose Archive.")
                      : qsTr("No channels yet.\nRefresh feeds or add a source in Settings.")''',
    ),
]

CTXMENU_EDITS = [
    (
        "ChatContextMenu: Archive/Unarchive label",
        r'''text: qsTr("Archive");''',
        r'''text: bridge.archiveOpen ? qsTr("Unarchive") : qsTr("Archive");''',
    ),
]


# --------------------------------------------------------------------------- #
#  Engine
# --------------------------------------------------------------------------- #
def _read(path: Path):
    raw = path.read_text(encoding="utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def _write(path: Path, text: str, crlf: bool):
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_text(text, encoding="utf-8")


def plan_file(path: Path, edits):
    """Return (new_text, crlf, applied, skipped) or raise on a missing anchor."""
    text, crlf = _read(path)
    applied, skipped = [], []
    for label, old, new in edits:
        if new in text:
            skipped.append(label)
            continue
        cnt = text.count(old)
        if cnt == 0:
            raise RuntimeError(
                f"Anchor NOT found for '{label}' in {path.name}. "
                f"Nothing was written. Is the repo unmodified / on the same version?"
            )
        if cnt > 1:
            raise RuntimeError(
                f"Anchor for '{label}' matched {cnt} times in {path.name} (must be unique). "
                f"Nothing was written."
            )
        text = text.replace(old, new, 1)
        applied.append(label)
    return text, crlf, applied, skipped


def backup_repo() -> Path:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = ROOT.parent / f"OfflineFeed-backup-{ts}.zip"
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fn in filenames:
                fp = Path(dirpath) / fn
                if fp.suffix == ".zip":
                    continue
                zf.write(fp, fp.relative_to(ROOT))
    return dest


def main() -> int:
    print("OfflineFeed -> Telegram-style Archive folder patcher\n" + "=" * 52)

    missing = [p for p in (BRIDGE, CHATLIST, CTXMENU) if not p.exists()]
    if missing:
        print("ERROR: run this from the OfflineFeed repo root. Missing:")
        for p in missing:
            print("   -", p.relative_to(ROOT) if ROOT in p.parents else p)
        return 2

    # ----- STEP 1: backup -----
    try:
        bkp = backup_repo()
        print(f"[1/3] Backup created: {bkp}")
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: backup failed ({exc}). Aborting before any change.")
        return 3

    # ----- STEP 2: plan all edits (no writes yet) -----
    try:
        plans = [
            (BRIDGE, *plan_file(BRIDGE, BRIDGE_EDITS)),
            (CHATLIST, *plan_file(CHATLIST, CHATLIST_EDITS)),
            (CTXMENU, *plan_file(CTXMENU, CTXMENU_EDITS)),
        ]
    except Exception as exc:  # noqa: BLE001
        print(f"\nABORTED: {exc}")
        print("No files were modified. Your backup is intact.")
        return 4

    # ----- STEP 3: commit writes -----
    for path, new_text, crlf, applied, skipped in plans:
        _write(path, new_text, crlf)
        rel = path.relative_to(ROOT)
        print(f"[2/3] Patched {rel}: {len(applied)} applied, {len(skipped)} already-present")
        for s in skipped:
            print(f"        (skip) {s}")

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_SVG.write_text(ARCHIVE_SVG_CONTENT, encoding="utf-8")
    BACK_SVG.write_text(BACK_SVG_CONTENT, encoding="utf-8")
    print(f"[3/3] Wrote icons: {ARCHIVE_SVG.relative_to(ROOT)}, {BACK_SVG.relative_to(ROOT)}")

    print("\nDONE. Now run the app and verify:")
    print("   - Right-click a channel -> Archive (it leaves the main list).")
    print("   - 'Archived chats' sits ABOVE 'Saved Messages'.")
    print("   - Click it -> a LIST of archived channels with a back arrow.")
    print("   - Right-click inside -> Unarchive to send it back.")
    print("\nIf anything looks wrong, restore the backup ZIP from the parent folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
