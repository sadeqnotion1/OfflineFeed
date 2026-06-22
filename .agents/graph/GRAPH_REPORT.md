# OfflineFeed Knowledge Graph Report

**Repo:** `sadeqnotion1/OfflineFeed`  
**Generated:** 2026-06-19T09:16:05.075279+00:00  
**Nodes:** 74 | **Edges:** 134

> OfflineFeed is a Windows desktop news/RSS aggregator (PySide6 + QML) that reads feeds offline, in a TelegramDesktop-style 3-pane UI, and reposts channels to Telegram. A local Python `gui_server.py` HTTP backend (port 8080) does the aggregation; the QML UI talks to it only over HTTP through a `ChatBridge`.

## God nodes

The most-connected hubs — where structure and control flow concentrate.

- **gui_server.py** (file, degree 22) — Local ThreadingHTTPServer (port 8080) that aggregates RSS/HTML/Telegram/Twitter sources, caches news, serves the API and reposts to Telegram.
- **ChatBridge** (class, degree 19) — Imperative surface QML calls into (slots) and observes (properties/signals); owns settings, models and backend calls.
- **frontend/qml/Main.qml** (file, degree 13) — Frameless root window: 3-pane Telegram layout (rail | chat list | chat view) plus slide-in info panel, reader overlay and toast.
- **frontend/bridge.py** (file, degree 12) — QObject + QAbstractListModel layer that exposes the unchanged backend HTTP API to QML.
- **main()** (function, degree 11) — Creates the QApplication, instantiates the four models + ChatBridge, wires QML context properties and loads Main.qml.
- **frontend/debug.py** (file, degree 10) — Diagnostics + logging subsystem with no PySide6 dependency: rotating log, ring buffer, excepthooks, and the preflight doctor.

## Communities

### App bootstrap & lifecycle (7 nodes)
_Launch and process lifecycle: the smart launcher, the PySide6 entry point, font enumeration and backend bootstrap._

- **main()** (function) `frontend/app.py:main`: Creates the QApplication, instantiates the four models + ChatBridge, wires QML context properties and loads Main.qml.
- **frontend/app.py** (file) `frontend/app.py:1`: PySide6 entry point: boots the backend thread, loads fonts, registers bridge+models as QML context properties, loads Main.qml.
- **main()** (function) `run_offlinefeed.py:38`: Parses flags (--doctor/--force/--refresh-avatars), runs the doctor, refuses to launch on FAIL, then runs the GUI as a child process.
- **start_backend()** (function) `frontend/app.py:start_backend`: Imports gui_server in a daemon thread and calls the first available entry point (start_server/main/run/start/serve).
- **run_offlinefeed.py** (file) `run_offlinefeed.py:1`: Smart launcher: runs diagnostics, backfills avatars, then spawns frontend.app and tails the log on failure.
- **enumerate_system_fonts()** (function) `frontend/app.py:enumerate_system_fonts`: Returns a de-duplicated, sorted list of installed font families for the QML font picker.
- **get_backend_port() [app]** (function) `frontend/app.py:get_backend_port`: Reads backend_port from ui_settings.json, defaulting to 8080.

### Diagnostics & logging (10 nodes)
_The no-PySide6 doctor/logging layer that turns opaque 'Code: 1' failures into actionable PASS/WARN/FAIL reports._

- **frontend/debug.py** (file) `frontend/debug.py:1`: Diagnostics + logging subsystem with no PySide6 dependency: rotating log, ring buffer, excepthooks, and the preflight doctor.
- **run_diagnostics()** (function) `frontend/debug.py:run_diagnostics`: Runs all preflight checks and returns a structured PASS/WARN/FAIL report.
- **get_logger()** (function) `frontend/debug.py:get_logger`: Singleton logger writing to console, a rotating file, and the in-memory ring buffer.
- **probe_backend_import()** (function) `frontend/debug.py:probe_backend_import`: Imports gui_server in a clean subprocess to surface the real import-time traceback behind 'Code: 1'.
- **check_backend_module()** (function) `frontend/debug.py:check_backend_module`: Verifies gui_server is resolvable on sys.path the same way app.py searches.
- **_RingBufferHandler** (class) `frontend/debug.py:_RingBufferHandler`: Logging handler that keeps the most recent records in memory for the in-app System Logs panel.
- **main()** (function) `frontend/doctor.py:main`: Resolves the port from settings, runs diagnostics, prints the report, returns the exit code.
- **install_excepthooks()** (function) `frontend/debug.py:install_excepthooks`: Routes uncaught main-thread and daemon-thread exceptions into the log.
- **frontend/doctor.py** (file) `frontend/doctor.py:1`: One-command CLI health check (python -m frontend.doctor) that wraps debug.run_diagnostics and exits 0/1.
- **logs/offlinefeed_debug.log** (resource) `logs/offlinefeed_debug.log`: Rotating debug log written by the logger; tailed by the launcher on a non-zero exit.

