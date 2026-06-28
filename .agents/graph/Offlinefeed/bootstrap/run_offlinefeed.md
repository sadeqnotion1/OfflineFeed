---
id: "run_offlinefeed"
label: "run_offlinefeed.py"
type: "file"
community: "bootstrap"
location: "run_offlinefeed.py:1"
degree: 3
---

# run_offlinefeed.py

- **Type**: `file`
- **Community**: `bootstrap`
- **Location**: `run_offlinefeed.py:1`
- **Degree**: `3`

## Summary
Smart launcher: runs diagnostics, backfills avatars, then spawns frontend.app and tails the log on failure.

## Outgoing Connections
- [[debug|frontend/debug.py]] (type: `imports` (*evidence: import debug  (run_offlinefeed.py)*))
- [[run_offlinefeed_main|main()]] (type: `contains` (*evidence: def main() in run_offlinefeed.py*))

## Incoming Connections
- [[runbat|run.bat]] (type: `depends_on` (*evidence: README: double-click run.bat launches run_offlinefeed.py*))