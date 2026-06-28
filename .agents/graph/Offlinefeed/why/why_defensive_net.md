---
id: "why:defensive_net"
label: "Defensive networking keeps UI alive"
type: "rationale"
community: "why"
location: "frontend/bridge.py:_get"
degree: 1
---

# Defensive networking keeps UI alive

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/bridge.py:_get`
- **Degree**: `1`

## Summary
Every backend call is defensive: if the backend is unreachable the UI loads empty + a toast instead of crashing.

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge_get|_get()]] (type: `explains` (*evidence: try/except + retry once after reset_backend_port*))