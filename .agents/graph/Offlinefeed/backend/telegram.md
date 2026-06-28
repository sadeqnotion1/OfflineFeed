---
id: "telegram"
label: "Telegram (channels)"
type: "resource"
community: "backend"
degree: 2
---

# Telegram (channels)

- **Type**: `resource`
- **Community**: `backend`
- **Degree**: `2`

## Summary
External Telegram destination that channels are reposted to.

## Outgoing Connections
*None*

## Incoming Connections
- [[ep_forward|POST /api/forward-to-telegram]] (type: `depends_on` (*evidence: backend reposts the channel to Telegram*))
- [[gui_server|gui_server.py]] (type: `writes` (*evidence: README: one-click reposting of channels to Telegram*))