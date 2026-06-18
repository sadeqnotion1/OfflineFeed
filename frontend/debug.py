"""
debug.py - OfflineFeed diagnostics & debug subsystem.

Why this exists
---------------
The old launcher died with a message that hides the real problem:

    [WARNING] The Feed Server exited with an error - Code: 1
    If this is your first time launching, make sure requirements are met...

"Code: 1" can mean a dozen different things: a missing package, a busy port,
a syntax error in the backend, the wrong Python version, a bad working
directory, etc. This module replaces the guesswork with facts:

* a persistent rotating log file at  <repo>/logs/offlinefeed_debug.log
* global hooks that capture uncaught exceptions on the main thread AND inside
  the backend daemon thread (which were previously swallowed)
* a preflight "doctor" that checks the Python version, required packages, the
  TCP port and the backend module, returning structured results + a fix hint
* an in-memory ring buffer so the in-app "System Logs" panel can show what went
  wrong even when the backend HTTP server never came up

Nothing here imports PySide6, so it is safe to use from a plain CLI (doctor.py)
or a launcher before Qt is available.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import socket
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
#  Paths
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent        # .../OfflineFeed/frontend
REPO_ROOT = HERE.parent                        # .../OfflineFeed
LOG_DIR = REPO_ROOT / "logs"
LOG_FILE = LOG_DIR / "offlinefeed_debug.log"

LOGGER_NAME = "offlinefeed"
_DEFAULT_PORT = 8080

# Map a pip distribution name -> the module you actually "import".
# Used so the doctor can verify requirements.txt entries by importing them.
KNOWN_IMPORT_NAMES = {
    "pyside6": "PySide6",
    "beautifulsoup4": "bs4",
    "python-telegram-bot": "telegram",
    "pillow": "PIL",
    "pyyaml": "yaml",
    "python-dateutil": "dateutil",
    "feedparser": "feedparser",
    "requests": "requests",
    "lxml": "lxml",
}

# Packages the app needs even if requirements.txt is missing/incomplete.
BASELINE_REQUIREMENTS = ["PySide6"]


# --------------------------------------------------------------------------- #
#  In-memory ring buffer (feeds the in-app System Logs panel)
# --------------------------------------------------------------------------- #
class _RingBufferHandler(logging.Handler):
    """Keeps the most recent N records in memory as UI-friendly dicts."""

    def __init__(self, capacity: int = 300) -> None:
        super().__init__()
        self.capacity = capacity
        self._records: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "section": getattr(record, "section", record.name),
                "time": time.strftime("%H:%M:%S", time.localtime(record.created)),
                "message": record.getMessage(),
                "level": record.levelname,
            }
            if record.exc_info:
                entry["message"] += "\n" + "".join(
                    traceback.format_exception(*record.exc_info)
                ).rstrip()
            with self._lock:
                self._records.append(entry)
                if len(self._records) > self.capacity:
                    self._records = self._records[-self.capacity:]
        except Exception:  # never let logging crash the app
            pass

    def snapshot(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(reversed(self._records))  # newest first


_ring = _RingBufferHandler()
_logger: Optional[logging.Logger] = None
_hooks_installed = False


# --------------------------------------------------------------------------- #
#  Logger
# --------------------------------------------------------------------------- #
def get_logger() -> logging.Logger:
    """Return the singleton OfflineFeed logger (idempotent)."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console (stderr)
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # Rotating file - best effort (read-only installs shouldn't crash startup)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not open log file %s: %s", LOG_FILE, exc)

    # UI ring buffer
    logger.addHandler(_ring)

    _logger = logger
    return logger


def log_event(section: str, message: str, level: int = logging.INFO) -> None:
    """Log a message tagged with a UI 'section' (shown in System Logs)."""
    get_logger().log(level, message, extra={"section": section})


def log_exception(section: str, message: str) -> None:
    """Log the currently-handled exception with a full traceback."""
    get_logger().error(message, exc_info=True, extra={"section": section})


