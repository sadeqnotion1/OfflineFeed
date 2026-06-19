"""
doctor.py - one-command health check for OfflineFeed.

Run it whenever the app won't start:

    python -m frontend.doctor        # from the repo root (recommended)
    python frontend/doctor.py        # also works

It prints a PASS/WARN/FAIL report for the Python version, every package in
requirements.txt, the backend port, and the backend module - and, crucially,
the real traceback if the Feed Server backend fails to import (the thing the
old "exited with code 1" message hid from you).

Exit code is 0 when healthy, 1 when something is broken - so launchers/CI can
branch on it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `import debug` work whether launched as a module or a loose script.
_HERE = Path(__file__).resolve().parent
for _p in (str(_HERE), str(_HERE.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    import debug  # type: ignore
except Exception:  # pragma: no cover
    from frontend import debug  # type: ignore


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Optional: `--port 9000` to check a non-default backend port.
    port = 8080
    try:
        settings_path = _HERE.parent / "offline_viewer" / "assets" / "ui_settings.json"
        if settings_path.exists():
            import json
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            loaded = data[0] if (isinstance(data, list) and len(data) > 0) else (data if isinstance(data, dict) else {})
            port = loaded.get("advanced", {}).get("backend_port", 8080)
    except Exception:
        pass

    if "--port" in argv:
        try:
            port = int(argv[argv.index("--port") + 1])
        except (ValueError, IndexError):
            pass

    debug.get_logger()  # ensure the log file is created
    report = debug.run_diagnostics(port=port)
    print(debug.format_report(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
