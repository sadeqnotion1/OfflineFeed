---
id: "debug"
label: "frontend/debug.py"
type: "file"
community: "diagnostics"
location: "frontend/debug.py:1"
degree: 10
---

# frontend/debug.py

- **Type**: `file`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:1`
- **Degree**: `10`

## Summary
Diagnostics + logging subsystem with no PySide6 dependency: rotating log, ring buffer, excepthooks, and the preflight doctor.

## Outgoing Connections
- [[debug_run_diagnostics|run_diagnostics()]] (type: `contains` (*evidence: def run_diagnostics in debug.py*))
- [[debug_get_logger|get_logger()]] (type: `contains` (*evidence: def get_logger in debug.py*))
- [[debug_install_excepthooks|install_excepthooks()]] (type: `contains` (*evidence: def install_excepthooks in debug.py*))
- [[debug_probe_backend_import|probe_backend_import()]] (type: `contains` (*evidence: def probe_backend_import in debug.py*))
- [[debug_check_backend_module|check_backend_module()]] (type: `contains` (*evidence: def check_backend_module in debug.py*))
- [[debug_RingBufferHandler|_RingBufferHandler]] (type: `contains` (*evidence: class _RingBufferHandler in debug.py*))
- [[why_real_traceback|Replace opaque 'Code: 1' with real diagnostics]] (type: `explains` (*evidence: module docstring: replace guesswork with facts*))

## Incoming Connections
- [[run_offlinefeed|run_offlinefeed.py]] (type: `imports` (*evidence: import debug  (run_offlinefeed.py)*))
- [[app|frontend/app.py]] (type: `imports` (*evidence: import debug as _dbg*))
- [[doctor|frontend/doctor.py]] (type: `imports` (*evidence: import debug (doctor.py)*))