def recent_logs() -> List[Dict[str, Any]]:
    """Newest-first snapshot of recent log entries for the UI."""
    return _ring.snapshot()


# --------------------------------------------------------------------------- #
#  Global exception hooks
# --------------------------------------------------------------------------- #
def install_excepthooks() -> None:
    """Route uncaught exceptions (main + threads) into the log."""
    global _hooks_installed
    if _hooks_installed:
        return
    log = get_logger()

    prev = sys.excepthook

    def _hook(exc_type, exc, tb):
        log.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc, tb),
            extra={"section": "Crash"},
        )
        prev(exc_type, exc, tb)

    sys.excepthook = _hook

    # Thread exceptions (Python 3.8+) - this is what previously hid backend
    # daemon-thread crashes.
    if hasattr(threading, "excepthook"):
        def _thread_hook(args):
            log.critical(
                "Uncaught exception in thread %s" % args.thread.name,
                exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
                extra={"section": "Crash"},
            )
        threading.excepthook = _thread_hook

    _hooks_installed = True


# --------------------------------------------------------------------------- #
#  Preflight checks ("doctor")
# --------------------------------------------------------------------------- #
def _check(name: str, status: str, detail: str, fix: str = "") -> Dict[str, str]:
    return {"name": name, "status": status, "detail": detail, "fix": fix}


def parse_requirements(path: Path) -> List[Tuple[str, str]]:
    """Return [(dist_name, import_name), ...] from a requirements.txt."""
    out: List[Tuple[str, str]] = []
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        # strip version specifiers / extras / markers
        dist = line
        for sep in ("==", ">=", "<=", "~=", "!=", ">", "<", ";", "[", " "):
            if sep in dist:
                dist = dist.split(sep)[0]
        dist = dist.strip()
        if not dist:
            continue
        imp = KNOWN_IMPORT_NAMES.get(dist.lower(), dist.replace("-", "_"))
        out.append((dist, imp))
    return out


def check_python(minimum: Tuple[int, int] = (3, 8)) -> Dict[str, str]:
    v = sys.version_info
    cur = "%d.%d.%d" % (v.major, v.minor, v.micro)
    if (v.major, v.minor) < minimum:
        return _check(
            "Python version", "fail",
            "Found %s, need >= %d.%d" % (cur, minimum[0], minimum[1]),
            "Install Python %d.%d+ and relaunch." % minimum,
        )
    return _check("Python version", "pass", "%s (%s)" % (cur, sys.executable))


def _try_import(import_name: str) -> Optional[str]:
    """Return None if importable, else the error string."""
    try:
        __import__(import_name)
        return None
    except Exception as exc:  # noqa: BLE001
        return "%s: %s" % (type(exc).__name__, exc)


def check_requirements(req_path: Path) -> List[Dict[str, str]]:
    """Verify each requirement actually imports."""
    results: List[Dict[str, str]] = []
    reqs = parse_requirements(req_path)
    # Always include the baseline even if requirements.txt is missing.
    seen = {imp for _, imp in reqs}
    for base in BASELINE_REQUIREMENTS:
        if base not in seen:
            reqs.append((base, base))

    if not reqs:
        results.append(_check(
            "Requirements file", "warn",
            "No requirements.txt found at %s" % req_path,
            "Create one or rely on the baseline (%s)." % ", ".join(BASELINE_REQUIREMENTS),
        ))

    for dist, imp in reqs:
        err = _try_import(imp)
        if err is None:
            results.append(_check("Package: %s" % dist, "pass", "import %s OK" % imp))
        else:
            results.append(_check(
                "Package: %s" % dist, "fail", err,
                "pip install %s" % dist,
            ))
    return results


def port_listening(host: str = "127.0.0.1", port: int = _DEFAULT_PORT,
                   timeout: float = 0.4) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def check_port(port: int = _DEFAULT_PORT) -> Dict[str, str]:
    if port_listening("127.0.0.1", port):
        return _check(
            "Backend port %d" % port, "warn",
            "Something is already listening on 127.0.0.1:%d" % port,
            "A previous instance may still be running. Close it (or change the "
            "port) - a busy port makes the Feed Server exit with code 1.",
        )
    return _check("Backend port %d" % port, "pass", "Free")


