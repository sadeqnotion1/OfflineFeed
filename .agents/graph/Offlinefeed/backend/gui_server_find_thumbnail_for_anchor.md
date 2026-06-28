---
id: "gui_server:find_thumbnail_for_anchor"
label: "find_thumbnail_for_anchor()"
type: "function"
community: "backend"
location: "gui_server.py:find_thumbnail_for_anchor"
degree: 4
---

# find_thumbnail_for_anchor()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:find_thumbnail_for_anchor`
- **Degree**: `4`

## Summary
Walks up the DOM from an anchor to find a usable thumbnail image.

## Outgoing Connections
- [[gui_server_extract_img_url|extract_img_url()]] (type: `calls` (*evidence: val = extract_img_url(img)*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_scrape_vulture_html|scrape_vulture_html()]] (type: `calls` (*evidence: thumbnail = find_thumbnail_for_anchor(a)*))
- [[gui_server_scrape_rt_html|scrape_rt_html()]] (type: `calls` (*evidence: thumbnail = find_thumbnail_for_anchor(a)*))