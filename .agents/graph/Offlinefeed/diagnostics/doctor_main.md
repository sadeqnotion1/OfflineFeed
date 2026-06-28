---
id: "doctor:main"
label: "main()"
type: "function"
community: "diagnostics"
location: "frontend/doctor.py:main"
degree: 3
---

# main()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/doctor.py:main`
- **Degree**: `3`

## Summary
Resolves the port from settings, runs diagnostics, prints the report, returns the exit code.

## Outgoing Connections
- [[debug_run_diagnostics|run_diagnostics()]] (type: `calls` (*evidence: report = debug.run_diagnostics(port=port)*))
- [[ui_settings|offline_viewer/assets/ui_settings.json]] (type: `reads` (*evidence: reads advanced.backend_port from ui_settings.json*))

## Incoming Connections
- [[doctor|frontend/doctor.py]] (type: `contains` (*evidence: def main() in doctor.py*))