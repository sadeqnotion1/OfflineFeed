---
id: "ChatList"
label: "ChatList"
type: "component"
community: "ui"
location: "frontend/qml/components/ChatList.qml"
degree: 3
---

# ChatList

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/ChatList.qml`
- **Degree**: `3`

## Summary
Middle channel list bound to chatModel; opens chats and raises the context menu.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: onOpenChat -> bridge.openChat(id)*))
- [[bridge_ChatListModel|ChatListModel]] (type: `references` (*evidence: ChatList is bound to chatModel exposed from bridge*))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: ChatList { id: chatList }*))