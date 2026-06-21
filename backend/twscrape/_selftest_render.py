#!/usr/bin/env python3
# Offline self-test for render_rss(): no network, no twscrape, no accounts.
# Confirms the shim emits well-formed RSS that an XML parser accepts and that
# the fields OfflineFeed's parse_xml_rss() needs are present.
import sys
from datetime import datetime, timezone
from xml.dom.minidom import parseString

import twscrape_rss_shim as shim

items = [
    {
        "id": "2068370225049854456",
        "text": "Breaking: something just happened.\nSecond line.",
        "url": "https://x.com/TheAthletic/status/2068370225049854456",
        "date": datetime(2026, 6, 20, 16, 27, 44, tzinfo=timezone.utc),
        "thumb": "https://pbs.twimg.com/media/abc.jpg",
    },
    {
        "id": "2068369048937603128",
        "text": "A tweet with an ampersand & < angle > brackets to test escaping.",
        "url": "https://x.com/TheAthletic/status/2068369048937603128",
        "date": datetime(2026, 6, 20, 16, 23, 4, tzinfo=timezone.utc),
        "thumb": None,
    },
]

xml = shim.render_rss("TheAthletic", items)
dom = parseString(xml)  # raises if malformed -> test fails

assert dom.getElementsByTagName("item").length == 2, "expected 2 items"
links = [n.firstChild.data for n in dom.getElementsByTagName("link")]
assert "https://x.com/TheAthletic/status/2068370225049854456" in links
assert all(dom.getElementsByTagName(t).length >= 2 for t in ("title", "pubDate", "guid"))
# Verify newest-first ordering is preserved by render order.
item_links = [
    it.getElementsByTagName("link")[0].firstChild.data
    for it in dom.getElementsByTagName("item")
]
assert item_links[0].endswith("2068370225049854456")

print("PASS: render_rss produces valid, well-formed RSS with required fields.")
print("---- sample output (first 800 chars) ----")
print(xml[:800])
sys.exit(0)
