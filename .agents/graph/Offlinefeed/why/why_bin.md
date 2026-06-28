---
id: "why:bin"
label: "Bin keeps deleted posts recoverable"
type: "rationale"
community: "why"
location: "frontend/bridge.py:ChatBridge"
degree: 1
---

# Bin keeps deleted posts recoverable

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/bridge.py:ChatBridge`
- **Degree**: `1`

## Summary
Full article dicts of deleted posts are kept locally so they survive feed refresh and stay readable.

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `explains` (*evidence: _binned_items keep deleted posts recoverable across refresh*))