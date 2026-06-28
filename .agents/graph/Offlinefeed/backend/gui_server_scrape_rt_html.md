---
id: "gui_server:scrape_rt_html"
label: "scrape_rt_html()"
type: "function"
community: "backend"
location: "gui_server.py:scrape_rt_html"
degree: 3
---

# scrape_rt_html()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:scrape_rt_html`
- **Degree**: `3`

## Summary
HTML scraper for Rotten Tomatoes editorial with inline date parsing.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_find_thumbnail_for_anchor|find_thumbnail_for_anchor()]] (type: `calls` (*evidence: thumbnail = find_thumbnail_for_anchor(a)*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))