### UI ↔ backend bridge (11 nodes)
_The QObject/list-model layer translating the QML UI's intents into defensive HTTP calls against the backend._

- **ChatBridge** (class) `frontend/bridge.py:ChatBridge`: Imperative surface QML calls into (slots) and observes (properties/signals); owns settings, models and backend calls.
- **frontend/bridge.py** (file) `frontend/bridge.py:1`: QObject + QAbstractListModel layer that exposes the unchanged backend HTTP API to QML.
- **ChatListModel** (class) `frontend/bridge.py:ChatListModel`: List model backing the channel list (incl. Saved Messages + System Logs).
- **_get()** (function) `frontend/bridge.py:_get`: Defensive HTTP GET wrapper around the backend API; retries once after re-resolving the port.
- **MessageModel** (class) `frontend/bridge.py:MessageModel`: List model backing the right pane: articles/posts of the selected channel.
- **SourcesModel** (class) `frontend/bridge.py:SourcesModel`: List model for custom RSS/news sources shown on the Settings page.
- **_post()** (function) `frontend/bridge.py:_post`: Defensive HTTP POST wrapper around the backend API; retries once after re-resolving the port.
- **SearchResultsModel** (class) `frontend/bridge.py:SearchResultsModel`: List model for global search results.
- **get_backend_port() [bridge]** (function) `frontend/bridge.py:get_backend_port`: Caches and returns backend_port from ui_settings.json, defaulting to 8080.
- **_Task / QThreadPool** (class) `frontend/bridge.py:_Task`: QRunnable that runs blocking backend calls off the GUI thread and emits the result via a signal.
- **highlight_text()** (function) `frontend/bridge.py:highlight_text`: Wraps matched search terms in bold colored markup for the results UI.

### QML UI layer (12 nodes)
_The QML view tree: a frameless 3-pane Telegram layout driven by the Theme singleton and the bridge._

- **frontend/qml/Main.qml** (file) `frontend/qml/Main.qml:1`: Frameless root window: 3-pane Telegram layout (rail | chat list | chat view) plus slide-in info panel, reader overlay and toast.
- **ChatView** (component) `frontend/qml/components/ChatView.qml`: Right conversation pane bound to messageModel; forwards channels and opens the reader.
- **ChatList** (component) `frontend/qml/components/ChatList.qml`: Middle channel list bound to chatModel; opens chats and raises the context menu.
- **SettingsView** (component) `frontend/qml/components/SettingsView.qml`: Settings page loaded on demand; binds appearance/language/source settings to the bridge.
- **Theme (themes singleton)** (component) `frontend/qml/themes`: QML singleton holding theme variant, RTL, fonts, accent and wallpaper; kept in sync with ChatBridge via Bindings.
- **FolderRail** (component) `frontend/qml/components/FolderRail.qml`: Left rail of folder/tab icons; emits tab + settings selection to the bridge.
- **ReaderView** (component) `frontend/qml/components/ReaderView.qml`: Full-body offline article reader overlay.
- **ChatContextMenu** (component) `frontend/qml/components/ChatContextMenu.qml`: Per-channel context menu (pin/mute/archive/delete/mark unread/add to folder).
- **TitleBar** (component) `frontend/qml/components/TitleBar.qml`: Custom frameless title bar with minimize/maximize/close and system move.
- **SearchResultsView** (component) `frontend/qml/components/SearchResultsView.qml`: Detail pane shown when the SearchResults virtual channel is active.
- **InfoPanel** (component) `frontend/qml/components/InfoPanel.qml`: Slide-in channel info panel overlaying the right side.
- **AddToFolderDialog** (component) `frontend/qml/components/AddToFolderDialog.qml`: Dialog to choose/create a custom folder for a channel.

### Feed Server backend & scrapers (20 nodes)
_The local Feed Server: source scrapers, the news cache, the HTTP API and Telegram reposting._

