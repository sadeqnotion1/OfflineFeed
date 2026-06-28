---
id: "FolderRail"
label: "FolderRail"
type: "component"
community: "ui"
location: "frontend/qml/components/FolderRail.qml"
degree: 2
---

# FolderRail

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/FolderRail.qml`
- **Degree**: `2`

## Summary
Left rail of folder/tab icons; emits tab + settings selection to the bridge.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: onTabSelected -> bridge.setTab(tab)*))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: FolderRail { id: rail }*))