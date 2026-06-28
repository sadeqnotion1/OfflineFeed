---
id: "ChatView"
label: "ChatView"
type: "component"
community: "ui"
location: "frontend/qml/components/ChatView.qml"
degree: 4
---

# ChatView

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/ChatView.qml`
- **Degree**: `4`

## Summary
Right conversation pane bound to messageModel; forwards channels and opens the reader.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: onForwardChannelRequested -> bridge.sendChannelToTelegram(id)*))
- [[bridge_MessageModel|MessageModel]] (type: `references` (*evidence: ChatView renders messageModel posts*))
- [[ReaderView|ReaderView]] (type: `calls` (*evidence: onReadArticleRequested -> reader.open(u,t,tx)*))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: ChatView { id: chatView }*))