---
id: "why:unchanged_backend"
label: "Backend left UNCHANGED, talk over HTTP"
type: "rationale"
community: "why"
location: "frontend/bridge.py:docstring"
degree: 1
---

# Backend left UNCHANGED, talk over HTTP

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/bridge.py:docstring`
- **Degree**: `1`

## Summary
The UI speaks to the existing backend only over its local HTTP API so aggregation/Telegram logic never breaks.

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge|frontend/bridge.py]] (type: `explains` (*evidence: docstring: backend left UNCHANGED, talk over HTTP*))