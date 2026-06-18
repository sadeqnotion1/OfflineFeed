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


class _Task(QRunnable):
    """Run a blocking backend call off the GUI thread."""

    def __init__(self, fn, on_done=None):
        super().__init__()
        self._fn = fn
        self._on_done = on_done

    def run(self):
        try:
            result = self._fn()
        except Exception as exc:  # noqa: BLE001 - surfaced to UI as a toast
            result = exc
        if self._on_done:
            self._on_done(result)


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
#  Bridge
# --------------------------------------------------------------------------- #
SPECIAL_SAVED = "SavedMessages"
SPECIAL_LOGS = "SystemLogs"
REACTION_EMOJIS = ["\U0001F44D", "\u2764\ufe0f", "\U0001F525", "\U0001F389", "\U0001F44F"]


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
    articleBlocksLoaded = Signal(str, "QVariant")
    toastMessage = Signal(str, str)  # (kind, message)

    def __init__(self, chat_model: ChatListModel, message_model: MessageModel,
                 sources_model: SourcesModel, parent=None):
        super().__init__(parent)
        self._chat_model = chat_model
        self._message_model = message_model
        self._sources_model = sources_model
        self._pool = QThreadPool.globalInstance()

        self._theme = "night"
        self._rtl = False
        self._active_tab = "entertainment"
        self._current_channel_id = ""
        self._current_channel_name = ""
        self._search = ""

        self._articles: List[Dict[str, Any]] = []
        self._custom_sources: List[Dict[str, Any]] = []
        self._activity_log: List[Dict[str, Any]] = []
        self._muted: set = set()
        self._pinned: set = {SPECIAL_SAVED}
        self._read_unread: set = set()
        self._hidden: set = set()  # archived / deleted channels
        self._msg_search: str = ""  # in-channel message search

        self.refreshNews(False)

    # ===================== properties =====================
    def _get_theme(self):
        return self._theme

    def _set_theme(self, value):
        if value != self._theme:
            self._theme = value
            self.themeChanged.emit(value)

    theme = Property(str, _get_theme, _set_theme, notify=themeChanged)

    def _get_rtl(self):
        return self._rtl

    def _set_rtl(self, value):
        if value != self._rtl:
            self._rtl = value
            self.rtlChanged.emit(value)

    rtl = Property(bool, _get_rtl, _set_rtl, notify=rtlChanged)

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

    @Slot(str)
    def setSearch(self, query):
        self._search = query or ""
        self.searchQueryChanged.emit(self._search)
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
        self._read_unread.add(channel_id)
        self.currentChannelIdChanged.emit(channel_id)
        self.currentChannelNameChanged.emit(self._current_channel_name)
        self._rebuild_messages(channel_id)
        self._rebuild_chat_list()

    # ===================== slots: data loading =====================
    @Slot(bool)
    def refreshNews(self, force):
        def work():
            return _get("/api/news" + ("?refresh=true" if force else ""))

        def done(result):
            if isinstance(result, Exception):
                self.toastMessage.emit("error", "Backend not reachable yet…")
                return
            self._articles = result.get("articles", []) or []
            self._custom_sources = result.get("custom_sources", []) or []
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

    # ===================== slots: forwarding =====================
    @Slot(str)
    def forwardToSaved(self, title):
        def work():
            return _post("/api/telegram/send_channel",
                         {"channel_name": SPECIAL_SAVED,
                          "articles": self._articles_payload_for_title(title)})
        self._run(work, lambda r: self._forward_done(r, "Saved"))

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
        # Appearance prefs are UI-only; keep theme variant in sync with bridge.
        self._set_theme(variant)

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
        self._rebuild_chat_list()

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

    # ===================== internals =====================
    def _run(self, work, done):
        self._pool.start(_Task(work, done))

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
        if channel_id == SPECIAL_LOGS:
            return "System Logs"
        return channel_id

    def _articles_for_channel(self, channel_id: str) -> List[Dict[str, Any]]:
        return [a for a in self._articles
                if (a.get("source") or a.get("category")) == channel_id]

    def _matches_search(self, name: str) -> bool:
        if not self._search:
            return True
        return self._search.lower() in (name or "").lower()

    def _rebuild_chat_list(self):
        rows: List[Dict[str, Any]] = []

        # Pinned specials first
        if self._matches_search("Saved Messages"):
            rows.append(self._special_row(SPECIAL_SAVED, "Saved Messages", "bookmark"))

        for cid in self._channels():
            if cid in self._hidden:
                continue
            if self._active_tab not in ("settings",) and self._section_of(cid) != self._active_tab:
                continue
            if not self._matches_search(cid):
                continue
            arts = self._articles_for_channel(cid)
            last = arts[0] if arts else {}
            unread = 0 if cid in self._read_unread else (_hash_code(cid) % 9)
            rows.append({
                "channelId": cid,
                "name": cid,
                "lastMessage": last.get("title", ""),
                "time": self._short_time(last.get("published") or last.get("timestamp", "")),
                "unread": unread,
                "avatarPath": self._avatar_for(cid),
                "section": self._section_of(cid),
                "muted": cid in self._muted,
                "pinned": cid in self._pinned,
            })
        self._chat_model.set_items(rows)

    def _special_row(self, cid, name, avatar):
        return {
            "channelId": cid, "name": name, "lastMessage": "",
            "time": "", "unread": 0, "avatarPath": avatar,
            "section": self._active_tab, "muted": False, "pinned": True,
        }

    def _avatar_for(self, cid):
        for s in self._custom_sources:
            if s.get("name") == cid:
                return self._source_avatar(s)
        return ""

    def _source_avatar(self, s):
        """Resolve a source avatar: explicit path/URL, else base64 logo, else none."""
        ap = s.get("avatar_path") or s.get("logo") or s.get("icon") or ""
        if ap:
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

        arts = (self._articles if channel_id == SPECIAL_SAVED
                else self._articles_for_channel(channel_id))
        if self._msg_search:
            q = self._msg_search.lower()
            arts = [a for a in arts
                    if q in (str(a.get("title", "")) + " " + str(a.get("description", ""))).lower()]
        items = []
        for a in arts:
            url = a.get("url", "")
            code = _hash_code(url or a.get("title", ""))
            items.append({
                "title": a.get("title", ""),
                "text": a.get("description", ""),
                "url": url,
                "thumbnail": a.get("thumbnail", ""),
                "time": self._short_time(a.get("published") or a.get("timestamp", "")),
                "outgoing": False,
                "read": True,
                "views": 1000 + (code % 48000),
                "reactions": self._reactions_for(code),
                "source": a.get("source", ""),
                "topic": a.get("category", ""),
                "day": (a.get("published") or "")[:10],
            })
        self._message_model.set_items(items)

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
