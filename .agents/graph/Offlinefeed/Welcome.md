# OfflineFeed Knowledge Graph Vault

Welcome to the Obsidian representation of the OfflineFeed codebase knowledge graph.

## Vault Stats
- **Total Nodes/Notes**: 74
- **Total Connections/Edges**: 134
- **Project Repo**: [sadeqnotion1/OfflineFeed](https://github.com/sadeqnotion1/OfflineFeed)
- **Generated At**: 2026-06-19T09:16:05.075279+00:00

---

## Key God Nodes (Most Connected)
These are the central hubs of the codebase. Start exploring here:
- [[gui_server|gui_server.py]] (`file`, degree: 22) — Local ThreadingHTTPServer (port 8080) that aggregates RSS/HTML/Telegram/Twitter sources, caches news, serves the API and...
- [[bridge_ChatBridge|ChatBridge]] (`class`, degree: 19) — Imperative surface QML calls into (slots) and observes (properties/signals); owns settings, models and backend calls.
- [[Main.qml|frontend/qml/Main.qml]] (`file`, degree: 13) — Frameless root window: 3-pane Telegram layout (rail | chat list | chat view) plus slide-in info panel, reader overlay an...
- [[bridge|frontend/bridge.py]] (`file`, degree: 12) — QObject + QAbstractListModel layer that exposes the unchanged backend HTTP API to QML.
- [[app_main|main()]] (`function`, degree: 11) — Creates the QApplication, instantiates the four models + ChatBridge, wires QML context properties and loads Main.qml.
- [[debug|frontend/debug.py]] (`file`, degree: 10) — Diagnostics + logging subsystem with no PySide6 dependency: rotating log, ring buffer, excepthooks, and the preflight do...
- [[app|frontend/app.py]] (`file`, degree: 8) — PySide6 entry point: boots the backend thread, loads fonts, registers bridge+models as QML context properties, loads Mai...
- [[gui_server_news_cache|news_cache]] (`variable`, degree: 8) — Global lock-guarded cache of aggregated news data, last-fetched time and per-source status.

---

## Folders & Communities
The codebase has been divided into the following functional areas:
### [[backend/|Backend]] (20 nodes)
  [[gui_server|gui_server.py]] · [[gui_server_news_cache|news_cache]] · [[gui_server_parse_xml_rss|parse_xml_rss()]] · [[gui_server_scrape_vulture_html|scrape_vulture_html()]] · [[gui_server_extract_title_for_anchor|extract_title_for_anchor()]]
### [[bootstrap/|Bootstrap]] (7 nodes)
  [[app_main|main()]] · [[app|frontend/app.py]] · [[run_offlinefeed_main|main()]] · [[app_start_backend|start_backend()]] · [[run_offlinefeed|run_offlinefeed.py]]
### [[bridge/|Bridge]] (11 nodes)
  [[bridge_ChatBridge|ChatBridge]] · [[bridge|frontend/bridge.py]] · [[bridge_ChatListModel|ChatListModel]] · [[bridge_get|_get()]] · [[bridge_MessageModel|MessageModel]]
### [[config/|Config]] (6 nodes)
  [[ui_settings|offline_viewer/assets/ui_settings.json]] · [[requirements|requirements.txt]] · [[runbat|run.bat]] · [[logo|qml/assets/logo.svg]] · [[spec|OfflineFeed.spec]]
### [[diagnostics/|Diagnostics]] (10 nodes)
  [[debug|frontend/debug.py]] · [[debug_run_diagnostics|run_diagnostics()]] · [[debug_get_logger|get_logger()]] · [[debug_probe_backend_import|probe_backend_import()]] · [[debug_check_backend_module|check_backend_module()]]
### [[ui/|Ui]] (12 nodes)
  [[Main.qml|frontend/qml/Main.qml]] · [[ChatView|ChatView]] · [[ChatList|ChatList]] · [[SettingsView|SettingsView]] · [[Theme|Theme (themes singleton)]]
### [[why/|Why]] (8 nodes)
  [[why_real_traceback|Replace opaque 'Code: 1' with real diagnostics]] · [[why_svg|Import QtSvg so icons render]] · [[why_unchanged_backend|Backend left UNCHANGED, talk over HTTP]] · [[why_defensive_net|Defensive networking keeps UI alive]] · [[why_no_diskcache|Disable QML disk cache]]

---

## Tips for Using this Vault in Obsidian
1. **Graph View**: Open the built-in Graph View in Obsidian (`Ctrl+G`) to see the interactive visual representation of your codebase.
2. **Backlinks**: Toggle the Backlinks pane in Obsidian to see what calls or references the note you are currently viewing.
3. **Frontmatter Search**: You can search notes by metadata, e.g., `type:file` or `community:backend`.