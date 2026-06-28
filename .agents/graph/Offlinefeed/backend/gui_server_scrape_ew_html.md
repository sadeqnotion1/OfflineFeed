---
id: "gui_server:scrape_ew_html"
label: "scrape_ew_html()"
type: "function"
community: "backend"
location: "gui_server.py:scrape_ew_html"
degree: 3
---

# scrape_ew_html()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:scrape_ew_html`
- **Degree**: `3`

## Summary
HTML scraper for Entertainment Weekly article links.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_extract_title_for_anchor|extract_title_for_anchor()]] (type: `calls` (*evidence: title = extract_title_for_anchor(a)*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))