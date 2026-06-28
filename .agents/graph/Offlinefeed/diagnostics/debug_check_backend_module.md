---
id: "debug:check_backend_module"
label: "check_backend_module()"
type: "function"
community: "diagnostics"
location: "frontend/debug.py:check_backend_module"
degree: 3
---

# check_backend_module()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:check_backend_module`
- **Degree**: `3`

## Summary
Verifies gui_server is resolvable on sys.path the same way app.py searches.

## Outgoing Connections
- [[gui_server|gui_server.py]] (type: `references` (*evidence: importlib.util.find_spec('gui_server')*))

## Incoming Connections
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: def check_backend_module in debug.py*))
- [[debug_run_diagnostics|run_diagnostics()]] (type: `calls` (*evidence: backend = check_backend_module(...)*))