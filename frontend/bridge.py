"""
bridge.py — the QObject + QAbstractListModel layer that exposes the existing
OfflineFeed Python backend (gui_server.py HTTP API on 127.0.0.1:8080) to QML.

Design notes
------------
* The backend is left completely UNCHANGED. We talk to it over its existing
  local HTTP API so nothing in the aggregation / Telegram-posting logic breaks.
* Two list models back the UI:
      ChatListModel  -> the left/middle channel list (incl. Saved Messages + System Logs)
      MessageModel   -> the right pane (articles of the selected channel)
* ChatBridge is the imperative surface QML calls into (slots) and observes
  (properties + signals).

Every network call is defensive: if the backend is unreachable the UI still
loads with empty models and surfaces a toast instead of crashing.
"""
from __future__ import annotations

import os
import sys
import json
import hashlib
import subprocess
import urllib.parse
import urllib.request
import unicodedata
import re
from typing import Any, Dict, List, Optional

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    Qt,
    QByteArray,
    Signal,
    Slot,
    Property,
    QThreadPool,
    QRunnable,
)

API_BASE = "http://127.0.0.1:8080"
HTTP_TIMEOUT = 20


# --------------------------------------------------------------------------- #
#  HTTP helpers (thin wrappers around the existing backend API)
# --------------------------------------------------------------------------- #
def _get(path: str) -> Any:
    url = API_BASE + path
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(path: str, payload: Optional[dict] = None) -> Any:
    url = API_BASE + path
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {}


def _hash_code(text: str) -> int:
    return int(hashlib.md5((text or "").encode("utf-8")).hexdigest(), 16)


class TaskSignals(QObject):
    finished = Signal(object)


class TaskResultReceiver(QObject):
    result_received = Signal(object)

    def __init__(self, on_done=None, parent=None):
        super().__init__(parent)
        self.on_done = on_done

    @Slot(object)
    def handle_result(self, result):
        if self.on_done:
            try:
                self.on_done(result)
            except Exception as exc:
                print(f"[Bridge DEBUG] Error in done callback: {exc}")
        self.result_received.emit(result)


class _Task(QRunnable):
    """Run a blocking backend call off the GUI thread."""

    def __init__(self, fn, parent=None):
        super().__init__()
        self._fn = fn
        self.signals = TaskSignals(parent)

    def run(self):
        try:
            result = self._fn()
        except Exception as exc:  # noqa: BLE001 - surfaced to UI as a toast
            result = exc
        try:
            self.signals.finished.emit(result)
        except RuntimeError as err:
            # Under PySide6, if the application is shutting down, the QObject (signals)
            # may already be deleted. Catching this avoids an uncaught exception traceback.
            if "deleted" not in str(err):
                raise


# --------------------------------------------------------------------------- #
#  Chat list model
# --------------------------------------------------------------------------- #
class ChatListModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    LastMessageRole = Qt.UserRole + 2
    TimeRole = Qt.UserRole + 3
    UnreadRole = Qt.UserRole + 4
    AvatarPathRole = Qt.UserRole + 5
    ChannelIdRole = Qt.UserRole + 6
    SectionRole = Qt.UserRole + 7
    MutedRole = Qt.UserRole + 8
    PinnedRole = Qt.UserRole + 9
    MatchCountRole = Qt.UserRole + 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: List[Dict[str, Any]] = []

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.LastMessageRole: b"lastMessage",
            self.TimeRole: b"time",
            self.UnreadRole: b"unread",
            self.AvatarPathRole: b"avatarPath",
            self.ChannelIdRole: b"channelId",
            self.SectionRole: b"section",
            self.MutedRole: b"muted",
            self.PinnedRole: b"pinned",
            self.MatchCountRole: b"matchCount",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        item = self._items[index.row()]
        mapping = {
            self.NameRole: "name",
            self.LastMessageRole: "lastMessage",
            self.TimeRole: "time",
            self.UnreadRole: "unread",
            self.AvatarPathRole: "avatarPath",
            self.ChannelIdRole: "channelId",
            self.SectionRole: "section",
            self.MutedRole: "muted",
            self.PinnedRole: "pinned",
            self.MatchCountRole: "matchCount",
        }
        return item.get(mapping.get(role, ""), "")

    def set_items(self, items: List[Dict[str, Any]]):
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def items(self) -> List[Dict[str, Any]]:
        return self._items


