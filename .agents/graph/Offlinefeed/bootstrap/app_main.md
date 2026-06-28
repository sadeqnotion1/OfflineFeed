---
id: "app:main"
label: "main()"
type: "function"
community: "bootstrap"
location: "frontend/app.py:main"
degree: 11
---

# main()

- **Type**: `function`
- **Community**: `bootstrap`
- **Location**: `frontend/app.py:main`
- **Degree**: `11`

## Summary
Creates the QApplication, instantiates the four models + ChatBridge, wires QML context properties and loads Main.qml.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `instantiates` (*evidence: bridge = ChatBridge(chat_model, message_model, sources_model, ...)*))
- [[bridge_ChatListModel|ChatListModel]] (type: `instantiates` (*evidence: chat_model = ChatListModel()*))
- [[bridge_MessageModel|MessageModel]] (type: `instantiates` (*evidence: message_model = MessageModel()*))
- [[bridge_SourcesModel|SourcesModel]] (type: `instantiates` (*evidence: sources_model = SourcesModel()*))
- [[bridge_SearchResultsModel|SearchResultsModel]] (type: `instantiates` (*evidence: search_results_model = SearchResultsModel()*))
- [[app_enumerate_system_fonts|enumerate_system_fonts()]] (type: `calls` (*evidence: system_fonts = enumerate_system_fonts()*))
- [[app_start_backend|start_backend()]] (type: `calls` (*evidence: start_backend()*))
- [[Main.qml|frontend/qml/Main.qml]] (type: `references` (*evidence: engine.load(QUrl.fromLocalFile(QML_DIR/'Main.qml'))*))
- [[why_no_diskcache|Disable QML disk cache]] (type: `explains` (*evidence: os.environ['QML_DISABLE_DISK_CACHE']='1'*))
- [[logo|qml/assets/logo.svg]] (type: `references` (*evidence: app.setWindowIcon(QIcon(str(LOGO)))*))

## Incoming Connections
- [[app|frontend/app.py]] (type: `contains` (*evidence: def main() in app.py*))