- **gui_server.py** (file) `gui_server.py:1`: Local ThreadingHTTPServer (port 8080) that aggregates RSS/HTML/Telegram/Twitter sources, caches news, serves the API and reposts to Telegram.
- **news_cache** (variable) `gui_server.py:18`: Global lock-guarded cache of aggregated news data, last-fetched time and per-source status.
- **parse_xml_rss()** (function) `gui_server.py:parse_xml_rss`: Parses RSS/Atom feeds into normalized article dicts, extracting title/link/date/thumbnail.
- **scrape_vulture_html()** (function) `gui_server.py:scrape_vulture_html`: HTML scraper for Vulture article links.
- **extract_title_for_anchor()** (function) `gui_server.py:extract_title_for_anchor`: Derives an article title from an anchor via headings/classes/img alt/text.
- **find_thumbnail_for_anchor()** (function) `gui_server.py:find_thumbnail_for_anchor`: Walks up the DOM from an anchor to find a usable thumbnail image.
- **POST /api/forward-to-telegram** (endpoint) `gui_server.py`: Repost-a-channel endpoint invoked when the UI forwards a channel to Telegram (inferred).
- **scrape_screendaily_html()** (function) `gui_server.py:scrape_screendaily_html`: HTML scraper for Screen Daily with section-based categories.
- **scrape_rt_html()** (function) `gui_server.py:scrape_rt_html`: HTML scraper for Rotten Tomatoes editorial with inline date parsing.
- **scrape_ew_html()** (function) `gui_server.py:scrape_ew_html`: HTML scraper for Entertainment Weekly article links.
- **backfill_avatars()** (function) `frontend/avatar_fetcher.py:backfill_avatars`: Populates missing channel avatars; called by run_offlinefeed.main unless --no-avatars.
- **scrape_telegram_html()** (function) `gui_server.py:scrape_telegram_html`: Scrapes the public t.me widget HTML into posts with text, date and thumbnail.
- **scrape_twitter_syndication()** (function) `gui_server.py:scrape_twitter_syndication`: Parses Twitter syndication __NEXT_DATA__ JSON into tweet entries.
- **resolve_image_url()** (function) `gui_server.py:resolve_image_url`: Normalizes protocol-relative/relative image URLs against a base host; drops data: URIs.
- **extract_img_url()** (function) `gui_server.py:extract_img_url`: Pulls a real image URL from lazy-load attributes/srcset, skipping placeholders.
- **parse_date_to_timestamp()** (function) `gui_server.py:parse_date_to_timestamp`: Best-effort multi-format date string to epoch conversion.
- **GET /api/status** (endpoint) `gui_server.py`: Health endpoint polled by app._backend_alive to confirm the Feed Server is up.
- **GET /api/news** (endpoint) `gui_server.py`: Aggregated news feed endpoint consumed by the bridge models (inferred from the HTTP API contract).
- **Telegram (channels)** (resource): External Telegram destination that channels are reposted to.
- **frontend/avatar_fetcher.py** (file) `frontend/avatar_fetcher.py:1`: Avatar backfill module run at launch; fetches/refreshes channel avatars (referenced from the launcher; body not loaded).

### Config, assets & build (6 nodes)
_Settings, assets and build inputs (ui_settings.json, requirements, PyInstaller spec, logo, launchers)._

- **offline_viewer/assets/ui_settings.json** (config) `offline_viewer/assets/ui_settings.json`: Persisted UI settings (appearance, language, advanced.backend_port, pins, folders, bin). Read across launcher, app, bridge and doctor.
- **requirements.txt** (config) `requirements.txt`: Dependency list (PySide6, requests, feedparser, beautifulsoup4, lxml) verified by the doctor.
- **run.bat** (config) `run.bat`: Windows launcher that calls run_offlinefeed.py.
- **qml/assets/logo.svg** (resource) `frontend/qml/assets/logo.svg`: App logo/window icon; relies on the QtSvg plugin to render.
- **OfflineFeed.spec** (config) `OfflineFeed.spec`: PyInstaller build spec.
- **frontend/gen_assets.py** (file) `frontend/gen_assets.py:1`: Regenerates the SVG icon set + logo (referenced in README; body not loaded).

### Rationale & concepts (8 nodes)
_Rationale/concept nodes captured from docstrings and comments — the design decisions behind the code._

