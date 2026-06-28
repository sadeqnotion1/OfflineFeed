---
id: "Theme"
label: "Theme (themes singleton)"
type: "component"
community: "ui"
location: "frontend/qml/themes"
degree: 2
---

# Theme (themes singleton)

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/themes`
- **Degree**: `2`

## Summary
QML singleton holding theme variant, RTL, fonts, accent and wallpaper; kept in sync with ChatBridge via Bindings.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: Binding { target: Theme; value: bridge.theme/rtl/fontFamily/... }*))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `imports` (*evidence: import './themes'; Theme.* used throughout*))