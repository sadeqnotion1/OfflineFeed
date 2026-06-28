# NEXT — the handoff card
_This is the FIRST thing to act on in a new chat (after the START prompt).
The AI rewrites this at the end of every session._

> Repo: https://github.com/sadeqnotion1/OfflineFeed

## ➡️ The one next task
**M3 — Icon hygiene.** Resolve issues with visual duplication, shared folders icons, action labels, and avatar sizes:
- Distinct trash icons/spacing so back-to-back trash controls do not merge visually (R3.1).
- Distinct icons for Feed Folders vs Custom Folders in channel settings (R3.2).
- Replace "Forward channel to Telegram" text action with an icon, surfaced only in Channel Info (R3.3).
- Clamp channel avatar rendering sizes to a fixed size app-wide (R3.4).

## Start the next chat with this
> "Let's do M3 — Icon hygiene. Start by showing me the QML files where trash buttons are adjacent, where folder icons are resolved, and where the Telegram forward action and channel avatars are rendered."

## What to paste / give me at the start
Pull these from the repo:
1. `frontend/qml/components/ChatList.qml` and `frontend/qml/components/ChatRow.qml` — listing channels and folders.
2. `frontend/qml/components/InfoPanel.qml` — channel info panel showing Telegram options and avatar.
3. `frontend/qml/components/Avatar.qml` — the channel avatar renderer.

## Decisions I need from you for this task
- **Trash Icon Variant:** Confirm which icon or spacing should distinguish the two adjacent trash actions (e.g., delete from app vs empty cache).
- **Folder Icon Assignment:** Confirm which distinct SVGs from assets to assign to Feed folders vs Custom folders (e.g., folder.svg vs saved.svg or bots.svg).

## Definition of done for this task
- Back-to-back trash actions look distinct and clear.
- Feed folders and Custom folders use different visual icons.
- Telegram forward action on rows replaced by a single icon in the Channel Info panel.
- All channel avatars render with a consistent clamped size.
- Brain updated (STATE/NEXT/SESSION_LOG).