- **Replace opaque 'Code: 1' with real diagnostics** (rationale) `frontend/debug.py:docstring`: The old launcher hid the real failure; debug/doctor/launcher surface the actual traceback and a fix hint.
- **Import QtSvg so icons render** (rationale) `frontend/app.py:QtSvg`: Importing QtSvg loads the qsvg image plugin; without it PySide6 renders SVG sources blank (why icons/logo were invisible).
- **Backend left UNCHANGED, talk over HTTP** (rationale) `frontend/bridge.py:docstring`: The UI speaks to the existing backend only over its local HTTP API so aggregation/Telegram logic never breaks.
- **Defensive networking keeps UI alive** (rationale) `frontend/bridge.py:_get`: Every backend call is defensive: if the backend is unreachable the UI loads empty + a toast instead of crashing.
- **Disable QML disk cache** (rationale) `frontend/app.py:main`: QML_DISABLE_DISK_CACHE=1 prevents cached legacy component conflicts on startup.
- **Suppress backend's old web UI** (rationale) `frontend/app.py:start_backend`: start_backend patches webbrowser.open to a no-op so the legacy backend can't pop the old web UI; the QML UI renders instead.
- **Reader font separate from chat font** (rationale) `frontend/bridge.py:ChatBridge`: The offline-reader font is stored independently so changing one never affects the other.
- **Bin keeps deleted posts recoverable** (rationale) `frontend/bridge.py:ChatBridge`: Full article dicts of deleted posts are kept locally so they survive feed refresh and stay readable.

## Surprising connections

Cross-module / cross-layer edges that aren't obvious from the folder structure, ranked by how unexpected they are.

- **Main.qml/ChatView → telegram** — A UI button (ChatView.onForwardChannelRequested) reaches all the way across the bridge and backend to repost a channel to an external Telegram destination.
- **bridge:ChatBridge → ui_settings** — backend_port lives in ui_settings.json and is re-read independently by app.py, bridge.py, doctor.py and run_offlinefeed.py — the same parsing logic is duplicated in four places instead of being centralized.
- **debug → app + doctor + run_offlinefeed** — debug.py deliberately imports no PySide6, which lets the same module serve both the pre-Qt CLI/launcher world and the GUI — an unusually load-bearing hub spanning two runtimes.
- **app:start_backend → gui_server (start_server/main/run/start/serve)** — The GUI imports the backend and calls whichever entry point exists via getattr fallbacks — a deliberately loose coupling where the real entry point is ambiguous.

## The "why" (rationale captured from the code)

- **Import QtSvg so icons render** — Importing QtSvg loads the qsvg image plugin; without it PySide6 renders SVG sources blank (why icons/logo were invisible). _(explains: frontend/app.py)_
- **Backend left UNCHANGED, talk over HTTP** — The UI speaks to the existing backend only over its local HTTP API so aggregation/Telegram logic never breaks. _(explains: frontend/bridge.py)_
- **Defensive networking keeps UI alive** — Every backend call is defensive: if the backend is unreachable the UI loads empty + a toast instead of crashing. _(explains: _get())_
- **Replace opaque 'Code: 1' with real diagnostics** — The old launcher hid the real failure; debug/doctor/launcher surface the actual traceback and a fix hint. _(explains: _RingBufferHandler, frontend/debug.py, run_diagnostics())_
- **Disable QML disk cache** — QML_DISABLE_DISK_CACHE=1 prevents cached legacy component conflicts on startup. _(explains: main())_
- **Suppress backend's old web UI** — start_backend patches webbrowser.open to a no-op so the legacy backend can't pop the old web UI; the QML UI renders instead. _(explains: start_backend())_
- **Reader font separate from chat font** — The offline-reader font is stored independently so changing one never affects the other. _(explains: ChatBridge)_
- **Bin keeps deleted posts recoverable** — Full article dicts of deleted posts are kept locally so they survive feed refresh and stay readable. _(explains: ChatBridge)_

## Suggested questions

Questions this graph is uniquely positioned to answer:

- How does clicking 'forward' on a channel end up reposting it to Telegram (UI → bridge → backend → Telegram)?
- What exactly happens at startup when PySide6 is missing or the backend port is already busy?
- Where is backend_port resolved, and why is the same logic duplicated across four modules?
- How are article thumbnails extracted differently across RSS, scraped HTML, Telegram and Twitter sources?
- What keeps the desktop UI usable when the Feed Server backend is unreachable?

## Confidence summary

- **EXTRACTED** (read literally from code): 111
- **INFERRED** (deduced from references to files not fully loaded): 23
- **AMBIGUOUS**: 0

> Note: the GitHub API rate limit was hit mid-extraction. The launcher, entry point, diagnostics, bridge models/HTTP layer, the QML root window and the backend scrapers/helpers were read directly (EXTRACTED). The QML child components, `avatar_fetcher.py`, the backend HTTP request handler/endpoints and the Telegram repost path were referenced but not fully loaded, so their edges are marked INFERRED. Re-running extraction on those files later will upgrade them.
