---
id: "bridge:_post"
label: "_post()"
type: "function"
community: "bridge"
location: "frontend/bridge.py:_post"
degree: 4
---

# _post()

- **Type**: `function`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:_post`
- **Degree**: `4`

## Summary
Defensive HTTP POST wrapper around the backend API; retries once after re-resolving the port.

## Outgoing Connections
- [[ep_forward|POST /api/forward-to-telegram]] (type: `writes` (*evidence: forward-to-telegram action posts via _post*))
- [[gui_server|gui_server.py]] (type: `depends_on` (*evidence: POST to the gui_server HTTP API*))

## Incoming Connections
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: def _post in bridge.py*))
- [[bridge_ChatBridge|ChatBridge]] (type: `calls` (*evidence: action slots persist through the _post HTTP helper*))