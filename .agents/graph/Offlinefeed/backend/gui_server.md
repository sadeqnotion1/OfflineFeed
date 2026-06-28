---
id: "gui_server"
label: "gui_server.py"
type: "file"
community: "backend"
location: "gui_server.py:1"
degree: 22
---

# gui_server.py

- **Type**: `file`
- **Community**: `backend`
- **Location**: `gui_server.py:1`
- **Degree**: `22`

## Summary
Local ThreadingHTTPServer (port 8080) that aggregates RSS/HTML/Telegram/Twitter sources, caches news, serves the API and reposts to Telegram.

## Outgoing Connections
- [[telegram|Telegram (channels)]] (type: `writes` (*evidence: README: one-click reposting of channels to Telegram*))
- [[gui_server_news_cache|news_cache]] (type: `contains` (*evidence: news_cache global in gui_server.py*))
- [[ep_status|GET /api/status]] (type: `contains` (*evidence: HTTP handler exposes /api/status (polled by app)*))
- [[ep_news|GET /api/news]] (type: `contains` (*evidence: HTTP handler exposes aggregated news*))
- [[ep_forward|POST /api/forward-to-telegram]] (type: `contains` (*evidence: HTTP handler exposes the Telegram repost action*))
- [[gui_server_parse_xml_rss|parse_xml_rss()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_vulture_html|scrape_vulture_html()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_screendaily_html|scrape_screendaily_html()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_rt_html|scrape_rt_html()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_ew_html|scrape_ew_html()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_telegram_html|scrape_telegram_html()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_scrape_twitter_syndication|scrape_twitter_syndication()]] (type: `contains` (*evidence: scraper defined in gui_server.py*))
- [[gui_server_resolve_image_url|resolve_image_url()]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_extract_img_url|extract_img_url()]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_extract_title_for_anchor|extract_title_for_anchor()]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_find_thumbnail_for_anchor|find_thumbnail_for_anchor()]] (type: `contains` (*evidence: helper defined in gui_server.py*))
- [[gui_server_parse_date_to_timestamp|parse_date_to_timestamp()]] (type: `contains` (*evidence: helper defined in gui_server.py*))

## Incoming Connections
- [[app_start_backend|start_backend()]] (type: `depends_on` (*evidence: import gui_server inside start_backend daemon thread*))
- [[debug_check_backend_module|check_backend_module()]] (type: `references` (*evidence: importlib.util.find_spec('gui_server')*))
- [[debug_probe_backend_import|probe_backend_import()]] (type: `depends_on` (*evidence: subprocess imports gui_server to catch import-time crash*))
- [[bridge_get|_get()]] (type: `depends_on` (*evidence: get_api_base() -> http://127.0.0.1:port served by gui_server*))
- [[bridge_post|_post()]] (type: `depends_on` (*evidence: POST to the gui_server HTTP API*))