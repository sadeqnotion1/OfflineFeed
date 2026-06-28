---
id: "debug:install_excepthooks"
label: "install_excepthooks()"
type: "function"
community: "diagnostics"
location: "frontend/debug.py:install_excepthooks"
degree: 2
---

# install_excepthooks()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:install_excepthooks`
- **Degree**: `2`

## Summary
Routes uncaught main-thread and daemon-thread exceptions into the log.

## Outgoing Connections
*None*

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `calls` (*evidence: debug.install_excepthooks()*))
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: def install_excepthooks in debug.py*))