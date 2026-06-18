# Bundled fonts

These `.ttf` / `.otf` files are the fonts that ship **with** OfflineFeed
(e.g. Roboto and Vazirmatn). They are registered at startup by
`load_fonts()` in `frontend/app.py`.

## System fonts now load automatically

As of the font-system update, the desktop app no longer relies only on these
bundled files. After registering the bundled fonts, `frontend/app.py` calls
`enumerate_system_fonts()` which uses the static `QFontDatabase.families()` API
to discover **every font family installed on the machine**. That full list is
exposed to QML as `bridge.systemFonts` and powers the searchable **Font Family**
picker in Settings → Chat appearance (each entry is previewed in its own font).

Notes:
- Bundled fonts are still registered **first**, so Roboto / Vazirmatn always
  appear in the list even if they are not installed system-wide.
- Private/hidden families (names starting with `.`) are filtered out by default
  via the `EXCLUDE_PRIVATE_FAMILIES` constant in `frontend/app.py`.
- If enumeration ever fails or returns nothing, the picker falls back to the
  original built-in names (`Roboto`, `Vazirmatn`, `Arial`, `Segoe UI`).
- The offline article viewer (web UI) has its **own, independent** font picker
  served from `GET /api/system/fonts`; it does not share this list.

You can still drop additional `.ttf` / `.otf` files here to bundle more fonts.