# --------------------------------------------------------------------------- #
#  Message model
# --------------------------------------------------------------------------- #
class MessageModel(QAbstractListModel):
    TitleRole = Qt.UserRole + 1     # 257 (used by ChatView pinned bar)
    TextRole = Qt.UserRole + 2
    UrlRole = Qt.UserRole + 3
    ThumbnailRole = Qt.UserRole + 4
    TimeRole = Qt.UserRole + 5
    OutgoingRole = Qt.UserRole + 6
    ReadRole = Qt.UserRole + 7
    ViewsRole = Qt.UserRole + 8
    ReactionsRole = Qt.UserRole + 9
    SourceRole = Qt.UserRole + 10
    TopicRole = Qt.UserRole + 11
    DayRole = Qt.UserRole + 12
    PinnedRole = Qt.UserRole + 13   # item 2: per-post pin flag

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: List[Dict[str, Any]] = []

    def roleNames(self):
        return {
            self.TitleRole: b"title",
            self.TextRole: b"text",
            self.UrlRole: b"url",
            self.ThumbnailRole: b"thumbnail",
            self.TimeRole: b"time",
            self.OutgoingRole: b"outgoing",
            self.ReadRole: b"read",
            self.ViewsRole: b"views",
            self.ReactionsRole: b"reactions",
            self.SourceRole: b"source",
            self.TopicRole: b"topic",
            self.DayRole: b"day",
            self.PinnedRole: b"pinned",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        item = self._items[index.row()]
        mapping = {
            self.TitleRole: "title",
            self.TextRole: "text",
            self.UrlRole: "url",
            self.ThumbnailRole: "thumbnail",
            self.TimeRole: "time",
            self.OutgoingRole: "outgoing",
            self.ReadRole: "read",
            self.ViewsRole: "views",
            self.ReactionsRole: "reactions",
            self.SourceRole: "source",
            self.TopicRole: "topic",
            self.DayRole: "day",
            self.PinnedRole: "pinned",
        }
        return item.get(mapping.get(role, ""), "")

    def set_items(self, items: List[Dict[str, Any]]):
        self.beginResetModel()
        self._items = items
        self.endResetModel()


# --------------------------------------------------------------------------- #
#  Custom-sources model (Settings page)
# --------------------------------------------------------------------------- #
class SourcesModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    UrlRole = Qt.UserRole + 2
    SectionRole = Qt.UserRole + 3
    CategoryRole = Qt.UserRole + 4
    AvatarPathRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: List[Dict[str, Any]] = []

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.UrlRole: b"url",
            self.SectionRole: b"section",
            self.CategoryRole: b"category",
            self.AvatarPathRole: b"avatarPath",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        item = self._items[index.row()]
        mapping = {
            self.NameRole: "name",
            self.UrlRole: "url",
            self.SectionRole: "section",
            self.CategoryRole: "category",
            self.AvatarPathRole: "avatarPath",
        }
        return item.get(mapping.get(role, ""), "")

    def set_items(self, items: List[Dict[str, Any]]):
        self.beginResetModel()
        self._items = items
        self.endResetModel()


# --------------------------------------------------------------------------- #
#  Search Results model
# --------------------------------------------------------------------------- #
class SearchResultsModel(QAbstractListModel):
    TitleRole = Qt.UserRole + 1
    SnippetRole = Qt.UserRole + 2
    UrlRole = Qt.UserRole + 3
    SourceRole = Qt.UserRole + 4
    SectionRole = Qt.UserRole + 5
    TimeRole = Qt.UserRole + 6
    ThumbnailRole = Qt.UserRole + 7

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: List[Dict[str, Any]] = []

    def roleNames(self):
        return {
            self.TitleRole: b"title",
            self.SnippetRole: b"snippet",
            self.UrlRole: b"url",
            self.SourceRole: b"source",
            self.SectionRole: b"section",
            self.TimeRole: b"time",
            self.ThumbnailRole: b"thumbnail",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        item = self._items[index.row()]
        mapping = {
            self.TitleRole: "title",
            self.SnippetRole: "snippet",
            self.UrlRole: "url",
            self.SourceRole: "source",
            self.SectionRole: "section",
            self.TimeRole: "time",
            self.ThumbnailRole: "thumbnail",
        }
        return item.get(mapping.get(role, ""), "")

    def set_items(self, items: List[Dict[str, Any]]):
        self.beginResetModel()
        self._items = items
        self.endResetModel()


# --------------------------------------------------------------------------- #
#  Bridge
# --------------------------------------------------------------------------- #
SPECIAL_SAVED = "SavedMessages"
SPECIAL_ARCHIVED = "ArchivedMessages"
SPECIAL_SEARCH = "SearchResults"
SPECIAL_LOGS = "SystemLogs"
SPECIAL_BIN = "BinMessages"          # NEW: recoverable deleted posts
REACTION_EMOJIS = ["\U0001F44D", "\u2764\ufe0f", "\U0001F525", "\U0001F389", "\U0001F44F"]


def strip_diacritics(text):
    if not text:
        return ""
    try:
        normalized = unicodedata.normalize('NFKD', text)
        return "".join(c for c in normalized if not unicodedata.combining(c))
    except Exception:
        return text


def highlight_text(text, query_terms):
    if not text or not query_terms:
        return text or ""
    # Filter out empty terms
    terms = [t for t in query_terms if t]
    if not terms:
        return text
    # Sort terms by length descending to match longer terms first
    sorted_terms = sorted(terms, key=len, reverse=True)
    # Build single-pass pattern
    pattern = re.compile("(" + "|".join(re.escape(t) for t in sorted_terms) + ")", re.IGNORECASE)
    return pattern.sub(r"<b><font color='#2f8ad6'>\1</font></b>", text)


class ChatBridge(QObject):
    # ----- signals -----
    themeChanged = Signal(str)
    rtlChanged = Signal(bool)
    activeTabChanged = Signal(str)
    currentChannelIdChanged = Signal(str)
    currentChannelNameChanged = Signal(str)
    searchQueryChanged = Signal(str)
    logsUpdated = Signal()
    customSourcesUpdated = Signal()
    telegramConfigChanged = Signal()
    fontFamilyChanged = Signal(str)
    accentOverrideChanged = Signal(str)
    wallpaperModeChanged = Signal(str)
    interfaceScaleChanged = Signal(float)
    articleBlocksLoaded = Signal(str, "QVariant")
    toastMessage = Signal(str, str)  # (kind, message)
    newsRefreshingChanged = Signal(bool)  # True while a feed refresh is in flight
    readerFontFamilyChanged = Signal(str)      # item 1: independent reader font
    wallpaperImageChanged = Signal(str)        # item 8: custom wallpaper image path
    currentChannelAvatarChanged = Signal(str)  # item 5: open-channel header avatar
    pinnedPostsChanged = Signal()              # item 2: pinned posts in open channel
    customFoldersChanged = Signal()            # item 7: user-defined folders

    def __init__(self, chat_model: ChatListModel, message_model: MessageModel,
                 sources_model: SourcesModel, search_results_model: Optional[SearchResultsModel] = None, parent=None, system_fonts=None):
        super().__init__(parent)
        self._chat_model = chat_model
        self._message_model = message_model
        self._sources_model = sources_model
        # All installed system font families (computed once in app.py and
        # passed in). Exposed read-only to QML as `bridge.systemFonts`.
        self._system_fonts = list(system_fonts) if system_fonts else []
        self._search_results_model = search_results_model
        self._pool = QThreadPool.globalInstance()
        self._active_tasks = set()

        # Load and merge settings
        self._ui_settings = self._load_ui_settings()

        self._theme = self._ui_settings["appearance"]["theme"]
        self._rtl = self._ui_settings["language"]["rtl"]
        self._fontFamily = self._ui_settings["appearance"]["font_family"]
        self._accentOverride = self._ui_settings["appearance"]["accent_override"]
        self._wallpaperMode = self._ui_settings["appearance"]["wallpaper_mode"]
        self._interfaceScale = float(self._ui_settings["appearance"]["interface_scale"])
        # Item 1: offline-reader font stored separately from the chat/UI font so
        # changing one never affects the other. Falls back to the chat font.
        self._readerFontFamily = self._ui_settings["appearance"].get(
            "reader_font_family", self._fontFamily)
        # Item 8: optional custom wallpaper image (stored as a file URI).
        self._wallpaperImage = self._ui_settings["appearance"].get("wallpaper_image", "")
        self._active_tab = "entertainment"
        self._current_channel_id = ""
        self._current_channel_name = ""
        self._current_channel_avatar = ""            # item 5
        self._current_pinned_posts: List[Dict[str, Any]] = []  # item 2
        self._search = ""

        self._articles: List[Dict[str, Any]] = []
        self._saved_articles: List[Dict[str, Any]] = []
        self._archived_articles: List[Dict[str, Any]] = []
        self._custom_sources: List[Dict[str, Any]] = []
        self._activity_log: List[Dict[str, Any]] = []
        self._muted: set = set()
        # Item 2: pinned channels + pinned posts persist across restarts.
        _pins = self._ui_settings.setdefault("pins", {})
        self._pinned: set = {SPECIAL_SAVED, SPECIAL_ARCHIVED} | set(_pins.get("channels", []) or [])
        self._pinned_messages: set = set(_pins.get("messages", []) or [])
        # Item 7: user-defined folders that combine multiple channels.
        self._custom_folders: list = list((self._ui_settings.setdefault("folders", {}) or {}).get("custom", []) or [])
        self._read_unread: set = set()
        self._hidden: set = set()  # archived / deleted channels
        self._msg_search: str = ""  # in-channel message search
        self._news_refreshing = False  # backs the newsRefreshing property

        # ---- Bin: recoverable deleted posts (task 3 + task 4) ----
        # Full article dicts are kept locally so a deleted post survives feed
        # refresh and stays readable even after it leaves the source feed.
        _bin = self._ui_settings.setdefault("bin", {})
        self._binned_items: List[Dict[str, Any]] = list(_bin.get("items", []) or [])
        self._binned_keys: set = {self._article_key(a) for a in self._binned_items}

        self._rebuild_chat_list()
        self.refreshNews(False)

    # ===================== properties =====================
    def _get_theme(self):
        return self._theme

    def _set_theme(self, value):
        if value == "dark":
            value = "night"
        elif value == "light":
            value = "day"
        if value != self._theme:
            self._theme = value
            self.themeChanged.emit(value)
            self._ui_settings["appearance"]["theme"] = value
            self._save_ui_settings(self._ui_settings)

    theme = Property(str, _get_theme, _set_theme, notify=themeChanged)

    def _get_rtl(self):
        return self._rtl

    def _set_rtl(self, value):
        if value != self._rtl:
            self._rtl = value
            self.rtlChanged.emit(value)
            self._ui_settings["language"]["rtl"] = value
            self._save_ui_settings(self._ui_settings)

    rtl = Property(bool, _get_rtl, _set_rtl, notify=rtlChanged)

    def _get_font_family(self):
        return self._fontFamily

    def _set_font_family(self, value):
        if value != self._fontFamily:
            self._fontFamily = value
            self.fontFamilyChanged.emit(value)
            self._ui_settings["appearance"]["font_family"] = value
            self._save_ui_settings(self._ui_settings)

    fontFamily = Property(str, _get_font_family, _set_font_family, notify=fontFamilyChanged)

    def _get_accent_override(self):
        return self._accentOverride

    def _set_accent_override(self, value):
        if value != self._accentOverride:
            self._accentOverride = value
            self.accentOverrideChanged.emit(value)
            self._ui_settings["appearance"]["accent_override"] = value
            self._save_ui_settings(self._ui_settings)

    accentOverride = Property(str, _get_accent_override, _set_accent_override, notify=accentOverrideChanged)

    def _get_wallpaper_mode(self):
        return self._wallpaperMode

    def _set_wallpaper_mode(self, value):
        if value != self._wallpaperMode:
            self._wallpaperMode = value
            self.wallpaperModeChanged.emit(value)
            self._ui_settings["appearance"]["wallpaper_mode"] = value
            self._save_ui_settings(self._ui_settings)

    wallpaperMode = Property(str, _get_wallpaper_mode, _set_wallpaper_mode, notify=wallpaperModeChanged)

    def _get_interface_scale(self):
        return self._interfaceScale

    def _set_interface_scale(self, value):
        try:
            val_float = float(value)
        except Exception:
            val_float = 1.0
        if abs(val_float - self._interfaceScale) > 1e-5:
            self._interfaceScale = val_float
            self.interfaceScaleChanged.emit(val_float)
            self._ui_settings["appearance"]["interface_scale"] = val_float
            self._save_ui_settings(self._ui_settings)

    interfaceScale = Property(float, _get_interface_scale, _set_interface_scale, notify=interfaceScaleChanged)

    # ----- Item 1: offline-reader font (independent of the chat/UI font) -----
    def _get_reader_font_family(self):
        return self._readerFontFamily

    def _set_reader_font_family(self, value):
        if value and value != self._readerFontFamily:
            self._readerFontFamily = value
            self.readerFontFamilyChanged.emit(value)
            self._ui_settings["appearance"]["reader_font_family"] = value
            self._save_ui_settings(self._ui_settings)

    readerFontFamily = Property(str, _get_reader_font_family, _set_reader_font_family, notify=readerFontFamilyChanged)

    # ----- Item 8: custom chat wallpaper image (file URI) -----
    def _get_wallpaper_image(self):
        return self._wallpaperImage

    def _set_wallpaper_image(self, value):
        if value != self._wallpaperImage:
            self._wallpaperImage = value
            self.wallpaperImageChanged.emit(value)
            self._ui_settings["appearance"]["wallpaper_image"] = value
            self._save_ui_settings(self._ui_settings)

    wallpaperImage = Property(str, _get_wallpaper_image, _set_wallpaper_image, notify=wallpaperImageChanged)

    # ----- Item 5: avatar for the currently open channel (header) -----
    def _get_current_channel_avatar(self):
        return self._current_channel_avatar

    currentChannelAvatar = Property(str, _get_current_channel_avatar, notify=currentChannelAvatarChanged)

    def _get_tab(self):
        return self._active_tab

    def _set_tab(self, value):
        if value != self._active_tab:
            self._active_tab = value
            self.activeTabChanged.emit(value)
            if value not in ("settings",):
                self._rebuild_chat_list()

    activeTab = Property(str, _get_tab, _set_tab, notify=activeTabChanged)

    def _get_cid(self):
        return self._current_channel_id

    currentChannelId = Property(str, _get_cid, notify=currentChannelIdChanged)

    def _get_cname(self):
        return self._current_channel_name

    currentChannelName = Property(str, _get_cname, notify=currentChannelNameChanged)

    def _get_search(self):
        return self._search

    searchQuery = Property(str, _get_search, notify=searchQueryChanged)

    def _get_system_fonts(self):
        return self._system_fonts

    # Read-only list of every installed system font family (see app.py).
    systemFonts = Property("QStringList", _get_system_fonts, constant=True)

    def _get_news_refreshing(self):
        return self._news_refreshing

    newsRefreshing = Property(bool, _get_news_refreshing, notify=newsRefreshingChanged)

    # ===================== slots: navigation =====================
    @Slot(str)
    def setTheme(self, value):
        self._set_theme(value)

    @Slot(str)
    def setTab(self, value):
        self._set_tab(value)

    @Slot(bool)
    def setRtl(self, value):
        self._set_rtl(value)

    # ===================== Settings system (additive) =====================
    # Generic key/value access for the master->detail Settings UI. Values are
    # persisted through the EXISTING UI-settings store (self._ui_settings +
    # self._save_ui_settings), so they survive restart just like theme/rtl.
    settingsChanged = Signal(str)  # emitted with the group name after a write

    @Slot(str, result="QVariant")
    def settingsGetGroup(self, group):
        """Return the persisted dict for a settings group (creating it empty if
        missing). Never raises."""
        try:
            g = self._ui_settings.setdefault(group, {})
            if not isinstance(g, dict):
                g = {}
                self._ui_settings[group] = g
            return dict(g)
        except Exception as exc:  # noqa: BLE001
            print(f"[Bridge] settingsGetGroup({group!r}) failed: {exc}")
            return {}

    @Slot(str, str, "QVariant")
    def settingsSetValue(self, group, key, value):
        """Persist a single value into a settings group and save to disk."""
        try:
            g = self._ui_settings.setdefault(group, {})
            if not isinstance(g, dict):
                g = {}
                self._ui_settings[group] = g
            g[key] = value
            self._save_ui_settings(self._ui_settings)
            self.settingsChanged.emit(group)
        except Exception as exc:  # noqa: BLE001
            print(f"[Bridge] settingsSetValue({group!r}, {key!r}) failed: {exc}")
            try:
                self.toastMessage.emit("error", "Could not save setting")
            except Exception:
                pass

    @Slot(result="QVariant")
    def settingsGetTelegram(self):
        """Read the Telegram repost config from the existing backend API
        (GET /api/telegram/config). Returns {} if the backend is unreachable."""
        try:
            cfg = _get("/api/telegram/config")
            return cfg if isinstance(cfg, dict) else {}
        except Exception as exc:  # noqa: BLE001
            print(f"[Bridge] settingsGetTelegram failed: {exc}")
            try:
                self.toastMessage.emit("error", "Backend offline: can't load Telegram config")
            except Exception:
                pass
            return {}

    @Slot("QVariant", result=bool)
    def settingsSaveTelegram(self, cfg):
        """Persist Telegram repost config through the existing backend API
        (POST /api/telegram/config). Returns True on success."""
        try:
            payload = dict(cfg) if cfg else {}
        except Exception:
            payload = {}
        try:
            _post("/api/telegram/config", payload)
            try:
                self.telegramConfigChanged.emit()
            except Exception:
                pass
            try:
                self.toastMessage.emit("ok", "Telegram settings saved")
            except Exception:
                pass
            return True
        except Exception as exc:  # noqa: BLE001
            print(f"[Bridge] settingsSaveTelegram failed: {exc}")
            try:
                self.toastMessage.emit("error", "Could not save Telegram settings")
            except Exception:
                pass
            return False
    # =================== end Settings system (additive) ===================

    def _searchable_text_for_article(self, a) -> str:
        title = a.get("title") or ""
        desc = a.get("description") or a.get("text") or ""
        source = a.get("source") or ""
        category = a.get("category") or a.get("topic") or ""
        combined = f"{title} {desc} {source} {category}"
        return strip_diacritics(combined).lower()

    def _match_article(self, a, query_terms) -> bool:
        if not query_terms:
            return True
        text = self._searchable_text_for_article(a)
        return all(term in text for term in query_terms)

    def _is_same_article(self, a1, a2) -> bool:
        url1 = a1.get("url")
        url2 = a2.get("url")
        if url1 and url2:
            return url1.strip() == url2.strip()
        return (a1.get("title") or "").strip() == (a2.get("title") or "").strip()

    def _score_article(self, a, query_terms) -> int:
        title = strip_diacritics(a.get("title") or "").lower()
        source = strip_diacritics(a.get("source") or "").lower()
        body = strip_diacritics(a.get("description") or a.get("text") or "").lower()
        category = strip_diacritics(a.get("category") or a.get("topic") or "").lower()
        
        score = 0
        for term in query_terms:
            if term in title:
                score += 100
            elif term in source:
                score += 50
            elif term in body:
                score += 10
            elif term in category:
                score += 5
        return score

    def _get_article_timestamp(self, a) -> float:
        ts = a.get("timestamp")
        if isinstance(ts, (int, float)):
            return float(ts)
        pub = a.get("published")
        if pub:
            try:
                import dateutil.parser
                return dateutil.parser.parse(str(pub)).timestamp()
            except Exception:
                digits = "".join(c for c in str(pub) if c.isdigit())
                if digits:
                    try:
                        return float(digits[:14])
                    except Exception:
                        pass
        return 0.0

    @Slot(str)
    def setSearch(self, query):
        self._search = query or ""
        self.searchQueryChanged.emit(self._search)
        
        if self._search_results_model:
            if self._search:
                query_normalized = strip_diacritics(self._search).lower()
                query_terms = [t for t in query_normalized.split() if t]
                
                matching_posts = []
                # Search across all channels: normal articles, saved, archived
                for a in self._articles:
                    if self._article_key(a) in self._binned_keys:
                        continue
                    if self._match_article(a, query_terms):
                        matching_posts.append(a)
                for a in self._saved_articles:
                    if self._article_key(a) in self._binned_keys:
                        continue
                    if self._match_article(a, query_terms):
                        if not any(self._is_same_article(a, m) for m in matching_posts):
                            matching_posts.append(a)
                for a in self._archived_articles:
                    if self._article_key(a) in self._binned_keys:
                        continue
                    if self._match_article(a, query_terms):
                        if not any(self._is_same_article(a, m) for m in matching_posts):
                            matching_posts.append(a)
                            
                scored_posts = []
                for a in matching_posts:
                    score = self._score_article(a, query_terms)
                    timestamp = self._get_article_timestamp(a)
                    scored_posts.append((score, timestamp, a))
                
                scored_posts.sort(key=lambda x: (x[0], x[1]), reverse=True)
                
                items = []
                for score, ts, a in scored_posts:
                    title_raw = a.get("title") or ""
                    desc_raw = a.get("description") or a.get("text") or ""
                    
                    title_hl = highlight_text(title_raw, query_terms)
                    snippet_hl = highlight_text(desc_raw[:180] + ("..." if len(desc_raw) > 180 else ""), query_terms)
                    
                    items.append({
                        "title": title_hl,
                        "snippet": snippet_hl,
                        "url": a.get("url") or "",
                        "source": a.get("source") or a.get("category") or "Feed",
                        "section": a.get("section") or "Entertainment",
                        "time": self._short_time(a.get("published") or a.get("timestamp") or ""),
                        "thumbnail": a.get("thumbnail") or "",
                    })
                self._search_results_model.set_items(items)
            else:
                self._search_results_model.set_items([])
                
        self._rebuild_chat_list()

    @Slot(str)
    def setChannelSearch(self, query):
        """Filter the messages of the currently open channel."""
        self._msg_search = query or ""
        if self._current_channel_id:
            self._rebuild_messages(self._current_channel_id)

    @Slot(result="QVariant")
    def getActivityLog(self):
        return list(self._activity_log)

    @Slot(str)
    def openChat(self, channel_id):
        self._msg_search = ""
        self._current_channel_id = channel_id
        self._current_channel_name = self._name_for_channel(channel_id)
        self._current_channel_avatar = self._header_avatar_for(channel_id)
        self._read_unread.add(channel_id)
        self.currentChannelIdChanged.emit(channel_id)
        self.currentChannelNameChanged.emit(self._current_channel_name)
        self.currentChannelAvatarChanged.emit(self._current_channel_avatar)
        self._rebuild_messages(channel_id)
        self._rebuild_chat_list()

    # ===================== slots: data loading =====================
    @Slot(bool)
    def refreshNews(self, force):
        # Debounce: ignore taps while a refresh is already running.
        if self._news_refreshing:
            return
        self._news_refreshing = True
        self.newsRefreshingChanged.emit(True)

        def work():
            return _get("/api/news" + ("?refresh=true" if force else ""))

        def done(result):
            # Always clear the loading state first, on success or failure.
            self._news_refreshing = False
            self.newsRefreshingChanged.emit(False)
            if isinstance(result, Exception):
                print("[Bridge DEBUG] refreshNews failed with exception:", result)
                self.toastMessage.emit("error", "Backend not reachable yet…")
                return
            print("[Bridge DEBUG] refreshNews finished successfully. Articles count:", len(result.get("articles", []) or []))
            self._articles = result.get("articles", []) or []
            self._custom_sources = result.get("custom_sources", []) or []
            self._saved_articles = result.get("saved_articles", []) or []
            self._archived_articles = result.get("archived_articles", []) or []
            self._refresh_sources_model()
            self._rebuild_chat_list()
            if self._current_channel_id:
                self._rebuild_messages(self._current_channel_id)
            self.customSourcesUpdated.emit()
            if force:
                self.toastMessage.emit("ok", "Feeds refreshed")

        self._run(work, done)

    @Slot()
    def loadLogs(self):
        def work():
            return _get("/api/activity_log")

        def done(result):
            if isinstance(result, Exception):
                # Backend is down - fall back to the local debug log so the
                # System Logs panel still shows missing packages / crashes.
                try:
                    import debug as _dbg
                    local = _dbg.recent_logs()
                    if local:
                        self._activity_log = local
                        self.logsUpdated.emit()
                except Exception:
                    pass
                return
            self._activity_log = result or []
            self.logsUpdated.emit()
            if self._current_channel_id == SPECIAL_LOGS:
                self._rebuild_messages(SPECIAL_LOGS)

        self._run(work, done)

    @Slot(str)
    def openArticle(self, url):
        """Fetch offline reader content (with images) for an article."""
        if not url:
            return

        def work():
            return _get("/api/news/article?url=" + urllib.parse.quote(url, safe=""))

        def done(result):
            if isinstance(result, Exception):
                # Still emit so the reader leaves its loading state and can show
                # the in-app fallback text instead of spinning forever.
                self.articleBlocksLoaded.emit(url, {"error": "Could not load this article offline."})
                return
            self.articleBlocksLoaded.emit(url, result)

        self._run(work, done)

    @Slot(str)
    def fetchArticleContent(self, url):  # backwards-compatible alias
        self.openArticle(url)

    @Slot(str)
    def copyLink(self, url):
        """Copy an article link to the system clipboard."""
        if not url:
            return
        try:
            from PySide6.QtGui import QGuiApplication
            cb = QGuiApplication.clipboard()
            if cb is not None:
                cb.setText(url)
            self.toastMessage.emit("ok", "Link copied")
        except Exception:  # noqa: BLE001
            self.toastMessage.emit("error", "Could not copy link")

    @Slot(str)
    def openExternal(self, url):
        # Use an OS-level opener so it still works even though app.py disables
        # webbrowser.open (to stop the backend auto-launching the old web UI).
        if not url:
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(url)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", url])
            else:
                subprocess.Popen(["xdg-open", url])
        except Exception:  # noqa: BLE001
            pass

    @Slot(str)
    @Slot(str, str)
    def openInOfflineViewer(self, url, title=""):
        """Open ONE article in the existing web offline viewer.

        Reuses the offline_viewer page already served by gui_server.py and its
        existing window.openOfflineReader(url, title) entry point via a
        ?reader= deep link. No new backend route is introduced.
        """
        if not url:
            return
        target = API_BASE + "/?reader=" + urllib.parse.quote(url, safe="")
        if title:
            target += "&title=" + urllib.parse.quote(title, safe="")
        try:
            if sys.platform.startswith("win"):
                os.startfile(target)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
            self.toastMessage.emit("ok", "Opening in offline viewer…")
        except Exception:  # noqa: BLE001
            self.toastMessage.emit("error", "Could not open offline viewer")

    # ===================== slots: forwarding =====================
    @Slot(str, str)
    def saveArticle(self, url, title):
        art = None
        for a in self._articles:
            if url and a.get("url") == url:
                art = a
                break
        if not art:
            for a in self._articles:
                if a.get("title") == title:
                    art = a
                    break
        if not art:
            for a in self._archived_articles:
                if url and a.get("url") == url:
                    art = a
                    break
                if a.get("title") == title:
                    art = a
                    break
        if not art:
            art = {
                "title": title,
                "description": "",
                "url": url,
                "thumbnail": "",
                "category": "",
                "section": "Entertainment"
            }
            
        payload = self._to_send_article(art)
        
        def work():
            return _post("/api/news/saved/add", payload)
            
        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Could not save article")
            else:
                status = result.get("status")
                msg = result.get("message", "Article saved")
                self._saved_articles = result.get("saved_articles", [])
                if status == "already_saved":
                    self.toastMessage.emit("info", msg)
                else:
                    self.toastMessage.emit("ok", msg)
                if self._current_channel_id == SPECIAL_SAVED:
                    self._rebuild_messages(SPECIAL_SAVED)
                self._rebuild_chat_list()
        self._run(work, done)

    @Slot(str, str)
    def unsaveArticle(self, url, title):
        def work():
            return _post("/api/news/saved/remove", {"url": url, "title": title, "key": url or title})
            
        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Could not remove article")
            else:
                msg = result.get("message", "Removed from Saved Messages")
                self._saved_articles = result.get("saved_articles", [])
                self.toastMessage.emit("ok", msg)
                if self._current_channel_id == SPECIAL_SAVED:
                    self._rebuild_messages(SPECIAL_SAVED)
                self._rebuild_chat_list()
        self._run(work, done)

    @Slot(str)
    def forwardToSaved(self, title):
        url = ""
        for a in self._articles:
            if a.get("title") == title:
                url = a.get("url", "")
                break
        self.saveArticle(url, title)

    @Slot()
    def forwardAllToTelegram(self):
        cid = self._current_channel_id
        if cid:
            self.sendChannelToTelegram(cid)

    @Slot(str)
    def sendChannelToTelegram(self, channel_id):
        name = self._name_for_channel(channel_id)
        articles = self._articles_for_channel(channel_id)
        payload = {
            "channel_name": name,
            "articles": [self._to_send_article(a) for a in articles],
        }

        def work():
            return _post("/api/telegram/send_channel", payload)

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Telegram send failed")
                return
            sent = result.get("sent_count", 0)
            skipped = result.get("already_sent_count", 0)
            self.toastMessage.emit("ok", f"Sent {sent}, skipped {skipped}")
            self.loadLogs()

        self._run(work, done)

    @Slot(str, int)
    def toggleReaction(self, url, index):
        # Reactions are presentation-only in the backend; refresh the row.
        if self._current_channel_id:
            self._rebuild_messages(self._current_channel_id)

    # ===================== slots: source management =====================
    @Slot(str, str, str, str)
    @Slot(str, str, str, str, str)
    def addCustomSource(self, name, feed_url, section, category, avatar_base64=""):
        payload = {
            "name": name,
            "feed_url": feed_url,
            "section": section or "entertainment",
            "category": category or "",
            "is_rss": True,
            "logo_base64": avatar_base64,
        }

        def work():
            return _post("/api/news/sources/add", payload)

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Could not add source")
                return
            self.toastMessage.emit("ok", f"Added {name}")
            self.refreshNews(False)

        self._run(work, done)

    @Slot(str, str)
    def deleteCustomSource(self, name, url=""):
        def work():
            return _post("/api/news/sources/delete", {"name": name, "url": url, "feed_url": url})

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Could not delete source")
                return
            self.toastMessage.emit("ok", f"Removed {name}")
            self.refreshNews(False)

        self._run(work, done)

    @Slot(str, str)
    def setSourceAvatar(self, name, local_path):
        """Set a source's avatar from a local image file, copy/normalize, and update."""
        if local_path.startswith("file:///"):
            local_path = urllib.parse.unquote(local_path[8:])
            local_path = os.path.normpath(local_path)

        if not os.path.exists(local_path):
            self.toastMessage.emit("error", f"File not found: {local_path}")
            return

        try:
            from pathlib import Path
            repo_root = Path(__file__).resolve().parent.parent
            avatars_dir = repo_root / "data" / "avatars"
            avatars_dir.mkdir(parents=True, exist_ok=True)

            slug = re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
            slug = re.sub(r'_+', '_', slug).strip('_')
            if not slug:
                slug = "channel"

            try:
                from PIL import Image
                has_pil = True
            except ImportError:
                has_pil = False

            if has_pil:
                img = Image.open(local_path)
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                img = img.resize((128, 128), Image.Resampling.LANCZOS)
                out_path = avatars_dir / f"{slug}.png"
                img.save(out_path, "PNG")
                target_rel = f"data/avatars/{slug}.png"
            else:
                ext = os.path.splitext(local_path)[1].lower()
                if not ext:
                    ext = ".png"
                out_path = avatars_dir / f"{slug}{ext}"
                import shutil
                shutil.copy2(local_path, out_path)
                target_rel = f"data/avatars/{slug}{ext}"

            # Update custom_sources list on disk
            try:
                from frontend.avatar_fetcher import load_sources_file, save_sources_file
            except ImportError:
                from avatar_fetcher import load_sources_file, save_sources_file
            sources = load_sources_file()
            found = False
            for s in sources:
                if s.get("name") == name:
                    s["avatar_path"] = target_rel
                    found = True
                    break

            if not found:
                self.toastMessage.emit("error", f"Source not found: {name}")
                return

            save_sources_file(sources)

            # Update memory cache
            for s in self._custom_sources:
                if s.get("name") == name:
                    s["avatar_path"] = target_rel
                    break

            self._refresh_sources_model()
            self._rebuild_chat_list()
            self.customSourcesUpdated.emit()

            self.toastMessage.emit("ok", "Avatar updated successfully")
        except Exception as e:
            self.toastMessage.emit("error", f"Failed to save avatar: {e}")


    @Slot(str)
    def analyzeSource(self, url):
        def work():
            return _post("/api/news/sources/analyze", {"url": url})

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Analyze failed")
                return
            if result.get("success"):
                self.toastMessage.emit("ok", f"Detected: {result.get('name', 'feed')}")
            else:
                self.toastMessage.emit("error", "No feed detected")

        self._run(work, done)

    # ===================== slots: telegram config =====================
    @Slot(result="QVariant")
    def getTelegramConfig(self):
        try:
            return _get("/api/telegram/config")
        except Exception:  # noqa: BLE001
            return {
                "bot_token": "",
                "default_chat_id": "",
                "sports_chat_id": "",
                "technology_chat_id": "",
                "channel_threads": {},
            }

    @Slot(str, str, str, str, str)
    def saveTelegramConfig(self, bot_token, ent_id, sports_id, tech_id, thread_ids_json):
        try:
            threads = json.loads(thread_ids_json) if thread_ids_json else {}
        except Exception:  # noqa: BLE001
            threads = {}
            self.toastMessage.emit("error", "Thread IDs must be valid JSON")

        payload = {
            "bot_token": bot_token,
            "default_chat_id": ent_id,
            "sports_chat_id": sports_id,
            "technology_chat_id": tech_id,
            "channel_threads": threads,
        }

        def work():
            return _post("/api/telegram/config", payload)

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Could not save config")
                return
            self.toastMessage.emit("ok", "Telegram config saved")
            self.telegramConfigChanged.emit()

        self._run(work, done)

    @Slot()
    def resetTelegramHistory(self):
        def work():
            return _post("/api/telegram/reset_history", {})
        self._run(work, lambda r: self.toastMessage.emit(
            "ok" if not isinstance(r, Exception) else "error",
            "Telegram history reset" if not isinstance(r, Exception) else "Reset failed"))

    @Slot()
    def clearCache(self):
        def work():
            return _post("/api/cache/clear", {})
        self._run(work, lambda r: (
            self.toastMessage.emit(
                "ok" if not isinstance(r, Exception) else "error",
                "Cache cleared" if not isinstance(r, Exception) else "Clear failed"),
            self.refreshNews(False)))

    @Slot(str)
    def ignorePost(self, url):
        def work():
            return _post("/api/news/ignore", {"url": url})
        self._run(work, lambda r: self.refreshNews(False))

    @Slot(result="QVariant")
    def getCustomSources(self):
        return self._custom_sources

    @Slot(str, str, bool, str, str)
    def saveChatAppearance(self, variant, name_color, auto_night, font_family, wallpaper):
        self._ui_settings["appearance"]["auto_night"] = auto_night
        self._set_theme(variant)
        self._set_accent_override(name_color)
        self._set_font_family(font_family)
        self._set_wallpaper_mode(wallpaper)

    @Slot(str, result="QVariantMap")
    def getSettings(self, group):
        if group == "account":
            try:
                backend_config = _get("/api/telegram/config")
            except Exception as e:
                print(f"[Bridge] Failed to fetch backend telegram config: {e}")
                backend_config = {}
            for k, v in backend_config.items():
                self._ui_settings["account"][k] = v
            return self._ui_settings.get("account", {})
        return self._ui_settings.get(group, {})

    @Slot(str, str, "QVariant")
    def setSetting(self, group, key, value):
        if group not in self._ui_settings:
            self._ui_settings[group] = {}
        if key == "channel_threads" and isinstance(value, str):
            try:
                value = json.loads(value)
            except Exception:
                pass
        self._ui_settings[group][key] = value
        self._save_ui_settings(self._ui_settings)
        if group == "appearance":
            if key == "theme":
                self._set_theme(value)
            elif key == "accent_override":
                self._set_accent_override(value)
            elif key == "wallpaper_mode":
                self._set_wallpaper_mode(value)
            elif key == "interface_scale":
                self._set_interface_scale(value)
        elif group == "language":
            if key == "rtl":
                self._set_rtl(bool(value))
        if group == "account":
            tg_keys = {"bot_token", "default_chat_id", "sports_chat_id", "technology_chat_id", "channel_threads"}
            if key in tg_keys:
                payload = {
                    "bot_token": self._ui_settings["account"].get("bot_token", ""),
                    "default_chat_id": self._ui_settings["account"].get("default_chat_id", ""),
                    "sports_chat_id": self._ui_settings["account"].get("sports_chat_id", ""),
                    "technology_chat_id": self._ui_settings["account"].get("technology_chat_id", ""),
                    "channel_threads": self._ui_settings["account"].get("channel_threads", {})
                }
                try:
                    _post("/api/telegram/config", payload)
                    self.telegramConfigChanged.emit()
                except Exception as e:
                    print(f"[Bridge] Failed to post telegram config: {e}")

    def _load_ui_settings(self) -> dict:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "offline_viewer", "assets", "ui_settings.json")
        defaults = {
            "appearance": {
                "theme": "night",
                "font_family": "Roboto",
                "accent_override": "",
                "wallpaper_mode": "pattern",
                "interface_scale": 1.0,
                "auto_night": False,
                "reader_font_family": "Roboto",
                "wallpaper_image": ""
            },
            "notifications": {
                "enabled": True,
                "sound": "default"
            },
            "privacy": {
                "keep_history": "forever",
                "lock_code": ""
            },
            "feed": {
                "reader_mode": "rich",
                "scraping_fallback": True
            },
            "language": {
                "language": "en",
                "rtl": False
            },
            "advanced": {
                "backend_port": 8080,
                "cache_limit_mb": 500
            },
            "account": {
                "api_id": "",
                "api_hash": "",
                "bot_token": "",
                "default_chat_id": "",
                "sports_chat_id": "",
                "technology_chat_id": "",
                "channel_threads": {}
            }
        }
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        loaded = data[0] if isinstance(data[0], dict) else {}
                    elif isinstance(data, dict):
                        loaded = data
                    else:
                        loaded = {}
                    if loaded and not any(isinstance(v, dict) for v in loaded.values()):
                        # Flat structure fallback
                        normalized = {
                            "appearance": {
                                "theme": loaded.get("theme", "night"),
                                "font_family": loaded.get("font_family", "Roboto"),
                                "accent_override": loaded.get("accent_override", ""),
                                "wallpaper_mode": loaded.get("wallpaper_mode", "pattern"),
                                "interface_scale": loaded.get("interface_scale", 1.0),
                                "auto_night": loaded.get("auto_night", False)
                            },
                            "notifications": {
                                "enabled": loaded.get("notifications_enabled", True),
                                "sound": loaded.get("notifications_sound", "default")
                            },
                            "privacy": {
                                "keep_history": loaded.get("keep_history", "forever"),
                                "lock_code": loaded.get("lock_code", "")
                            },
                            "feed": {
                                "reader_mode": loaded.get("reader_mode", "rich"),
                                "scraping_fallback": loaded.get("scraping_fallback", True)
                            },
                            "language": {
                                "language": loaded.get("language", "en"),
                                "rtl": loaded.get("rtl", False)
                            },
                            "advanced": {
                                "backend_port": loaded.get("backend_port", 8080),
                                "cache_limit_mb": loaded.get("cache_limit_mb", 500)
                            },
                            "account": {
                                "api_id": loaded.get("api_id", ""),
                                "api_hash": loaded.get("api_hash", "")
                            }
                        }
                        loaded = normalized
                    def merge(d1, d2):
                        for k, v in d2.items():
                            if k not in d1:
                                d1[k] = v
                            elif isinstance(v, dict) and isinstance(d1[k], dict):
                                merge(d1[k], v)
                    merge(loaded, defaults)
                    app_settings = loaded.get("appearance", {})
                    if app_settings.get("theme") == "dark":
                        app_settings["theme"] = "night"
                    elif app_settings.get("theme") == "light":
                        app_settings["theme"] = "day"
                    return loaded
        except Exception as e:
            print(f"Error loading UI settings: {e}")
        return defaults

    def _save_ui_settings(self, settings: dict):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "offline_viewer", "assets", "ui_settings.json")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump([settings], f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving UI settings: {e}")

    # ===================== slots: context menu (UI-state) =====================
    @Slot(str)
    def openInNewWindow(self, channel_id):
        self.toastMessage.emit("ok", "Open in new window")

    @Slot(str)
    def archiveChat(self, channel_id):
        self._hidden.add(channel_id)
        if channel_id == self._current_channel_id:
            self._current_channel_id = ""
            self.currentChannelIdChanged.emit("")
            self._message_model.set_items([])
        self._rebuild_chat_list()
        self.toastMessage.emit("ok", "Channel archived")

    @Slot(str)
    def togglePin(self, channel_id):
        if channel_id in self._pinned:
            self._pinned.discard(channel_id)
        else:
            self._pinned.add(channel_id)
        self._save_pins()
        self._rebuild_chat_list()

    # ---- Item 2: per-post pinning -----------------------------------------
    @Slot(str)
    def toggleMessagePin(self, url):
        if not url:
            return
        if url in self._pinned_messages:
            self._pinned_messages.discard(url)
        else:
            self._pinned_messages.add(url)
        self._save_pins()
        if self._current_channel_id:
            self._rebuild_messages(self._current_channel_id)

    @Slot(result="QVariant")
    def currentPinnedPosts(self):
        return list(self._current_pinned_posts)

    def _save_pins(self):
        grp = self._ui_settings.setdefault("pins", {})
        grp["channels"] = [c for c in self._pinned
                           if c not in (SPECIAL_SAVED, SPECIAL_ARCHIVED)]
        grp["messages"] = list(self._pinned_messages)
        self._save_ui_settings(self._ui_settings)

    # ---- Item 1: reader font convenience slot -----------------------------
    @Slot(str)
    def setReaderFont(self, value):
        self._set_reader_font_family(value)

    # ---- Item 8: custom wallpaper image -----------------------------------
    @Slot()
    def pickWallpaperImage(self):
        try:
            from PySide6.QtWidgets import QFileDialog
        except Exception:
            self.toastMessage.emit("error", "File dialog unavailable")
            return
        path, _ = QFileDialog.getOpenFileName(
            None, "Choose wallpaper image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if not path:
            return
        stored = self._store_wallpaper_image(path)
        if not stored:
            self.toastMessage.emit("error", "Could not load that image")
            return
        self._set_wallpaper_image(stored)
        self._set_wallpaper_mode("image")
        self.toastMessage.emit("ok", "Wallpaper updated")

    def _store_wallpaper_image(self, src_path):
        try:
            from pathlib import Path
            import shutil
            repo_root = Path(__file__).resolve().parent.parent
            dest_dir = repo_root / "data" / "wallpapers"
            dest_dir.mkdir(parents=True, exist_ok=True)
            ext = os.path.splitext(src_path)[1].lower() or ".png"
            dest = dest_dir / ("wallpaper" + ext)
            shutil.copy2(src_path, dest)
            return dest.absolute().as_uri()
        except Exception as e:
            print(f"[Bridge] wallpaper copy failed: {e}")
            return ""

    # ---- Item 7: user-defined folders that combine channels ---------------
    @Slot(result="QVariant")
    def getCustomFolders(self):
        return [dict(f) for f in self._custom_folders]

    @Slot(result="QVariant")
    def getAllChannels(self):
        return [c for c in self._channels() if c not in self._hidden]

    @Slot(str, result=str)
    def createFolder(self, name):
        name = (name or "").strip() or "Folder"
        fid = "folder:" + re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower()) + ":" + str(len(self._custom_folders) + 1)
        self._custom_folders.append({"id": fid, "name": name, "channels": []})
        self._save_folders()
        return fid

    @Slot(str, str)
    def renameFolder(self, fid, name):
        for f in self._custom_folders:
            if f.get("id") == fid:
                f["name"] = (name or "").strip() or f.get("name", "Folder")
                break
        self._save_folders()

    @Slot(str)
    def deleteFolder(self, fid):
        self._custom_folders = [f for f in self._custom_folders if f.get("id") != fid]
        self._save_folders()
        if self._active_tab == fid:
            self._set_tab("entertainment")

    @Slot(str, str)
    def addChannelToFolder(self, fid, channel_id):
        for f in self._custom_folders:
            if f.get("id") == fid:
                chans = f.setdefault("channels", [])
                if channel_id and channel_id not in chans:
                    chans.append(channel_id)
                break
        self._save_folders()
        self.toastMessage.emit("ok", "Added to folder")
        if self._active_tab == fid:
            self._rebuild_chat_list()

    @Slot(str, str)
    def removeChannelFromFolder(self, fid, channel_id):
        for f in self._custom_folders:
            if f.get("id") == fid:
                f["channels"] = [c for c in f.get("channels", []) if c != channel_id]
                break
        self._save_folders()
        if self._active_tab == fid:
            self._rebuild_chat_list()

    def _save_folders(self):
        grp = self._ui_settings.setdefault("folders", {})
        grp["custom"] = [dict(f) for f in self._custom_folders]
        self._save_ui_settings(self._ui_settings)
        self.customFoldersChanged.emit()

    def _folder_by_id(self, fid):
        for f in self._custom_folders:
            if f.get("id") == fid:
                return f
        return None

    def _passes_active_filter(self, cid):
        folder = self._folder_by_id(self._active_tab)
        if folder is not None:
            return cid in (folder.get("channels") or [])
        if self._active_tab in ("settings",):
            return True
        return self._section_of(cid) == self._active_tab

    def _header_avatar_for(self, cid):
        if cid == SPECIAL_SAVED:
            return "bookmark"
        if cid == SPECIAL_LOGS:
            return "logs"
        if cid == SPECIAL_BIN:
            return "trash"
        if cid == SPECIAL_ARCHIVED:
            return ""
        return self._avatar_for(cid)

    @Slot(str)
    def toggleMute(self, channel_id):
        if channel_id in self._muted:
            self._muted.discard(channel_id)
        else:
            self._muted.add(channel_id)
        self._rebuild_chat_list()

    @Slot(str)
    def markUnread(self, channel_id):
        self._read_unread.discard(channel_id)
        self._rebuild_chat_list()

    @Slot(str)
    def addToFolder(self, channel_id):
        self.toastMessage.emit("ok", "Added to folder")

    @Slot(str)
    def clearHistory(self, channel_id):
        if channel_id == self._current_channel_id:
            self._message_model.set_items([])
        self.toastMessage.emit("ok", "History cleared")

    @Slot(str)
    def deleteChat(self, channel_id):
        self._hidden.add(channel_id)
        if channel_id == self._current_channel_id:
            self._current_channel_id = ""
            self.currentChannelIdChanged.emit("")
            self._message_model.set_items([])
        self._rebuild_chat_list()
        self.toastMessage.emit("ok", "Channel removed")

    # ===================== slots: Bin (recoverable delete) ================
    @staticmethod
    def _now_iso() -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def _article_key(self, art) -> str:
        # Mirrors gui_server.get_article_key(): url, else hash of the title.
        url = (art.get("url") or "").strip()
        if url:
            return url
        return "hash:" + hashlib.sha256((art.get("title") or "").encode("utf-8")).hexdigest()

    def _find_article(self, url, title=""):
        url = (url or "").strip()
        pools = (self._articles, self._saved_articles, self._archived_articles)
        if url:
            for pool in pools:
                for a in pool:
                    if (a.get("url") or "").strip() == url:
                        return a
        if title:
            for pool in pools:
                for a in pool:
                    if a.get("title") == title:
                        return a
        return None

    def _save_bin(self):
        self._ui_settings.setdefault("bin", {})["items"] = [dict(a) for a in self._binned_items]
        self._save_ui_settings(self._ui_settings)

    def _refresh_after_bin_change(self):
        self._rebuild_chat_list()
        if self._current_channel_id:
            self._rebuild_messages(self._current_channel_id)

    @Slot(str, str)
    def deletePost(self, url, title=""):
        art = self._find_article(url, title) or {
            "title": title, "url": url, "description": "",
            "thumbnail": "", "category": "", "source": "", "section": "",
        }
        key = self._article_key(art)
        if key not in self._binned_keys:
            binned = dict(art)
            binned["deleted_at"] = self._now_iso()
            self._binned_items.insert(0, binned)
            self._binned_keys.add(key)
            self._save_bin()
        self.toastMessage.emit("ok", "Moved to Bin")
        self._refresh_after_bin_change()

    @Slot(str, str)
    def restorePost(self, url, title=""):
        key = self._article_key({"url": url, "title": title})
        before = len(self._binned_items)
        self._binned_items = [a for a in self._binned_items if self._article_key(a) != key]
        self._binned_keys.discard(key)
        if len(self._binned_items) != before:
            self._save_bin()
            self.toastMessage.emit("ok", "Restored from Bin")
        self._refresh_after_bin_change()

    @Slot(str, str)
    def purgePost(self, url, title=""):
        key = self._article_key({"url": url, "title": title})
        self._binned_items = [a for a in self._binned_items if self._article_key(a) != key]
        self._binned_keys.discard(key)
        self._save_bin()
        self.toastMessage.emit("ok", "Permanently deleted")
        self._refresh_after_bin_change()

    @Slot()
    def emptyBin(self):
        self._binned_items = []
        self._binned_keys = set()
        self._save_bin()
        self.toastMessage.emit("ok", "Bin emptied")
        self._refresh_after_bin_change()

    @Slot(result=int)
    def binCount(self):
        return len(self._binned_items)

    # ===================== internals =====================
    def _run(self, work, done):
        task = _Task(work, parent=self)
        self._active_tasks.add(task)

        receiver = TaskResultReceiver(done, self)

        def wrapper(result):
            self._active_tasks.discard(task)
            try:
                task.signals.setParent(None)
            except RuntimeError:
                pass
            receiver.setParent(None)

        receiver.result_received.connect(wrapper)
        task.signals.finished.connect(receiver.handle_result, Qt.QueuedConnection)
        self._pool.start(task)

    def _refresh_sources_model(self):
        rows = []
        for s in self._custom_sources:
            rows.append({
                "name": s.get("name", ""),
                "url": s.get("feed_url") or s.get("url", ""),
                "section": (s.get("section") or "Entertainment").title(),
                "category": s.get("category", ""),
                "avatarPath": self._source_avatar(s),
            })
        self._sources_model.set_items(rows)

    def _channels(self) -> List[str]:
        seen, order = set(), []
        for a in self._articles:
            src = a.get("source") or a.get("category") or "Feed"
            if src not in seen:
                seen.add(src)
                order.append(src)
        return order

    def _section_of(self, channel_id: str) -> str:
        for a in self._articles:
            if (a.get("source") or a.get("category")) == channel_id:
                return (a.get("section") or "Entertainment").lower()
        return "entertainment"

    def _name_for_channel(self, channel_id: str) -> str:
        if channel_id == SPECIAL_SAVED:
            return "Saved Messages"
        if channel_id == SPECIAL_ARCHIVED:
            return "Archived Messages"
        if channel_id == SPECIAL_SEARCH:
            return "Search results"
        if channel_id == SPECIAL_LOGS:
            return "System Logs"
        if channel_id == SPECIAL_BIN:
            return "Bin"
        return channel_id

    def _articles_for_channel(self, channel_id: str) -> List[Dict[str, Any]]:
        if channel_id == SPECIAL_BIN:
            return list(self._binned_items)
        if channel_id == SPECIAL_SAVED:
            return [a for a in self._saved_articles
                    if self._article_key(a) not in self._binned_keys]
        if channel_id == SPECIAL_ARCHIVED:
            return [a for a in self._archived_articles
                    if self._article_key(a) not in self._binned_keys]
        if channel_id == SPECIAL_SEARCH:
            return []
        return [a for a in self._articles
                if (a.get("source") or a.get("category")) == channel_id
                and self._article_key(a) not in self._binned_keys]

    def _matches_search(self, name: str) -> bool:
        if not self._search:
            return True
        return self._search.lower() in (name or "").lower()

    def _rebuild_chat_list(self):
        rows: List[Dict[str, Any]] = []

        if self._search:
            rows.append(self._special_row(SPECIAL_SEARCH, "Search results", "search"))
            
            query_normalized = strip_diacritics(self._search).lower()
            query_terms = [t for t in query_normalized.split() if t]
            
            channels_data = []
            
            for cid in self._channels():
                if cid in self._hidden:
                    continue
                arts = self._articles_for_channel(cid)
                matching_arts = [a for a in arts if self._match_article(a, query_terms)]
                match_count = len(matching_arts)
                if match_count >= 1:
                    max_score = max(self._score_article(a, query_terms) for a in matching_arts)
                    max_ts = max(self._get_article_timestamp(a) for a in matching_arts)
                    channels_data.append({
                        "channelId": cid,
                        "name": cid,
                        "lastMessage": matching_arts[0].get("title", ""),
                        "time": self._short_time(matching_arts[0].get("published") or matching_arts[0].get("timestamp") or ""),
                        "unread": 0,
                        "avatarPath": self._avatar_for(cid),
                        "section": self._section_of(cid),
                        "muted": cid in self._muted,
                        "pinned": cid in self._pinned,
                        "matchCount": match_count,
                        "score": max_score,
                        "recency": max_ts
                    })
                    
            saved_matching = [a for a in self._saved_articles if self._match_article(a, query_terms)]
            if len(saved_matching) >= 1:
                max_score = max(self._score_article(a, query_terms) for a in saved_matching)
                max_ts = max(self._get_article_timestamp(a) for a in saved_matching)
                channels_data.append({
                    "channelId": SPECIAL_SAVED,
                    "name": "Saved Messages",
                    "lastMessage": saved_matching[0].get("title", ""),
                    "time": self._short_time(saved_matching[0].get("published") or saved_matching[0].get("timestamp") or ""),
                    "unread": 0,
                    "avatarPath": "bookmark",
                    "section": self._active_tab,
                    "muted": False,
                    "pinned": SPECIAL_SAVED in self._pinned,
                    "matchCount": len(saved_matching),
                    "score": max_score,
                    "recency": max_ts
                })
                
            archived_matching = [a for a in self._archived_articles if self._match_article(a, query_terms)]
            if len(archived_matching) >= 1:
                max_score = max(self._score_article(a, query_terms) for a in archived_matching)
                max_ts = max(self._get_article_timestamp(a) for a in archived_matching)
                channels_data.append({
                    "channelId": SPECIAL_ARCHIVED,
                    "name": "Archived Messages",
                    "lastMessage": archived_matching[0].get("title", ""),
                    "time": self._short_time(archived_matching[0].get("published") or archived_matching[0].get("timestamp") or ""),
                    "unread": 0,
                    "avatarPath": "archive",
                    "section": self._active_tab,
                    "muted": False,
                    "pinned": SPECIAL_ARCHIVED in self._pinned,
                    "matchCount": len(archived_matching),
                    "score": max_score,
                    "recency": max_ts
                })
                
            channels_data.sort(key=lambda x: (x["score"], x["recency"]), reverse=True)
            rows.extend(channels_data)
            
        else:
            if self._matches_search("Saved Messages"):
                rows.append(self._special_row(SPECIAL_SAVED, "Saved Messages", "bookmark"))
            if self._matches_search("Archived Messages"):
                rows.append(self._special_row(SPECIAL_ARCHIVED, "Archived Messages", "archive"))
            if self._binned_items and self._matches_search("Bin"):
                rows.append(self._special_row(SPECIAL_BIN, "Bin", "trash"))

            chan_rows = []
            for cid in self._channels():
                if cid in self._hidden:
                    continue
                if not self._passes_active_filter(cid):
                    continue
                if not self._matches_search(cid):
                    continue
                arts = self._articles_for_channel(cid)
                last = arts[0] if arts else {}
                unread = 0 if cid in self._read_unread else (_hash_code(cid) % 9)
                chan_rows.append({
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
            # Item 2: pinned channels float to the top (stable within groups).
            chan_rows.sort(key=lambda r: 0 if r.get("pinned") else 1)
            rows.extend(chan_rows)
                
        self._chat_model.set_items(rows)

    def _special_row(self, cid, name, avatar):
        return {
            "channelId": cid, "name": name, "lastMessage": "",
            "time": "", "unread": 0, "avatarPath": avatar,
            "section": self._active_tab, "muted": False, "pinned": True,
            "matchCount": 0
        }

    def _avatar_for(self, cid):
        for s in self._custom_sources:
            if s.get("name") == cid:
                return self._source_avatar(s)
        try:
            from pathlib import Path
            repo_root = Path(__file__).resolve().parent.parent
            index_path = repo_root / "offline_viewer" / "assets" / "avatars" / "index.json"
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_map = json.load(f)
                val = index_map.get(cid.lower())
                if val:
                    p = repo_root / "offline_viewer" / val
                    if p.exists():
                        return p.absolute().as_uri()
        except Exception:
            pass
        return ""

    def _source_avatar(self, s):
        """Resolve a source avatar: explicit path/URL, else base64 logo, else none."""
        ap = s.get("avatar_path") or s.get("logo") or s.get("icon") or ""
        if ap:
            if not ap.startswith(("http:", "https:", "data:")):
                from pathlib import Path
                repo_root = Path(__file__).resolve().parent.parent
                p = Path(ap)
                if not p.is_absolute():
                    if (repo_root / p).exists():
                        p = repo_root / p
                    else:
                        p = repo_root / "offline_viewer" / p
                if p.exists():
                    return p.absolute().as_uri()
            return ap
        b64 = s.get("logo_base64") or ""
        if b64:
            return b64 if b64.startswith("data:") else ("data:image/png;base64," + b64)
        return ""

    def _rebuild_messages(self, channel_id):
        if channel_id == SPECIAL_LOGS:
            self.loadLogs()
            items = []
            for entry in self._activity_log:
                items.append({
                    "title": entry.get("section", "Log"),
                    "text": entry.get("message", ""),
                    "url": "", "thumbnail": "",
                    "time": self._short_time(entry.get("time", "")),
                    "outgoing": False, "read": True, "views": 0,
                    "reactions": [], "source": "logs", "topic": "",
                    "day": "",
                })
            items.reverse()  # newest first (bottom-to-top view)
            self._message_model.set_items(items)
            return

        arts = self._articles_for_channel(channel_id)
        if self._msg_search:
            q = self._msg_search.lower()
            arts = [a for a in arts
                    if q in (str(a.get("title", "")) + " " + str(a.get("description", ""))).lower()]
        # Item 4: render posts oldest -> newest (ascending by article timestamp).
        arts = sorted(arts, key=self._get_article_timestamp)
        items = []
        pinned_posts = []
        for a in arts:
            url = a.get("url", "")
            code = _hash_code(url or a.get("title", ""))
            is_pinned = bool(url) and url in self._pinned_messages
            items.append({
                "title": a.get("title", ""),
                "text": a.get("description", ""),
                "url": url,
                "thumbnail": a.get("thumbnail", ""),
                "time": self._abs_datetime(a.get("published") or a.get("timestamp", "")),
                "outgoing": False,
                "read": True,
                "views": 1000 + (code % 48000),
                "reactions": self._reactions_for(code),
                "source": a.get("source", ""),
                "topic": a.get("category", ""),
                "day": (a.get("published") or "")[:10],
                "pinned": is_pinned,
            })
            if is_pinned:
                pinned_posts.append({"title": a.get("title", ""), "url": url})
        self._message_model.set_items(items)
        # Item 2: expose the open channel's pinned posts to the pinned bar.
        self._current_pinned_posts = pinned_posts
        self.pinnedPostsChanged.emit()

    def _reactions_for(self, code):
        out = []
        n = code % 4
        for i in range(n):
            emoji = REACTION_EMOJIS[(code >> (i + 1)) % len(REACTION_EMOJIS)]
            out.append({"emoji": emoji, "count": 1 + ((code >> i) % 25),
                        "active": (code >> i) % 5 == 0})
        return out

    def _to_send_article(self, a):
        return {
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "url": a.get("url", ""),
            "thumbnail": a.get("thumbnail", ""),
            "category": a.get("category", ""),
            "section": a.get("section", "Entertainment"),
        }

    def _articles_payload_for_title(self, title):
        for a in self._articles:
            if a.get("title") == title:
                return [self._to_send_article(a)]
        return []

    def _forward_done(self, result, label):
        if isinstance(result, Exception):
            self.toastMessage.emit("error", f"Could not forward to {label}")
        else:
            self.toastMessage.emit("ok", f"Forwarded to {label}")

    @staticmethod
    def _short_time(value: str) -> str:
        if not value:
            return ""
        v = str(value)
        if "T" in v and len(v) >= 16:
            return v[11:16]
        return v[:16]

    @staticmethod
    def _abs_datetime(value) -> str:
        # Item 3: always show an explicit calendar date + time (never relative
        # labels like Today/Yesterday). Format: "YYYY-MM-DD HH:MM".
        if value is None or value == "":
            return ""
        if isinstance(value, (int, float)):
            try:
                from datetime import datetime
                return datetime.fromtimestamp(float(value)).strftime("%Y-%m-%d %H:%M")
            except Exception:
                return str(value)
        v = str(value).strip()
        try:
            from dateutil import parser as _dtp
            return _dtp.parse(v).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
        if "T" in v and len(v) >= 16:
            return v[:10] + " " + v[11:16]
        return v[:16]
