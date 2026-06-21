"""
app.py — PySide6 entry point for the OfflineFeed Telegram-style desktop UI.

Responsibilities
----------------
* Boot the existing Python backend (gui_server.py) on its local HTTP port in a
  daemon thread — unchanged from the original app.
* Create a frameless QApplication, load the Roboto + Vazirmatn fonts, set the
  window icon from logo.svg.
* Register the bridge + list models as QML context properties.
* Add the qml/ directory to the QML import path so `import "./themes"` and the
  `themes` singleton module resolve, then load Main.qml.

Run:
    python -m frontend.app          # from the repo root (recommended)
    # or
    cd frontend && python app.py
"""
from __future__ import annotations

import os
import sys
import json
import time
import threading
import urllib.request
from pathlib import Path

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QGuiApplication, QFontDatabase, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

# Importing QtSvg loads Qt's "qsvg" image-format plugin into the process so the
# QML engine can rasterize .svg sources (all line icons + the app logo).
# Without this, PySide6 frequently renders SVG <Image> sources as blank — which
# is exactly why the icons and logo were invisible.
try:
    from PySide6 import QtSvg  # noqa: F401
except Exception:  # noqa: BLE001
    pass

# --------------------------------------------------------------------------- #
#  Paths
# --------------------------------------------------------------------------- #
HERE = Path(__file__).resolve().parent          # .../OfflineFeed/frontend
REPO_ROOT = HERE.parent                          # .../OfflineFeed
QML_DIR = HERE / "qml"
ASSETS = QML_DIR / "assets"
FONTS = ASSETS / "fonts"
LOGO = ASSETS / "logo.svg"

def get_backend_port() -> int:
    try:
        path = REPO_ROOT / "backend" / "offline_viewer" / "assets" / "ui_settings.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            loaded = data[0] if (isinstance(data, list) and len(data) > 0) else (data if isinstance(data, dict) else {})
            return loaded.get("advanced", {}).get("backend_port", 8080)
    except Exception:
        pass
    return 8080

def get_backend_base() -> str:
    return f"http://127.0.0.1:{get_backend_port()}"

# When True, private/hidden font families (names starting with ".") are excluded
# from the system font list exposed to the desktop UI. Flip to False to show
# absolutely everything QFontDatabase reports.
EXCLUDE_PRIVATE_FAMILIES = True

# Allow importing the bridge whether launched as a module or a script.
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "backend"))  # backend modules (gui_server, feed_store, ...)

from bridge import ChatBridge, ChatListModel, MessageModel, SourcesModel, SearchResultsModel  # noqa: E402

# OfflineFeed diagnostics (logging + crash hooks + preflight). Never fatal.
try:
    import debug as _dbg  # noqa: E402
    _dbg.get_logger()
except Exception:  # noqa: BLE001
    _dbg = None


def _log_event(section, message):
    if _dbg:
        _dbg.log_event(section, message)
    else:
        print(f"[OfflineFeed] {section}: {message}")


def _log_exc(section, message):
    if _dbg:
        _dbg.log_exception(section, message)
    else:
        print(f"[OfflineFeed] {section}: {message}")


# --------------------------------------------------------------------------- #
#  Backend bootstrap (existing gui_server.py, untouched)
# --------------------------------------------------------------------------- #
def _backend_alive() -> bool:
    try:
        urllib.request.urlopen(get_backend_base() + "/api/status", timeout=1.5)
        return True
    except Exception:  # noqa: BLE001
        return False


def start_backend() -> None:
    """Import and launch the existing backend server in a daemon thread.

    The original project starts gui_server.py's ThreadingHTTPServer on port
    8080. We reuse it verbatim. If it is already running (e.g. launched
    separately) we simply attach to it.
    """
    if _backend_alive():
        return

    def run():
        # Try the common entry points exposed by the existing backend without
        # modifying it. The first import that works wins.
        candidates = []
        try:
            # Prevent the existing backend from auto-opening the OLD web UI in a
            # browser on startup (it calls webbrowser.open). We render our own UI.
            import webbrowser
            webbrowser.open = lambda *a, **k: True
            import gui_server  # type: ignore
            candidates = [
                getattr(gui_server, "start_server", None),  # confirmed entry point
                getattr(gui_server, "main", None),
                getattr(gui_server, "run", None),
                getattr(gui_server, "start", None),
                getattr(gui_server, "serve", None),
            ]
        except Exception as exc:  # noqa: BLE001
            _log_exc("Backend", f"Could not import backend gui_server: {exc}")
            return
        for fn in candidates:
            if callable(fn):
                try:
                    fn()
                    return
                except TypeError:
                    try:
                        fn(get_backend_port())
                        return
                    except Exception as exc:  # noqa: BLE001
                        _log_exc("Backend", f"Backend entry failed: {exc}")
        _log_event("Backend", "No callable backend entry point found; "
                   "start gui_server.py manually if the UI stays empty.")

    threading.Thread(target=run, daemon=True, name="offlinefeed-backend").start()

    # Give the server a moment to bind the port.
    for _ in range(20):
        if _backend_alive():
            _log_event("Backend", f"Feed Server is up on {get_backend_base()}")
            break
        time.sleep(0.25)
    else:
        _log_event("Backend", f"Feed Server did not respond on {get_backend_base()} "
                   "after startup; run `python -m frontend.doctor` to see why.")


