# STATE — where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** —
> tell me and I fix the brain. Repo: https://github.com/sadeqnotion1/OfflineFeed

**Status (one-liner):** Working app. Brain just installed + roadmap captured from the maintainer's 23-item bug/feature list. Next up: **M1 — Window chrome & theme foundation**.

| Part | Status | Notes |
|---|---|---|
| App boots | ✅ | `run.bat` / `run.sh` → `python backend/run_offlinefeed.py` (doctor → launch). Logs in `logs/offlinefeed_debug.log`. |
| Backend (Feed Server) | ✅ | `backend/gui_server.py` on 127.0.0.1:8080. Fetch + dedupe + cache + async thumbnails + 14-day retention. |
| Frontend (desktop UI) | ✅ | PySide6 + QML, three-pane Telegram-style. `frontend/app.py`, `frontend/bridge.py`, `frontend/qml/`. |
| X / Twitter | ✅ (flaky) | twscrape RSS shim at 127.0.0.1:8081 (`backend/twscrape/`). Some high-volume handles go stale — see R9.1. |
| Offline reader | ✅ | `backend/offline_reader.py` renders deep-link `?reader=...`. Too plain — see R8.1. |
| Knowledge graph (`.agents/graph/`) | ✅ | Full 74-node Graphify graph included. Standard schema and renderer validated. |
| Brain (`.agents/brain/`) | ✅ | This system. |
| M1 Window chrome & theme | ✅ | True rounded frameless shell, cyberpunk Tinted theme, card radius, folder rail, distinct close glyph |
| M2 Settings IA & consistency | ⬜ | **← NEXT** |
| M3–M10 | ⬜ | See ROADMAP.md |

> Legend: ✅ done · 🟦 in progress · ⬜ not started · ⚠️ blocked. Mark the active task with **← NEXT**.

## Open decisions / questions waiting on you
- **Milestone ordering.** Current order is visual-foundation → settings → icons → image correctness → channel info → telegram → copy → reader → backend → loading. Re-order anytime in ROADMAP.md if your priority differs (e.g. R4.1 thumbnails or R10.1 streaming may be more urgent than chrome).
- **R5.1 storage.** Where should per-channel `telegram_group` + `topic` live (existing channel/source config store vs a new settings file)? Decide at M5.

## Known risks / watch-items
- **Don't break the working launcher.** `run.bat` / `run.sh` and the `:8080` backend already work — changes are additive (Delivery Standard §1).
- **twscrape pool (R9.1).** Stale handles are likely rate-limit / account-pool behavior, not a UI bug — diagnose before "fixing" the UI.
- **Thumbnails (R4.1).** List vs post mismatch points at two code paths reading different image fields — unify the source, don't fake images.
