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

REPO_ROOT = Path(__file__).resolve().parent.parent  # backend/ sits one level below the repo root
BACKEND = REPO_ROOT / "backend"
FRONTEND = REPO_ROOT / "frontend"
for _p in (str(REPO_ROOT), str(BACKEND), str(FRONTEND)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import debug  # noqa: E402  (frontend/ is on the path)


def _tail(path: Path, lines: int = 25) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(data[-lines:])
    except Exception:
        return "(no log file yet)"


def _get_python_310_executable() -> str | None:
    import subprocess
    import sys
    import os
    # 1. Try py -3.12, py -3.11, py -3.10
    for ver in ["3.12", "3.11", "3.10"]:
        try:
            res = subprocess.run(["py", f"-{ver}", "-V"], capture_output=True, text=True)
            if res.returncode == 0:
                return f"py -{ver}"
        except Exception:
            pass
    # 2. Check current interpreter
    if sys.version_info >= (3, 10):
        return sys.executable
    # 3. Check common Windows program paths
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    if local_appdata:
        base_dir = os.path.join(local_appdata, "Programs", "Python")
        for ver_folder in ["Python312", "Python311", "Python310"]:
            p = os.path.join(base_dir, ver_folder, "python.exe")
            if os.path.isfile(p):
                return p
    return None


def main() -> int:
    import os
    os.environ["OFFLINEFEED_NITTER_HOSTS"] = "http://127.0.0.1:8081"
    os.environ["OFFLINEFEED_NITTER_TIMEOUT"] = "10"

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
        settings_path = BACKEND / "offline_viewer" / "assets" / "ui_settings.json"
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

    # Auto-start twscrape RSS shim if available
    shim_proc = None
    shim_path = BACKEND / "twscrape" / "twscrape_rss_shim.py"
    if shim_path.exists():
        py_310 = _get_python_310_executable()
        if py_310:
            log.info("Auto-starting twscrape RSS shim using: %s", py_310)
            print(f"Auto-starting twscrape RSS shim using: {py_310}...")
            import os
            env = os.environ.copy()
            env["TWSCRAPE_ACCOUNTS_DB"] = str(BACKEND / "twscrape" / "accounts.db")
            if py_310.startswith("py "):
                parts = py_310.split()
                cmd = ["py", parts[1], str(shim_path)]
            else:
                cmd = [py_310, str(shim_path)]
            try:
                log_dir = REPO_ROOT / "logs"
                log_dir.mkdir(exist_ok=True)
                shim_log = open(log_dir / "twscrape_shim.log", "w", encoding="utf-8")
                shim_proc = subprocess.Popen(
                    cmd,
                    cwd=str(BACKEND / "twscrape"),
                    env=env,
                    stdout=shim_log,
                    stderr=shim_log
                )
            except Exception as e:
                log.error("Failed to auto-start twscrape RSS shim: %s", e)
                print(f"Warning: Failed to auto-start twscrape RSS shim: {e}")
        else:
            log.warning("Python 3.10+ not found; cannot auto-start twscrape RSS shim.")
            print("Warning: Python 3.10+ not found; cannot auto-start twscrape RSS shim.")

    # Launch the GUI as a child process so we can react to its exit code.
    print("\nStarting OfflineFeed...\n")
    log.info("Launching frontend.app")
    try:
        proc = subprocess.run([sys.executable, "-m", "frontend.app"],
                              cwd=str(REPO_ROOT))
        code = proc.returncode
    except KeyboardInterrupt:
        code = 0
    except Exception:
        debug.log_exception("Launcher", "Failed to start frontend.app")
        code = 1
    finally:
        if shim_proc and shim_proc.poll() is None:
            log.info("Stopping twscrape RSS shim...")
            print("Stopping twscrape RSS shim...")
            shim_proc.terminate()
            try:
                shim_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                shim_proc.kill()

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
