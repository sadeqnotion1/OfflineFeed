---
id: "logo"
label: "qml/assets/logo.svg"
type: "resource"
community: "config"
location: "frontend/qml/assets/logo.svg"
degree: 1
---

# qml/assets/logo.svg

- **Type**: `resource`
- **Community**: `config`
- **Location**: `frontend/qml/assets/logo.svg`
- **Degree**: `1`

## Summary
App logo/window icon; relies on the QtSvg plugin to render.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `references` (*evidence: app.setWindowIcon(QIcon(str(LOGO)))*))