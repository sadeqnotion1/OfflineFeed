---
id: "why:svg"
label: "Import QtSvg so icons render"
type: "rationale"
community: "why"
location: "frontend/app.py:QtSvg"
degree: 1
---

# Import QtSvg so icons render

- **Type**: `rationale`
- **Community**: `why`
- **Location**: `frontend/app.py:QtSvg`
- **Degree**: `1`

## Summary
Importing QtSvg loads the qsvg image plugin; without it PySide6 renders SVG sources blank (why icons/logo were invisible).

## Outgoing Connections
*None*

## Incoming Connections
- [[app|frontend/app.py]] (type: `explains` (*evidence: from PySide6 import QtSvg comment about blank SVG icons*))