def check_backend_module(module: str = "gui_server") -> Dict[str, str]:
    import importlib.util
    # Search the repo root + frontend dir the same way app.py does.
    for p in (str(REPO_ROOT), str(HERE)):
        if p not in sys.path:
            sys.path.insert(0, p)
    try:
        spec = importlib.util.find_spec(module)
    except Exception as exc:  # noqa: BLE001
        return _check("Backend module '%s'" % module, "fail",
                      "find_spec error: %s" % exc,
                      "Make sure %s.py sits next to app.py or in the repo root." % module)
    if spec is None:
        return _check(
            "Backend module '%s'" % module, "fail",
            "Not found on sys.path",
            "Place %s.py in the project folder (next to app.py or repo root) "
            "and launch from that folder." % module,
        )
    return _check("Backend module '%s'" % module, "pass", spec.origin or "found")


def probe_backend_import(module: str = "gui_server") -> Dict[str, str]:
    """Import the backend in a clean subprocess to catch import-time crashes.

    This is the single most useful check for "exited with code 1": it returns
    the real traceback the old launcher threw away.
    """
    code = (
        "import importlib, sys; "
        "importlib.import_module(sys.argv[1])"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, module],
            cwd=str(REPO_ROOT),
            capture_output=True, text=True, timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        return _check("Backend import", "warn", "Could not probe: %s" % exc)
    if proc.returncode == 0:
        return _check("Backend import", "pass", "%s imported cleanly" % module)
    detail = (proc.stderr or proc.stdout or "").strip()
    return _check(
        "Backend import", "fail",
        detail or "exited with code %d" % proc.returncode,
        "This traceback is the real reason the Feed Server exits with code 1.",
    )


def run_diagnostics(port: int = _DEFAULT_PORT, backend_module: str = "gui_server",
                    probe: bool = True) -> Dict[str, Any]:
    """Run all checks and return a structured report."""
    req_path = REPO_ROOT / "requirements.txt"
    checks: List[Dict[str, str]] = []
    checks.append(check_python())
    checks.append(_check("Working dir", "pass", str(Path.cwd())))
    checks.append(_check("Requirements path", "pass" if req_path.exists() else "warn",
                         str(req_path) + ("" if req_path.exists() else " (missing)")))
    checks.extend(check_requirements(req_path))
    checks.append(check_port(port))
    backend = check_backend_module(backend_module)
    checks.append(backend)
    if probe and backend["status"] == "pass":
        checks.append(probe_backend_import(backend_module))

    has_fail = any(c["status"] == "fail" for c in checks)
    has_warn = any(c["status"] == "warn" for c in checks)
    summary = ("FAIL - see fixes below" if has_fail
               else "OK with warnings" if has_warn
               else "All checks passed")
    return {"ok": not has_fail, "checks": checks, "summary": summary,
            "log_file": str(LOG_FILE)}


_GLYPH = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}


def format_report(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 64)
    lines.append(" OfflineFeed - diagnostics")
    lines.append("=" * 64)
    for c in report["checks"]:
        glyph = _GLYPH.get(c["status"], "[ ? ]")
        lines.append("%s %-26s %s" % (glyph, c["name"], c["detail"]))
        if c.get("fix") and c["status"] != "pass":
            lines.append("        fix -> %s" % c["fix"])
    lines.append("-" * 64)
    lines.append(" Result : %s" % report["summary"])
    lines.append(" Log    : %s" % report["log_file"])
    lines.append("=" * 64)
    return "\n".join(lines)


if __name__ == "__main__":
    # `python debug.py` behaves like the doctor.
    rep = run_diagnostics()
    print(format_report(rep))
    sys.exit(0 if rep["ok"] else 1)
