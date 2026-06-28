---
id: "gui_server:scrape_vulture_html"
label: "scrape_vulture_html()"
type: "function"
community: "backend"
location: "gui_server.py:scrape_vulture_html"
degree: 4
---

# scrape_vulture_html()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:scrape_vulture_html`
- **Degree**: `4`

## Summary
HTML scraper for Vulture article links.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_extract_title_for_anchor|extract_title_for_anchor()]] (type: `calls` (*evidence: title = extract_title_for_anchor(a)*))
- [[gui_server_find_thumbnail_for_anchor|find_thumbnail_for_anchor()]] (type: `calls` (*evidence: thumbnail = find_thumbnail_for_anchor(a)*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))