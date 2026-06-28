---
id: "ep:news"
label: "GET /api/news"
type: "endpoint"
community: "backend"
location: "gui_server.py"
degree: 2
---

# GET /api/news

- **Type**: `endpoint`
- **Community**: `backend`
- **Location**: `gui_server.py`
- **Degree**: `2`

## Summary
Aggregated news feed endpoint consumed by the bridge models (inferred from the HTTP API contract).

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge_get|_get()]] (type: `reads` (*evidence: GET helper consumes backend news endpoints*))
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: HTTP handler exposes aggregated news*))