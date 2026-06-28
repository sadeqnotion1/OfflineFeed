---
id: "gui_server:scrape_telegram_html"
label: "scrape_telegram_html()"
type: "function"
community: "backend"
location: "gui_server.py:scrape_telegram_html"
degree: 2
---

# scrape_telegram_html()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:scrape_telegram_html`
- **Degree**: `2`

## Summary
Scrapes the public t.me widget HTML into posts with text, date and thumbnail.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))