---
id: "gui_server:scrape_twitter_syndication"
label: "scrape_twitter_syndication()"
type: "function"
community: "backend"
location: "gui_server.py:scrape_twitter_syndication"
degree: 2
---

# scrape_twitter_syndication()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `gui_server.py:scrape_twitter_syndication`
- **Degree**: `2`

## Summary
Parses Twitter syndication __NEXT_DATA__ JSON into tweet entries.

## Outgoing Connections
- [[gui_server_news_cache|news_cache]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: scraper defined in gui_server.py*))