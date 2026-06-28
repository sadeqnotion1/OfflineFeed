---
id: "why:reader_font"
label: "Reader font separate from chat font"
type: "rationale"
community: "why"
location: "frontend/bridge.py:ChatBridge"
degree: 1
---

# Reader font separate from chat font

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/bridge.py:ChatBridge`
- **Degree**: `1`

## Summary
The offline-reader font is stored independently so changing one never affects the other.

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge_ChatBridge|ChatBridge]] (type: `explains` (*evidence: _readerFontFamily stored separately, falls back to chat font*))