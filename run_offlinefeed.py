"""
run_offlinefeed.py - the smart launcher that REPLACES the old batch wrapper.

The previous launcher printed only:

    [WARNING] The Feed Server exited with an error - Code: 1
    If this is your first time launching, make sure requirements are met...

...which hides the real cause. This launcher instead:

  1. Runs the diagnostics doctor first. If a hard requirement is missing
     (e.g. PySide6) it prints exactly which one + the pip command, and stops.
  2. Probes the backend import so an import-time crash shows its REAL traceback.
  3. Launches the GUI (frontend.app). If it exits non-zero, it prints the tail
     of the debug log - the actual error - instead of a generic message.

Usage:
    python run_offlinefeed.py            # diagnose, then launch the app
    python run_offlinefeed.py --doctor   # only run diagnostics, don't launch
    python run_offlinefeed.py --force    # launch even if checks fail
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
FRONTEND = REPO_ROOT / "frontend"
for _p in (str(REPO_ROOT), str(FRONTEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import debug  # noqa: E402  (frontend/ is on the path)


def _tail(path: Path, lines: int = 25) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(data[-lines:])
    except Exception:
        return "(no log file yet)"


def main() -> int:
    args = sys.argv[1:]
    doctor_only = "--doctor" in args
    force = "--force" in args
    refresh_avatars = "--refresh-avatars" in args
    no_avatars = "--no-avatars" in args

    log = debug.get_logger()
    debug.install_excepthooks()
    log.info("Launcher starting (cwd=%s)", Path.cwd())

    # Load configured port for diagnostics check
    port = 8080
    try:
        settings_path = REPO_ROOT / "offline_viewer" / "assets" / "ui_settings.json"
        if settings_path.exists():
            import json
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            loaded = data[0] if (isinstance(data, list) and len(data) > 0) else (data if isinstance(data, dict) else {})
            port = loaded.get("advanced", {}).get("backend_port", 8080)
    except Exception:
        pass

    report = debug.run_diagnostics(port=port)
    print(debug.format_report(report))

    if doctor_only:
        return 0 if report["ok"] else 1

    if not report["ok"] and not force:
        print("\nRefusing to launch: fix the [FAIL] items above, then retry.")
        print("(Override with:  python run_offlinefeed.py --force )")
        return 1

    # Run the avatar backfill pass unless skipped
    if not no_avatars:
        try:
            from frontend.avatar_fetcher import backfill_avatars
            backfill_avatars(refresh_avatars=refresh_avatars)
        except Exception as e:
            log.error("Failed to run avatar backfill on launch: %s", e)

    # Launch the GUI as a child process so we can react to its exit code.
    print("\nStarting OfflineFeed...\n")
    log.info("Launching frontend.app")
    try:
        proc = subprocess.run([sys.executable, "-m", "frontend.app"],
                              cwd=str(REPO_ROOT))
        code = proc.returncode
    except KeyboardInterrupt:
        return 0
    except Exception:
        debug.log_exception("Launcher", "Failed to start frontend.app")
        code = 1

    if code != 0:
        log.error("OfflineFeed exited with code %s", code)
        print("\n" + "=" * 64)
        print(" OfflineFeed exited with code %s. Most recent log lines:" % code)
        print("=" * 64)
        print(_tail(debug.LOG_FILE))
        print("=" * 64)
        print(" Full log : %s" % debug.LOG_FILE)
        print(" Re-run diagnostics:  python -m frontend.doctor")
    return code


if __name__ == "__main__":
    sys.exit(main())
