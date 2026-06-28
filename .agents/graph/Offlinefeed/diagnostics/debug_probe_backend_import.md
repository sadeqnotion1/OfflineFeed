---
id: "debug:probe_backend_import"
label: "probe_backend_import()"
type: "function"
community: "diagnostics"
location: "frontend/debug.py:probe_backend_import"
degree: 3
---

# probe_backend_import()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:probe_backend_import`
- **Degree**: `3`

## Summary
Imports gui_server in a clean subprocess to surface the real import-time traceback behind 'Code: 1'.

## Outgoing Connections
- [[gui_server|gui_server.py]] (type: `depends_on` (*evidence: subprocess imports gui_server to catch import-time crash*))

## Incoming Connections
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: def probe_backend_import in debug.py*))
- [[debug_run_diagnostics|run_diagnostics()]] (type: `calls` (*evidence: checks.append(probe_backend_import(...))*))