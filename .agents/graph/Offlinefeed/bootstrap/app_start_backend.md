---
id: "app:start_backend"
label: "start_backend()"
type: "function"
community: "bootstrap"
location: "frontend/app.py:start_backend"
degree: 5
---

# start_backend()

- **Type**: `function`
- **Community**: `bootstrap`
- **Location**: `frontend/app.py:start_backend`
- **Degree**: `5`

## Summary
Imports gui_server in a daemon thread and calls the first available entry point (start_server/main/run/start/serve).

## Outgoing Connections
- [[gui_server|gui_server.py]] (type: `depends_on` (*evidence: import gui_server inside start_backend daemon thread*))
- [[why_no_oldui|Suppress backend's old web UI]] (type: `explains` (*evidence: webbrowser.open = lambda *a, **k: True before importing gui_server*))
- [[ep_status|GET /api/status]] (type: `references` (*evidence: _backend_alive urlopen(get_backend_base()+'/api/status')*))

## Incoming Connections
- [[app|frontend/app.py]] (type: `contains` (*evidence: def start_backend() in app.py*))
- [[app_main|main()]] (type: `calls` (*evidence: start_backend()*))