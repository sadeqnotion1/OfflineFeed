# OfflineFeed - Debug & Diagnostics

When the app dies with something like:

```
[WARNING] The Feed Server exited with an error - Code: 1
If this is your first time launching, make sure requirements are met...
```

...that message is **generic** - it does not tell you *why*. This project now
ships a debug subsystem that surfaces the real cause.

## 1. Run the doctor

```
python -m frontend.doctor
```

You get a PASS / WARN / FAIL report:

```
================================================================
 OfflineFeed - diagnostics
================================================================
[PASS] Python version             3.11.6 (C:\...\python.exe)
[PASS] Working dir                E:\Projects\OfflineFeed
[FAIL] Package: feedparser        ModuleNotFoundError: No module named 'feedparser'
        fix -> pip install feedparser
[WARN] Backend port 8080          Something is already listening on 127.0.0.1:8080
        fix -> A previous instance may still be running. Close it...
[FAIL] Backend import             Traceback (most recent call last): ...
        fix -> This traceback is the real reason the Feed Server exits with code 1.
----------------------------------------------------------------
 Result : FAIL - see fixes below
 Log    : E:\Projects\OfflineFeed\logs\offlinefeed_debug.log
================================================================
```

The **Backend import** check imports your backend in a clean subprocess and
prints the actual traceback - the single most useful clue for "Code: 1".

## 2. Launch through the smart launcher

Instead of the old `.bat`, use:

```
python run_offlinefeed.py      # or just double-click run.bat on Windows
```

It runs the doctor first, refuses to launch on hard failures (with the exact
fix), and if the app still exits non-zero it prints the tail of the log - the
real error - instead of the generic warning. Use `--force` to launch anyway,
`--doctor` to only diagnose.

## 3. Read the log

Everything is recorded (with rotation) at:

```
logs/offlinefeed_debug.log
```

Uncaught exceptions on the main thread **and** inside the backend daemon thread
are captured here - previously those thread crashes were swallowed silently.

## 4. In-app System Logs

Open **Settings -> System -> System Logs**. It shows the backend activity log
when the server is up, and automatically falls back to the local debug log
(recent errors, missing packages, crash tracebacks) when the backend never
started - so you can diagnose without leaving the app.

## What feeds what

| Piece                     | Role                                                        |
|---------------------------|-------------------------------------------------------------|
| `frontend/debug.py`       | logging, crash hooks, ring buffer, all preflight checks     |
| `frontend/doctor.py`      | CLI report (`python -m frontend.doctor`)                    |
| `run_offlinefeed.py`      | smart launcher: diagnose -> launch -> show real error       |
| `run.bat`                 | Windows entry point that calls the launcher and pauses      |
| `logs/offlinefeed_debug.log` | persistent rotating log                                  |
| Settings -> System Logs   | in-app viewer with local-log fallback                       |
