# OfflineFeed — PySide6 + QML Telegram-style frontend

A near pixel-perfect Telegram Desktop clone UI for the existing OfflineFeed
backend. The backend (`gui_server.py` + `offline_viewer/`) is **unchanged**; this
frontend talks to it over its existing local HTTP API (`http://127.0.0.1:8080`).

## Layout

```
frontend/
  app.py                  PySide6 entry: frameless window, fonts, logo, backend bootstrap
  bridge.py               QObject bridge + 3 QAbstractListModels (chat / messages / sources)
  gen_assets.py           regenerates the SVG icon set + logo.svg
  qml/
    Main.qml              3-pane layout + slide-in info panel + toast
    themes/
      Theme.qml           singleton design tokens (exact Telegram palettes)
      qmldir              registers the `themes` singleton module
    components/
      TitleBar.qml        frameless title bar, SVG window buttons, logo (no emoji)
      FolderRail.qml      labeled folder tabs + unread badges + single Settings entry
      ChatList.qml        search field + channel list
      ChatRow.qml         one channel row (avatar, unread badge, mute/pin)
      ChatView.qml        header, pinned bar, wallpaper, messages, forward bar
      MessageBubble.qml   bubble w/ image, ticks, views, reactions, time (height fix)
      ReactionsBar.qml    reaction pills
      InfoPanel.qml       slide-in channel info
      Avatar.qml          per-peer gradient avatar + initials
      Icon.qml            recolorable SVG icon via ColorOverlay
      ChatContextMenu.qml right-click chat menu
      ChatSettings.qml    theme / name color / auto-night / font / wallpaper
      SettingsPage.qml    consolidated settings: appearance + sources + Telegram + system
    assets/
      icons/*.svg         30 crisp white-stroke line icons (recolored at runtime)
      logo.svg            app + window icon
      fonts/              place Roboto-*.ttf and Vazirmatn-*.ttf here (see below)
```

## Requirements

* Python 3.9+
* **Full PySide6** (NOT PySide6-Essentials — the `Qt5Compat.GraphicalEffects`
  module used for icon recoloring ships only with full PySide6):

```bash
pip install PySide6
```

Verify the GraphicalEffects module is present (fixes blank-icon issue #2):

```bash
python -c "from PySide6.QtCore import QLibraryInfo; import os, pathlib; \
p = pathlib.Path(QLibraryInfo.path(QLibraryInfo.QmlImportsPath)) / 'Qt5Compat' / 'GraphicalEffects'; \
print('GraphicalEffects present:', p.exists())"
```

## Fonts (Roboto + Vazirmatn for Persian/RTL)

Drop the TTFs into `frontend/qml/assets/fonts/`:

* `Roboto-Regular.ttf`, `Roboto-Medium.ttf`, `Roboto-Bold.ttf`
* `Vazirmatn-Regular.ttf`, `Vazirmatn-Bold.ttf`

`app.py` auto-loads every `*.ttf`/`*.otf` in that folder. If they are missing the
UI falls back to system fonts — it still runs.

## Run

From the repository root (recommended — lets `app.py` find `gui_server.py`):

```bash
python -m frontend.app
```

or:

```bash
cd frontend
python app.py
```

`app.py` will try to start the existing backend in a daemon thread. If your
backend uses a different entry function, start it yourself first; the UI simply
attaches to `http://127.0.0.1:8080` if it is already up.

## Regenerate icons

```bash
python frontend/gen_assets.py
```

## RTL / Persian

Call `bridge.setRtl(true)` (e.g. wire it to a language switch). The whole UI
mirrors via `LayoutMirroring`, and Persian text right-aligns in bubbles, rows and
fields.

## PyInstaller packaging

The critical part is bundling the `qml/` tree (Main.qml, themes, components,
assets) **and** forcing the `Qt5Compat` QML plugin to be collected. Use the
provided spec:

```bash
pip install pyinstaller
pyinstaller OfflineFeed.spec
```

Key points baked into the spec:

* `datas` bundles the entire `frontend/qml` folder (preserving structure) so
  `import "./themes"`, the `themes` singleton, and `assets/icons/*.svg` resolve.
* `collect_all('PySide6')` + explicit `Qt5Compat` collection ensures
  `Qt5Compat.GraphicalEffects` (icon recoloring) is shipped.
* In a frozen build, QML lives next to the executable; `app.py` already resolves
  paths relative to the script/exe via `Path(__file__)`. For one-file builds add
  a `sys._MEIPASS` fallback if you switch to `--onefile`.

See `OfflineFeed.spec` for the full, runnable configuration.
