---
id: "gui_server:news_cache"
label: "news_cache"
type: "variable"
community: "backend"
location: "gui_server.py:18"
degree: 8
---

# news_cache

- **Type**: `variable`
- **Community**: `backend`
- **Location**: `gui_server.py:18`
- **Degree**: `8`

## Summary
Global lock-guarded cache of aggregated news data, last-fetched time and per-source status.

## Outgoing Connections
*None*

## Incoming Connections
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: news_cache global in gui_server.py*))
- [[gui_server_parse_xml_rss|parse_xml_rss()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_vulture_html|scrape_vulture_html()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_screendaily_html|scrape_screendaily_html()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_rt_html|scrape_rt_html()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_ew_html|scrape_ew_html()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_telegram_html|scrape_telegram_html()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))
- [[gui_server_scrape_twitter_syndication|scrape_twitter_syndication()]] (type: `writes` (*evidence: scraped items aggregated into news_cache*))