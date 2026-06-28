---
id: "ep:forward"
label: "POST /api/forward-to-telegram"
type: "endpoint"
community: "backend"
location: "gui_server.py"
degree: 4
---

# POST /api/forward-to-telegram

- **Type**: `endpoint`
- **Community**: `backend`
- **Location**: `gui_server.py`
- **Degree**: `4`

## Summary
Repost-a-channel endpoint invoked when the UI forwards a channel to Telegram (inferred).

## Outgoing Connections
- [[telegram|Telegram (channels)]] (type: `depends_on` (*evidence: backend reposts the channel to Telegram*))

## Incoming Connections
- [[bridge_post|_post()]] (type: `writes` (*evidence: forward-to-telegram action posts via _post*))
- [[bridge_ChatBridge|ChatBridge]] (type: `references` (*evidence: sendChannelToTelegram slot triggers the backend repost*))
- [[gui_server|gui_server.py]] (type: `contains` (*evidence: HTTP handler exposes the Telegram repost action*))