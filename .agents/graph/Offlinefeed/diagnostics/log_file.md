---
id: "log_file"
label: "logs/offlinefeed_debug.log"
type: "resource"
community: "diagnostics"
location: "logs/offlinefeed_debug.log"
degree: 2
---

# logs/offlinefeed_debug.log

- **Type**: `resource`
- **Community**: `diagnostics`
- **Location**: `logs/offlinefeed_debug.log`
- **Degree**: `2`

## Summary
Rotating debug log written by the logger; tailed by the launcher on a non-zero exit.

## Outgoing Connections
*None*

## Incoming Connections
- [[run_offlinefeed_main|main()]] (type: `reads` (*evidence: _tail(debug.LOG_FILE) printed on non-zero exit*))
- [[debug_get_logger|get_logger()]] (type: `writes` (*evidence: RotatingFileHandler(LOG_FILE, ...)*))