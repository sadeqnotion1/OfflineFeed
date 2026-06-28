---
id: "app"
label: "frontend/app.py"
type: "file"
community: "bootstrap"
location: "frontend/app.py:1"
degree: 8
---

# frontend/app.py

- **Type**: `file`
- **Community**: `bootstrap`
- **Location**: `frontend/app.py:1`
- **Degree**: `8`

## Summary
PySide6 entry point: boots the backend thread, loads fonts, registers bridge+models as QML context properties, loads Main.qml.

## Outgoing Connections
- [[app_main|main()]] (type: `contains` (*evidence: def main() in app.py*))
- [[app_start_backend|start_backend()]] (type: `contains` (*evidence: def start_backend() in app.py*))
- [[app_enumerate_system_fonts|enumerate_system_fonts()]] (type: `contains` (*evidence: def enumerate_system_fonts() in app.py*))
- [[app_get_backend_port|get_backend_port() [app]]] (type: `contains` (*evidence: def get_backend_port() in app.py*))
- [[bridge|frontend/bridge.py]] (type: `imports` (*evidence: from bridge import ChatBridge, ChatListModel, MessageModel, SourcesModel, SearchResultsModel*))
- [[debug|frontend/debug.py]] (type: `imports` (*evidence: import debug as _dbg*))
- [[why_svg|Import QtSvg so icons render]] (type: `explains` (*evidence: from PySide6 import QtSvg comment about blank SVG icons*))

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `depends_on` (*evidence: subprocess.run([sys.executable, '-m', 'frontend.app'])*))