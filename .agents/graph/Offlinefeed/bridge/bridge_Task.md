---
id: "bridge:_Task"
label: "_Task / QThreadPool"
type: "class"
community: "bridge"
location: "frontend/bridge.py:_Task"
degree: 1
---

# _Task / QThreadPool

- **Type**: `class`
- **Community**: `bridge`
- **Location**: `frontend/bridge.py:_Task`
- **Degree**: `1`

## Summary
QRunnable that runs blocking backend calls off the GUI thread and emits the result via a signal.

## Outgoing Connections
*None*

## Incoming Connections
- [[bridge|frontend/bridge.py]] (type: `contains` (*evidence: class _Task(QRunnable)*))