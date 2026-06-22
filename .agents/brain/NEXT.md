# NEXT — the handoff card
_This is the FIRST thing to act on in a new chat (after the START prompt).
The AI rewrites this at the end of every session._

> Repo: https://github.com/sadeqnotion1/OfflineFeed

## ➡️ The one next task
**M1 — Window chrome & theme foundation.** Land the visual base the rest of the roadmap sits on:
rounded app window (R1.1), make Tinted vs Night themes visibly distinct (R1.2), unify all
settings sub-cards to rounded corners (R1.3), widen the left rail so labels like "Entertainment"
fit (R1.4), and give the window close button a distinct icon (R1.5). Pick the smallest subset that
ships cleanly first if M1 is too big for one chat (suggest R1.1 + R1.3 together).

## Start the next chat with this
> "Let's do M1 — window chrome & theme. Start with R1.1 (rounded app window) and R1.3 (all settings sub-cards rounded). Show me the QML you'll touch before editing."

## What to paste / give me at the start
Pull these from the repo (or paste them):
1. `frontend/qml/Main.qml` — the top-level window / frame (R1.1, R1.5).
2. `frontend/qml/themes/` (theme files) — Tinted vs Night palettes (R1.2).
3. `frontend/qml/components/` — the settings card component(s) + left rail (R1.3, R1.4).
4. A screenshot of the current window + Settings + left rail, so I match the real look.

## Decisions I need from you for this task
- **Frameless window?** Rounding usually means a frameless window + custom titlebar. OK to go frameless on Windows, or keep the native frame and round only inner content?
- **Corner radius token** — one value for everything (e.g. 12px)? Any existing radius token in the theme to reuse?
- **Tinted vs Night** — what should actually differ (accent tint, background warmth, contrast)?

## Definition of done for this task
- App window renders with rounded corners; drag/resize/min/max still work; no console errors.
- Tinted and Night themes are clearly distinguishable.
- All settings sub-cards share one rounded radius; left-rail labels no longer clip.
- Window close button has a distinct icon from in-app close icons.
- Existing features unchanged; app still launches via `run.bat` / `./run.sh`. Brain updated (STATE/NEXT/SESSION_LOG).
