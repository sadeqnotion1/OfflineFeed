---
id: "avatar_fetcher:backfill_avatars"
label: "backfill_avatars()"
type: "function"
community: "backend"
location: "frontend/avatar_fetcher.py:backfill_avatars"
degree: 3
---

# backfill_avatars()

- **Type**: `function`
- **Community**: `backend`
- **Location**: `frontend/avatar_fetcher.py:backfill_avatars`
- **Degree**: `3`

## Summary
Populates missing channel avatars; called by run_offlinefeed.main unless --no-avatars.

## Outgoing Connections
- [[bridge_ChatListModel|ChatListModel]] (type: `references` (*evidence: avatars backfilled are shown via ChatListModel avatarPath*))

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `calls` (*evidence: from frontend.avatar_fetcher import backfill_avatars; backfill_avatars(...)*))
- [[avatar_fetcher|frontend/avatar_fetcher.py]] (type: `contains` (*evidence: imported symbol backfill_avatars*))