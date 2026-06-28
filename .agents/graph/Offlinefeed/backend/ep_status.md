---
id: "ep:status"
label: "GET /api/status"
type: "endpoint"
community: "backend"
location: "gui_server.py"
degree: 2
---

# GET /api/status

- **Type**: `endpoint`
- **Community**: `backend`
- **Location**: `gui_server.py`
- **Degree**: `2`

## Summary
Health endpoint polled by app._backend_alive to confirm the Feed Server is up.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_start_backend|start_backend()]] (type: `references` (*evidence: _backend_alive urlopen(get_backend_base()+'/api/status')*))
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: HTTP handler exposes /api/status (polled by app)*))