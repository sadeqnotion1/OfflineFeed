---
id: "gui_server:parse_xml_rss"
label: "parse_xml_rss()"
type: "function"
community: "backend"
location: "gui_server.py:parse_xml_rss"
degree: 4
---

# parse_xml_rss()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:parse_xml_rss`
- **Degree**: `4`

## Summary
Parses RSS/Atom feeds into normalized article dicts, extracting title/link/date/thumbnail.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_resolve_image_url|resolve_image_url()]] (type: `calls` (*evidence: thumbnail = resolve_image_url(thumbnail, base_host)*))
- [[gui_server_parse_date_to_timestamp|parse_date_to_timestamp()]] (type: `calls` (*evidence: 'timestamp': parse_date_to_timestamp(pub_str)*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))