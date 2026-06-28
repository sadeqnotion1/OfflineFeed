---
id: "why:no_oldui"
label: "Suppress backend's old web UI"
type: "rationale"
community: "why"
location: "frontend/app.py:start_backend"
degree: 1
---

# Suppress backend's old web UI

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/app.py:start_backend`
- **Degree**: `1`

## Summary
start_backend patches webbrowser.open to a no-op so the legacy backend can't pop the old web UI; the QML UI renders instead.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_start_backend|start_backend()]] (type: `explains` (*evidence: webbrowser.open = lambda *a, **k: True before importing gui_server*))