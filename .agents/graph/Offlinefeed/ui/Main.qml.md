---
id: "Main.qml"
label: "frontend/qml/Main.qml"
type: "file"
community: "ui"
location: "frontend/qml/Main.qml:1"
degree: 13
---

# frontend/qml/Main.qml

- **Type**: `file`
- **Community**: `ui`
- **Location**: `frontend/qml/Main.qml:1`
- **Degree**: `13`

## Summary
Frameless root window: 3-pane Telegram layout (rail | chat list | chat view) plus slide-in info panel, reader overlay and toast.

## Outgoing Connections
- [[Theme|Theme (themes singleton)]] (type: `imports` (*evidence: import './themes'; Theme.* used throughout*))
- [[TitleBar|TitleBar]] (type: `instantiates` (*evidence: TitleBar { id: titleBar }*))
- [[FolderRail|FolderRail]] (type: `instantiates` (*evidence: FolderRail { id: rail }*))
- [[ChatList|ChatList]] (type: `instantiates` (*evidence: ChatList { id: chatList }*))
- [[ChatView|ChatView]] (type: `instantiates` (*evidence: ChatView { id: chatView }*))
- [[SearchResultsView|SearchResultsView]] (type: `instantiates` (*evidence: SearchResultsView { ... }*))
- [[InfoPanel|InfoPanel]] (type: `instantiates` (*evidence: InfoPanel { id: infoPanel }*))
- [[ReaderView|ReaderView]] (type: `instantiates` (*evidence: ReaderView { id: reader }*))
- [[ChatContextMenu|ChatContextMenu]] (type: `instantiates` (*evidence: ChatContextMenu { id: ctxMenu }*))
- [[AddToFolderDialog|AddToFolderDialog]] (type: `instantiates` (*evidence: AddToFolderDialog { id: addToFolderDialog }*))
- [[SettingsView|SettingsView]] (type: `instantiates` (*evidence: Loader source: 'components/SettingsView.qml'*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: bridge.theme/rtl/activeTab/currentChannelId + slot calls in Main.qml*))

## Incoming Connections
- [[app_main|main()]] (type: `references` (*evidence: engine.load(QUrl.fromLocalFile(QML_DIR/'Main.qml'))*))