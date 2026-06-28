---
id: "SettingsView"
label: "SettingsView"
type: "component"
community: "ui"
location: "frontend/qml/components/SettingsView.qml"
degree: 3
---

# SettingsView

- **Type**: `component`
- **Community**: `ui`
- **Location**: `frontend/qml/components/SettingsView.qml`
- **Degree**: `3`

## Summary
Settings page loaded on demand; binds appearance/language/source settings to the bridge.

## Outgoing Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: Settings page binds appearance/source settings to the bridge*))
- [[bridge_SourcesModel|SourcesModel]] (type: `references` (*evidence: custom sources list shown on Settings*))

## Incoming Connections
- [[Main.qml|frontend/qml/Main.qml]] (type: `instantiates` (*evidence: Loader source: 'components/SettingsView.qml'*))