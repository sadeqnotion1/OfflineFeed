---
id: "why:no_diskcache"
label: "Disable QML disk cache"
type: "rationale"
community: "why"
location: "frontend/app.py:main"
degree: 1
---

# Disable QML disk cache

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/app.py:main`
- **Degree**: `1`

## Summary
QML_DISABLE_DISK_CACHE=1 prevents cached legacy component conflicts on startup.

## Outgoing Connections
*None*

## Incoming Connections
- [[app_main|main()]] (type: `explains` (*evidence: os.environ['QML_DISABLE_DISK_CACHE']='1'*))