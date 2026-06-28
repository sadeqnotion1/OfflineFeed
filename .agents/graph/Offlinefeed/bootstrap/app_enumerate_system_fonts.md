---
id: "app:enumerate_system_fonts"
label: "enumerate_system_fonts()"
type: "function"
community: "bootstrap"
location: "frontend/app.py:enumerate_system_fonts"
degree: 2
---

# enumerate_system_fonts()

- **Type**: `function`
- **Community**: `bootstrap`
- **Location**: `frontend/app.py:enumerate_system_fonts`
- **Degree**: `2`

## Summary
Returns a de-duplicated, sorted list of installed font families for the QML font picker.

## Outgoing Connections
*None*

## Incoming Connections
- [[app|frontend/app.py]] (type: `contains` (*evidence: def enumerate_system_fonts() in app.py*))
- [[app_main|main()]] (type: `calls` (*evidence: system_fonts = enumerate_system_fonts()*))