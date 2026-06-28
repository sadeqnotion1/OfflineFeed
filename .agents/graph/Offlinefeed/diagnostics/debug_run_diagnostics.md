---
id: "debug:run_diagnostics"
label: "run_diagnostics()"
type: "function"
community: "diagnostics"
location: "frontend/debug.py:run_diagnostics"
degree: 7
---

# run_diagnostics()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:run_diagnostics`
- **Degree**: `7`

## Summary
Runs all preflight checks and returns a structured PASS/WARN/FAIL report.

## Outgoing Connections
- [[debug_check_backend_module|check_backend_module()]] (type: `calls` (*evidence: backend = check_backend_module(...)*))
- [[debug_probe_backend_import|probe_backend_import()]] (type: `calls` (*evidence: checks.append(probe_backend_import(...))*))
- [[requirements|requirements.txt]] (type: `reads` (*evidence: req_path = REPO_ROOT/'requirements.txt'; check_requirements(req_path)*))
- [[why_real_traceback|Replace opaque 'Code: 1' with real diagnostics]] (type: `explains` (*evidence: probe surfaces the real reason for code 1*))

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `calls` (*evidence: report = debug.run_diagnostics(port=port)*))
- [[doctor_main|main()]] (type: `calls` (*evidence: report = debug.run_diagnostics(port=port)*))
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: def run_diagnostics in debug.py*))