# --------------------------------------------------------------------------- #
#  Fonts
# --------------------------------------------------------------------------- #
def load_fonts() -> None:
    """Register the bundled .ttf/.otf families (Roboto, Vazirmatn, ...).

    Unchanged: bundled fonts are registered FIRST so they always appear in the
    application font database (and therefore in the system font list below).
    """
    if not FONTS.exists():
        return
    for ttf in FONTS.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(ttf))
    for otf in FONTS.glob("*.otf"):
        QFontDatabase.addApplicationFont(str(otf))


def enumerate_system_fonts() -> list:
    """Return a clean, sorted, de-duplicated list of every installed font family.

    Uses the static QFontDatabase API available in the repo's Qt6/PySide6
    version (`QFontDatabase.families()`). Because bundled fonts were registered
    in load_fonts() first, they are included here too.

    Cross-safe: any failure (or an empty result) returns an empty list so the
    caller / QML can fall back to the previous hardcoded names instead of
    crashing. Must be called AFTER a QGuiApplication/QApplication exists.
    """
    try:
        families = QFontDatabase.families()
    except Exception:  # noqa: BLE001
        return []

    seen = {}
    for fam in families:
        if not fam:
            continue
        # Drop private/hidden families (configurable) and de-dupe case-insensitively.
        if EXCLUDE_PRIVATE_FAMILIES and fam.startswith("."):
            continue
        key = fam.casefold()
        if key not in seen:
            seen[key] = fam
    return sorted(seen.values(), key=lambda s: s.casefold())


# --------------------------------------------------------------------------- #
#  main
# --------------------------------------------------------------------------- #
def main() -> int:
    if _dbg:
        _dbg.install_excepthooks()
    _log_event("App", "OfflineFeed starting")

    # High-DPI crispness for the SVG icon set.
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
    # Disable QML disk caching to prevent cached legacy component conflicts.
    os.environ["QML_DISABLE_DISK_CACHE"] = "1"

    start_backend()

    # QApplication (QtWidgets) gives us a taskbar/window icon + native dialogs;
    # QML still renders the actual UI.
    app = QApplication(sys.argv)
    app.setApplicationName("OfflineFeed")
    app.setOrganizationName("OfflineFeed")
    if LOGO.exists():
        app.setWindowIcon(QIcon(str(LOGO)))

    load_fonts()

    # Enumerate ALL installed system fonts ONCE (cached for the app lifetime)
    # and hand them to the bridge so the QML Font Family picker can list every
    # family. Computed after load_fonts() so bundled fonts are included, and
    # after the QApplication exists so QFontDatabase is populated.
    system_fonts = enumerate_system_fonts()
    _log_event("Fonts", f"Discovered {len(system_fonts)} system font families")

    # Models + bridge
    chat_model = ChatListModel()
    message_model = MessageModel()
    sources_model = SourcesModel()
    search_results_model = SearchResultsModel()
    bridge = ChatBridge(chat_model, message_model, sources_model,
                        search_results_model=search_results_model,
                        system_fonts=system_fonts)

    engine = QQmlApplicationEngine()
    # Make `import "./themes"` + the themes singleton module resolve.
    engine.addImportPath(str(QML_DIR))

    ctx = engine.rootContext()
    ctx.setContextProperty("bridge", bridge)
    ctx.setContextProperty("chatModel", chat_model)
    ctx.setContextProperty("messageModel", message_model)
    ctx.setContextProperty("sourcesModel", sources_model)
    ctx.setContextProperty("searchResultsModel", search_results_model)

    engine.load(QUrl.fromLocalFile(str(QML_DIR / "Main.qml")))
    if not engine.rootObjects():
        _log_event("App", "Failed to load Main.qml (see Qt errors above)")
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
