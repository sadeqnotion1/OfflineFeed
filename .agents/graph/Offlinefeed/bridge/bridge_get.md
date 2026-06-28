---
id: "bridge:_get"
label: "_get()"
type: "function"
community: "bridge"
location: "frontend/bridge.py:_get"
degree: 5
---

# _get()

- **Type**: `function`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:_get`
- **Degree**: `5`

## Summary
Defensive HTTP GET wrapper around the backend API; retries once after re-resolving the port.

## Outgoing Connections
- [[ep_news|GET /api/news]] (type: `reads` (*evidence: GET helper consumes backend news endpoints*))
- [[why_defensive_net|Defensive networking keeps UI alive]] (type: `explains` (*evidence: try/except + retry once after reset_backend_port*))
- [[gui_server|gui_server.py]] (type: `depends_on` (*evidence: get_api_base() -> http://127.0.0.1:port served by gui_server*))

## Incoming Connections
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: def _get in bridge.py*))
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: slots load data through the _get HTTP helper*))