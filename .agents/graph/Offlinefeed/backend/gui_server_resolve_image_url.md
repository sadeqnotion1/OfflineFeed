---
id: "gui_server:resolve_image_url"
label: "resolve_image_url()"
type: "function"
community: "backend"
location: "gui_server.py:resolve_image_url"
degree: 2
---

# resolve_image_url()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:resolve_image_url`
- **Degree**: `2`

## Summary
Normalizes protocol-relative/relative image URLs against a base host; drops data: URIs.

## Outgoing Connections
*None*

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_parse_xml_rss|parse_xml_rss()]] (type: `calls` (*evidence: thumbnail = resolve_image_url(thumbnail, base_host)*))