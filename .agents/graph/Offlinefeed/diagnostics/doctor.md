---
id: "doctor"
label: "frontend/doctor.py"
type: "file"
community: "diagnostics"
location: "frontend/doctor.py:1"
degree: 2
---

# frontend/doctor.py

- **Type**: `file`
- **Community**: `diagnostics`
- **Location**: `frontend/doctor.py:1`
- **Degree**: `2`

## Summary
One-command CLI health check (python -m frontend.doctor) that wraps debug.run_diagnostics and exits 0/1.

## Outgoing Connections
- [[debug|frontend/debug.py]] (type: `imports` (*evidence: import debug (doctor.py)*))
- [[doctor_main|main()]] (type: `contains` (*evidence: def main() in doctor.py*))

## Incoming Connections
*None*