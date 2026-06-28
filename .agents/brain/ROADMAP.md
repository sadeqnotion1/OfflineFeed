# ROADMAP — ordered build plan

Build in order. Each milestone is small enough to finish in roughly one chat.
Don't start the next one until the current one's acceptance criteria pass.

> Repo: https://github.com/sadeqnotion1/OfflineFeed

> Every item below comes from the maintainer's real bug/feature list. Each maps to
> real OfflineFeed code (frontend QML/bridge or backend Feed Server) — nothing invented.
> Mark the active milestone with **← NEXT**. Keep finished ones ✅ with a one-liner.

---

## M1 — Window chrome & theme foundation ✅
_Visual base everything else sits on. Finished 2026-06-22._
- **True rounded frameless shell** (R1.1)
- **Cyberpunk Tinted theme** (R1.2)
- **Shared 14px card radius token** (R1.3)
- **84px folder rail** (R1.4)
- **Distinct window-close glyph** (R1.5)

## M2 — Settings information architecture & consistency ✅
_Unified all settings sub-pages with card-based layouts and rich icon-led section headers (R2.1), resolved Advanced inner section naming duplication by renaming it to System (R2.2), and placed Advanced before Language setting row (R2.3). Finished 2026-06-28._

## M3 — Icon hygiene ⬜ ← NEXT
_Icon set + where icons are chosen in `frontend/qml/components/` and channel/folder rows._

- **R3.1 — Back-to-back trash icons.** Two identical trash icons sitting next to each other read as one blob. Use distinct icons (or spacing/variant) so each action is clear.
- **R3.2 — Feed folder vs Custom folder share an icon.** In channel settings, give Feed folders and Custom folders **different** icons.
- **R3.3 — "Forward channel to Telegram" should be an icon.** Replace the text action with a single icon, and ideally surface it **only** in Channel Info (not on every row).
- **R3.4 — Channel avatar sizes inconsistent.** Some channel avatars render huge vs others; clamp to one fixed avatar size everywhere.

## M4 — Avatars & thumbnails (data correctness) ⬜
_Backend image pipeline (`backend/gui_server.py` `download_feed_thumbnails_async`, `feed_store`) + how the list/post/viewer read those fields._

- **R4.1 — Thumbnail list/post mismatch.** Sometimes the list thumbnail is missing but the image exists inside the opened post — and sometimes the reverse (thumb in list, none in the post body). Make the post image and the list thumbnail resolve from the same real source so they stay consistent.
- **R4.2 — X(Twitter) avatars are the platform default.** X account avatars show the generic default, not the real profile picture. Fetch/store the real avatar (via the twscrape/Nitter path) and fall back gracefully.

## M5 — Channel Info enhancements ⬜
_Channel Info / "manage" panel in `frontend/qml` + supporting `bridge.py` + `gui_server.py` endpoints/storage._

- **R5.1 — Per-channel Telegram target.** Let each channel configure its own `telegram_group` + `topic` inside the Channel Info section (where you manage image, etc.). Persist per channel.
- **R5.2 — Editable channel "About".** Add a real, channel-specific "About" in Channel Info, editable via a pen icon. Persist the text.

## M6 — Per-post Telegram sending ⬜
_Builds on R5.1 (per-channel target) + the existing Telegram forward path._

- **R6.1 — Send a single post to Telegram.** Each post gets its own "send to Telegram" action (uses the post's channel target from R5.1 when set).

## M7 — Post actions ⬜

- **R7.1 — Copy post content + images.** Add an action to copy a post's text content and its image(s) to the clipboard.

## M8 — Reader customization ⬜
_`backend/offline_reader.py` (server-rendered reader) + `backend/offline_viewer/` + in-app reader view._

- **R8.1 — Customizable reader.** The reader is too plain in both web and in-app. Add reader controls (font size, width, theme/spacing) so the user can customize it. Keep it offline (no CDN) and respect `prefers-reduced-motion`.

## M9 — Backend reliability ⬜
_`backend/twscrape/` + `gui_server.py` logging (`log_system_activity`)._

- **R9.1 — Stale X accounts.** Some X accounts (e.g. Fabrizio Romano) aren't up to date — likely a twscrape issue under many accounts. Diagnose account-pool / rate-limit handling and make high-volume handles refresh reliably.
- **R9.2 — System Log is wrongly a "channel".** Logging is currently modeled as a feed channel (wrong logic). Build proper in-app log tracking separate from channels.

## M10 — Loading & performance UX ⬜
_Fetch flow in `gui_server.py` (`ThreadPoolExecutor` fan-out) + how `bridge.py`/QML render progress._

- **R10.1 — Progressive channel appearance.** Today you wait for ALL channels (X or feed) to finish before seeing the first one. Stream results so each already-fetched account appears one-by-one as it completes.
- **R10.2 — Modern 2026 loading states.** Replace "pick a channel first" + plain spinners with modern skeleton/streaming loading states app-wide.

---

## Backlog / maybe-later
- (none captured yet — add ideas that are explicitly out of scope for the milestones above)

## How the 23 items map to milestones (traceability)
| Item (maintainer wording) | Milestone |
|---|---|
| App window square → round corners | R1.1 |
| Tinted & night theme not different | R1.2 |
| Some sub-settings square, some rounded | R1.3 |
| Left rail too small, "Entertainment" clipped | R1.4 |
| App close button icon like other close icons | R1.5 |
| Settings not one UI theme (advanced vs simple) | R2.1 |
| Naming errors (Advanced has Advanced inside) | R2.2 |
| Advanced placement → before Language | R2.3 |
| Back-to-back trash icons uncomfortable | R3.1 |
| Feed folder & custom folder same icon | R3.2 |
| "Forward channel to Telegram" → icon, in Channel Info | R3.3 |
| Avatar sizes huge vs others | R3.4 |
| Thumbnail missing in list/post (and reverse) | R4.1 |
| X avatars are platform default | R4.2 |
| Per-channel telegram_group + topic in Channel Info | R5.1 |
| Channel "About" + edit via pen icon | R5.2 |
| Send each post to Telegram individually | R6.1 |
| Copy post content + images | R7.1 |
| Reader not customizable / too plain | R8.1 |
| X accounts stale (Fabrizio Romano / twscrape) | R9.1 |
| System log is a channel (wrong logic) | R9.2 |
| Channels take ages; want one-by-one appearance | R10.1 |
| Better/advanced 2026 loading everywhere | R10.2 |
