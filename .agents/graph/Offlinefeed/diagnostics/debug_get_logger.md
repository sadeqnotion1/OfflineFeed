---
id: "debug:get_logger"
label: "get_logger()"
type: "function"
community: "diagnostics"
location: "frontend/debug.py:get_logger"
degree: 3
---

# get_logger()

- **Type**: `function`
- **Community**: `diagnostics`
- **Location**: `frontend/debug.py:get_logger`
- **Degree**: `3`

## Summary
Singleton logger writing to console, a rotating file, and the in-memory ring buffer.

## Outgoing Connections
- [[debug_RingBufferHandler|_RingBufferHandler]] (type: `instantiates` (*evidence: logger.addHandler(_ring)*))
- [[log_file|logs/offlinefeed_debug.log]] (type: `writes` (*evidence: RotatingFileHandler(LOG_FILE, ...)*))

## Incoming Connections
- [[debug|frontend/debug.py]] (type: `contains` (*evidence: def get_logger in debug.py*))