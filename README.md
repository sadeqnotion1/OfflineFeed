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

OfflineFeed pulls articles from your RSS / news sources, stores them for offline reading, and lets you forward whole channels to Telegram. The interface is a TelegramDesktopstyle threepane layout built with PySide6 + QML, backed by a local Python HTTP server.

## Features

- Telegramstyle threepane UI (folder rail, chat list, conversation) with a slidein info panel
- Offline article reader with graceful fallback when a page can't be scraped
- Light and dark themes, custom accent color, and a customizable chat wallpaper
- Full RTL / Persian support
- Oneclick reposting of channels to Telegram
- Builtin diagnostics (doctor) and an inapp System Logs panel

## Architecture

| Layer | Technology | Location |
| --- | --- | --- |
| Desktop UI | PySide6 + QML | `frontend/qml/` |
| Bridge (UI to backend) | Python QObject slots / signals | `frontend/bridge.py` |
| App entry / bootstrap | Python | `frontend/app.py` |
| Feed Server (HTTP API, port 8080) | Python | `gui_server.py` |
| Diagnostics | Python | `frontend/debug.py`, `frontend/doctor.py` |

## Requirements

- Windows with Python 3.9 or newer
- The packages in `requirements.txt` (PySide6, requests, feedparser, beautifulsoup4, lxml)
- The backend `gui_server.py` present in the project root or in `frontend/`

## Installation

```

cd /d E:ProjectsOfflineFeedOfflineFeed_fixed

py -3.9 -m pip install -r requirements.txt

```

## Running

```

python run_[offlinefeed.py](http://offlinefeed.py)

```

Or doubleclick `run.bat`. The launcher runs a health check first and prints the real error if startup fails.

## Diagnostics

If the app will not start, run:

```

python -m [frontend.doctor](http://frontend.doctor)

```

It prints a PASS / WARN / FAIL line for the Python version, every dependency, the backend port, and the backend module  including the real traceback behind a "Code: 1" exit. See `DEBUG.md` for details. Logs are written to `logs/offlinefeed_debug.log`.

## Project structure

```

OfflineFeed/

frontend/

[app.py](http://app.py)            entry point

[bridge.py](http://bridge.py)         UI to backend bridge

[debug.py](http://debug.py)          diagnostics + logging

[doctor.py](http://doctor.py)         python -m [frontend.doctor](http://frontend.doctor)

gen_[assets.py](http://assets.py)     regenerates SVG icons + logo

qml/              QML UI and assets

gui_[server.py](http://server.py)       backend Feed Server (copy from your original project)

run_[offlinefeed.py](http://offlinefeed.py)  smart launcher

run.bat             Windows launcher

requirements.txt

[DEBUG.md](http://DEBUG.md)

OfflineFeed.spec    PyInstaller build spec

```

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Feed Server exited ... Code: 1` | a dependency or the backend is missing | run `python -m frontend.doctor` |
| `No module named 'feedparser'` | dependency not installed | `pip install -r requirements.txt` |
| `Backend module 'gui_server' Not found` | backend file missing | copy `gui_server.py` into the project |
| Icons or logo appear blank | Qt SVG plugin not loaded | reinstall PySide6 fully (the app imports QtSvg) |
