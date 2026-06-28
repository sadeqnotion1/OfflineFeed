---
id: "gui_server:extract_img_url"
label: "extract_img_url()"
type: "function"
community: "backend"
location: "gui_server.py:extract_img_url"
degree: 2
---

# extract_img_url()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:extract_img_url`
- **Degree**: `2`

## Summary
Pulls a real image URL from lazy-load attributes/srcset, skipping placeholders.

## Outgoing Connections
*None*

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_find_thumbnail_for_anchor|find_thumbnail_for_anchor()]] (type: `calls` (*evidence: val = extract_img_url(img)*))