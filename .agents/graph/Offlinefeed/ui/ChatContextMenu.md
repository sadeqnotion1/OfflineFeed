---
id: "ChatContextMenu"
label: "ChatContextMenu"
type: "component"
community: "ui"
location: "frontend/qml/components/ChatContextMenu.qml"
degree: 2
---

# ChatContextMenu

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/ChatContextMenu.qml`
- **Degree**: `2`

## Summary
Per-channel context menu (pin/mute/archive/delete/mark unread/add to folder).

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: onTogglePin/Mute/Archive/Delete -> bridge.**))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: ChatContextMenu { id: ctxMenu }*))