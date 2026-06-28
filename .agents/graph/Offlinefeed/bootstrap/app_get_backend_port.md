---
id: "app:get_backend_port"
label: "get_backend_port() [app]"
type: "function"
community: "bootstrap"
location: "frontend/app.py:get_backend_port"
degree: 2
---

# get_backend_port() [app]

- **Type**: `function`
- **Community**: `bootstrap`
- **Location**: `frontend/app.py:get_backend_port`
- **Degree**: `2`

## Summary
Reads backend_port from ui_settings.json, defaulting to 8080.

## Outgoing Connections
- [[ui_settings|offline_viewer/assets/ui_settings.json]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))

## Incoming Connections
- [[app|frontend/app.py]] (type: `contains` (*evidence: def get_backend_port() in app.py*))