---
id: "bridge"
label: "frontend/bridge.py"
type: "file"
community: "bridge"
location: "frontend/bridge.py:1"
degree: 12
---

# frontend/bridge.py

- **Type**: `file`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:1`
- **Degree**: `12`

## Summary
QObject + QAbstractListModel layer that exposes the unchanged backend HTTP API to QML.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `contains` (*evidence: class ChatBridge in bridge.py*))
- [[bridge_ChatListModel|ChatListModel]] (type: `contains` (*evidence: class ChatListModel*))
- [[bridge_MessageModel|MessageModel]] (type: `contains` (*evidence: class MessageModel*))
- [[bridge_SourcesModel|SourcesModel]] (type: `contains` (*evidence: class SourcesModel*))
- [[bridge_SearchResultsModel|SearchResultsModel]] (type: `contains` (*evidence: class SearchResultsModel*))
- [[bridge_Task|_Task / QThreadPool]] (type: `contains` (*evidence: class _Task(QRunnable)*))
- [[bridge_get|_get()]] (type: `contains` (*evidence: def _get in bridge.py*))
- [[bridge_post|_post()]] (type: `contains` (*evidence: def _post in bridge.py*))
- [[bridge_get_backend_port|get_backend_port() [bridge]]] (type: `contains` (*evidence: def get_backend_port in bridge.py*))
- [[bridge_highlight_text|highlight_text()]] (type: `contains` (*evidence: def highlight_text in bridge.py*))
- [[why_unchanged_backend|Backend left UNCHANGED, talk over HTTP]] (type: `explains` (*evidence: docstring: backend left UNCHANGED, talk over HTTP*))

## Incoming Connections
- [[app|frontend/app.py]] (type: `imports` (*evidence: from bridge import ChatBridge, ChatListModel, MessageModel, SourcesModel, SearchResultsModel*))