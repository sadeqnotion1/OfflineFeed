---
id: "bridge:SourcesModel"
label: "SourcesModel"
type: "class"
community: "bridge"
location: "frontend/bridge.py:SourcesModel"
degree: 4
---

# SourcesModel

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:SourcesModel`
- **Degree**: `4`

## Summary
List model for custom RSS/news sources shown on the Settings page.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `instantiates` (*evidence: sources_model = SourcesModel()*))
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class SourcesModel*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: ChatBridge.__init__(sources_model: SourcesModel, ...)*))
- [[SettingsView|SettingsView]] (type: `references` (*evidence: custom sources list shown on Settings*))