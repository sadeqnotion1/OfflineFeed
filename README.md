<div align="center">

<img src="frontend/qml/assets/logo.svg" width="96" alt="OfflineFeed logo" />

# OfflineFeed

**A native desktop news / RSS aggregator that reads feeds offline and reposts them to Telegram channels.**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-PySide6%20%2F%20QML-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![Telegram](https://img.shields.io/badge/Reposts%20to-Telegram-26A5E4?logo=telegram&logoColor=white)

</div>

---

## Overview

OfflineFeed pulls articles from your RSS / news sources, stores them for offline
reading, and lets you forward whole channels to Telegram. The interface is a
Telegram-Desktop-style three-pane layout built with PySide6 + QML, backed by a
local Python HTTP server.

## Running

```
run.bat        # Windows
./run.sh       # macOS / Linux
```

Both wrappers simply call `python backend/run_offlinefeed.py`, which runs a
health check first and prints the real error if startup fails. The repo root is
intentionally Python-free; all backend code lives under `backend/`.

## Diagnostics

If the app will not start:

```
python -m frontend.doctor
```

Logs are written to `logs/offlinefeed_debug.log`.

## Architecture

| Layer | Technology | Location |
| --- | --- | --- |
| Desktop UI | PySide6 + QML | `frontend/qml/` |
| Bridge (UI to backend) | Python QObject slots / signals | `frontend/bridge.py` |
| App entry / bootstrap | Python | `frontend/app.py` |
| Feed Server (HTTP API, port 8080) | Python | `backend/gui_server.py` |
| Smart launcher | Python | `backend/run_offlinefeed.py` |
| Offline web viewer + assets | HTML / JS + JSON | `backend/offline_viewer/` |
| Diagnostics | Python | `frontend/debug.py`, `frontend/doctor.py` |

## Project structure

```
OfflineFeed/
  run.bat                  Windows launcher
  run.sh                   macOS / Linux launcher
  docker-compose.yml
  nitter.conf
  backend/
    run_offlinefeed.py     smart launcher
    gui_server.py          Feed Server (HTTP API, port 8080)
    feed_store.py          durable live-feed snapshot
    media_cache.py         in-article image cache
    cache_retention.py     cached-post archiver
    offline_viewer/        web viewer + assets (served by the backend)
    tools/                 icon importer + helpers
    twscrape/              optional X -> RSS shim (port 8081)
  frontend/
    app.py                 entry point
    bridge.py              UI <-> backend bridge
    debug.py               diagnostics + logging
    doctor.py              python -m frontend.doctor
    gen_assets.py          regenerates SVG icons + logo
    qml/                   QML UI and assets
  docs/
```

## Requirements

- Python 3.9 or newer
- The packages in `requirements.txt` (PySide6, requests, feedparser,
  beautifulsoup4, lxml)
