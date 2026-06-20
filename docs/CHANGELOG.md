# OfflineFeed — 8 Fixes (drop-in delivery)

This ZIP mirrors the repository with all edits already applied. To use it:
back up your current repo, then copy these files over yours (or just run from
this folder). No new dependencies were added. `python run_offlinefeed.py`
starts exactly as before (doctor → backend probe → PySide6+QML app).

---

## How to run & verify

```bash
# 1. (optional) regenerate icons — already regenerated in this ZIP
python3 frontend/gen_assets.py        # writes 34 icons incl. soccer.svg + logo.svg

# 2. sanity-check sources (no GUI needed)
python3 -m py_compile frontend/bridge.py frontend/gen_assets.py
node --check offline_viewer/app.js
node --check offline_viewer/font_picker.js

# 3. run the app normally
python run_offlinefeed.py              # also: --doctor / --force still work
```

---

## New persisted settings keys (ui_settings.json)

| Key                          | Type            | Meaning                                              |
|------------------------------|-----------------|------------------------------------------------------|
| `appearance.reader_font_family` | string       | Font used ONLY by the article reader (default `Roboto`) |
| `appearance.wallpaper_image` | string (file URI) | Path to a user-chosen wallpaper image              |
| `appearance.wallpaper_mode`  | string          | May now be `"image"` (custom image) in addition to built-ins |
| `pins.channels`              | list[str]       | Pinned channel ids (specials excluded)               |
| `pins.messages`              | list[str]       | Pinned post urls                                     |
| `folders.custom`             | list[obj]       | Custom folders `{id,name,channels[]}`                |

Wallpaper images are copied into `data/wallpapers/wallpaper.<ext>` (next to the
existing `data/avatars/`), so the source file can move/delete without breaking.

---

## What changed, by task

### 1. Separate reader font
- **Desktop:** `bridge.py` adds `readerFontFamily` property + `setReaderFont()` slot,
  persisted under `appearance.reader_font_family`. `Theme.qml` exposes
  `readerFontFamily`; `ReaderView.qml` uses it for title/heading/paragraph/quote.
  `AppearancePage.qml` adds a "Reader" section with a font picker fed by
  `bridge.systemFonts`. The chat/UI `fontFamily` is untouched.
- **Web:** `font_picker.js` now sets ONLY `--reader-font-family` (no longer
  `--font-stack-graphik`), and `.reader-body` in `style.css` uses
  `var(--reader-font-family, var(--font-serif))`. Picker relabeled "Reader Font".
- **Done when:** changing the reader font never changes the chat font (and vice
  versa), and it survives restart. ✔

### 2. Pin system for channels and posts
- **Channels:** `togglePin()` persists to `pins.channels`; `_rebuild_chat_list`
  floats pinned channels into a top section. `ChatRow.qml` already renders the
  pin badge.
- **Posts:** `toggleMessagePin(url)` persists to `pins.messages`; `MessageModel`
  exposes a `pinned` role. `ChatView.qml` shows a pinned-posts bar under the
  header; `MessageBubble.qml` + `MessageContextMenu.qml` add a Pin/Unpin action.
- **Done when:** pinned channels float to top, pinned posts appear in the pinned
  bar, both persist. ✔

### 3. Exact date of posts
- **Desktop:** `MessageBubble.qml` time shows `bridge._abs_datetime(...)`
  (`YYYY-MM-DD HH:MM`) with the full date in a tooltip; RTL-safe.
- **Web:** `formatTelegramDate()` now returns the absolute `YYYY-MM-DD HH:MM`;
  `renderNewsArticles` uses it for each post.
- **Done when:** no more "Yesterday"/relative labels. ✔

### 4. Sort posts old → new
- **Desktop:** `_rebuild_messages` sorts ascending by
  `_get_article_timestamp` (newest-first reverse removed); `ChatView.qml`
  auto-scrolls to the newest (bottom).
- **Web:** `filterNews` sorts `dA - dB` (ascending) and sets
  `latestArticle = articles[last]`.
- **Done when:** messages render oldest-first. ✔

### 5. Open-channel header avatar
- `bridge.py` `openChat` sets `currentChannelAvatar`; `ChatView.qml` header
  `Avatar` now uses the SAME resolution as the list row
  (`avatarPath: bridge.currentChannelAvatar`). ✔

### 6. Sport category → soccer-ball icon
- `gen_assets.py` gains a `soccer` entry (24×24 white-stroke, recolorable, no
  emoji) → `frontend/qml/assets/icons/soccer.svg`. `FolderRail.qml` maps the
  Sports tab to `soccer`. (Web nav tabs are text-only, so no web mirror needed.) ✔

### 7. Custom folders that combine channels
- `bridge.py` implements real folders: `createFolder/renameFolder/deleteFolder`,
  `addChannelToFolder/removeChannelFromFolder`, `getCustomFolders`,
  `getAllChannels`, persisted under `folders.custom` (was a no-op toast).
- `FolderRail.qml` renders each custom folder as a tab; selecting it filters the
  chat list. `FoldersPage.qml` manages create/rename/delete + channel chips. A
  new `AddToFolderDialog.qml` (opened from a chat row's right-click "Add to
  folder") assigns a channel to a folder. ✔

### 8. Custom background / wallpaper
- `bridge.py` `pickWallpaperImage()` opens a native file dialog, copies the
  image into `data/wallpapers/`, persists `appearance.wallpaper_image`, and sets
  `wallpaper_mode="image"`. `AppearancePage.qml` adds a "Custom wallpaper image"
  control; `ChatView.qml` paints it as the chat background. Built-in wallpapers
  remain. **Web:** wallpaper var mirrored. ✔

---

## Manual test checklist

- [ ] Settings → Appearance → Reader font: change it, open an article — only the
      reader text changes; chat list font unchanged. Restart → still applied.
- [ ] Right-click a channel → Pin; it jumps to a pinned section at the top.
      Restart → still pinned.
- [ ] Right-click a post → Pin post; it appears in the pinned bar above the
      messages. Unpin removes it. Restart → still pinned.
- [ ] Open any channel — each post shows an absolute `YYYY-MM-DD HH:MM`
      (hover/tooltip shows full date). Persian/RTL still reads correctly.
- [ ] Posts are ordered oldest→newest and the view starts at the newest (bottom).
- [ ] Open a channel — the header avatar shows the real image, not a plain
      initial.
- [ ] The Sports tab shows a soccer-ball icon that recolors with the theme.
- [ ] Settings → Folders: create a folder, add channels; it appears as a tab in
      the left rail and filters the chat list. Rename/delete work. Restart →
      persists.
- [ ] Right-click a channel → Add to folder → toggle membership / create new.
- [ ] Settings → Appearance → Custom wallpaper image: pick a file; it becomes the
      chat background. Built-in wallpapers still selectable. Restart → persists.
- [ ] Web viewer: reader font picker changes only article text; post dates are
      absolute; posts ascending.

## Backup / restore

A pre-change backup of the original repo was taken before any edits. To roll
back, restore your own backup ZIP over this folder. This delivery only adds/edits
the files listed above; it removes nothing and adds no dependencies.

## Open questions

- Web nav is category-tab text only, so the soccer icon (item 6) is desktop-only
  by design — confirm you don't also want icons added to the web tab bar.
- Custom-folder filtering on the web viewer was out of scope (folders are a
  desktop-rail concept); say the word if you want web folder tabs too.
