---
id: "avatar_fetcher"
label: "frontend/avatar_fetcher.py"
type: "file"
community: "backend"
location: "frontend/avatar_fetcher.py:1"
degree: 1
---

# frontend/avatar_fetcher.py

- **Type**: `file`
- **Community**: `backend`
- **Location**: `frontend/avatar_fetcher.py:1`
- **Degree**: `1`

## Summary
Avatar backfill module run at launch; fetches/refreshes channel avatars (referenced from the launcher; body not loaded).

## Outgoing Connections
- [[avatar_fetcher_backfill_avatars|backfill_avatars()]] (type: `contains` (*evidence: imported symbol backfill_avatars*))

## Incoming Connections
*None*