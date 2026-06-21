# OfflineFeed

A local, offline-first feed reader. The repository root is intentionally minimal:

```
backend/     # all Python, the offline_viewer/, tools/, twscrape/, docs/, and config
frontend/    # the desktop GUI app (PySide/QML)
run.bat      # Windows launcher
run.sh       # macOS / Linux launcher
README.md    # this file
.gitignore
```

## Run

```bash
# Windows
run.bat

# macOS / Linux
./run.sh
```

Both wrappers just call `backend/run_offlinefeed.py`, which launches the backend
server and the `frontend` GUI together.

## Nitter (optional, for Twitter/X sources)

The nitter stack lives under `backend/` now, so point compose at it explicitly:

```bash
docker compose -f backend/docker-compose.yml up -d
```

## Layout notes

- `backend/run_offlinefeed.py` is the real entry point.
- `backend/gui_server.py` serves `backend/offline_viewer/` on `127.0.0.1:8080`.
- `frontend/app.py` is the GUI; it imports backend modules via `backend/` on
  `sys.path` and talks to the server over HTTP.
- History of this cleanup is in `backend/docs/CHANGELOG.md`.
