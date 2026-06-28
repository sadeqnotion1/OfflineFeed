---
id: "debug:_RingBufferHandler"
label: "_RingBufferHandler"
type: "class"
community: "diagnostics"
location: "frontend/debug.py:_RingBufferHandler"
degree: 3
---

# _RingBufferHandler

- **Type**: `class`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:_RingBufferHandler`
- **Degree**: `3`

## Summary
Logging handler that keeps the most recent records in memory for the in-app System Logs panel.

## Outgoing Connections
- [[why_real_traceback|Replace opaque 'Code: 1' with real diagnostics]] (type: `explains` (*evidence: ring buffer feeds in-app System Logs even when backend never came up*))

## Incoming Connections
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: class _RingBufferHandler in debug.py*))
- [[debug_get_logger|get_logger()]] (type: `instantiates` (*evidence: logger.addHandler(_ring)*))