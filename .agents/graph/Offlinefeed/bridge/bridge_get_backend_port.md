---
id: "bridge:get_backend_port"
label: "get_backend_port() [bridge]"
type: "function"
community: "bridge"
location: "frontend/bridge.py:get_backend_port"
degree: 2
---

# get_backend_port() [bridge]

- **Type**: `function`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:get_backend_port`
- **Degree**: `2`

## Summary
Caches and returns backend_port from ui_settings.json, defaulting to 8080.

## Outgoing Connections
- [[ui_settings|offline_viewer/assets/ui_settings.json]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))

## Incoming Connections
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: def get_backend_port in bridge.py*))