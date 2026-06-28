---
id: "why:real_traceback"
label: "Replace opaque 'Code: 1' with real diagnostics"
type: "rationale"
community: "why"
location: "frontend/debug.py:docstring"
degree: 3
---

# Replace opaque 'Code: 1' with real diagnostics

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/debug.py:docstring`
- **Degree**: `3`

## Summary
The old launcher hid the real failure; debug/doctor/launcher surface the actual traceback and a fix hint.

## Outgoing Connections
*None*

## Incoming Connections
- [[debug_RingBufferHandler|_RingBufferHandler]] (type: `explains` (*evidence: ring buffer feeds in-app System Logs even when backend never came up*))
- [[debug|frontend/debug.py]] (type: `explains` (*evidence: module docstring: replace guesswork with facts*))
- [[debug_run_diagnostics|run_diagnostics()]] (type: `explains` (*evidence: probe surfaces the real reason for code 1*))