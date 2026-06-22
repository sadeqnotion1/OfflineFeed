# NEXT — the handoff card
_This is the FIRST thing to act on in a new chat (after the START prompt).
The AI rewrites this at the end of every session._

> Repo: https://github.com/sadeqnotion1/OfflineFeed

## ➡️ The one next task
**M2 — Settings information architecture & consistency.** Clean up and unify settings views:
Unify settings pages into a single consistent visual styling (R2.1) and audit/fix mislabeled section
names (R2.2) (R2.3 is already completed).

## Start the next chat with this
> "Let's do M2 — Settings information architecture & consistency. Start by showing me the QML file layout for the settings components and how advanced vs simple pages currently differ in style."

## What to paste / give me at the start
Pull these from the repo:
1. `frontend/qml/components/SettingsView.qml` — the master settings registry and StackView.
2. `frontend/qml/components/AdvancedMergedPage.qml` — the combined advanced page.
3. `frontend/qml/components/AppearancePage.qml` — a representative simple settings page to use as a style base.

## Decisions I need from you for this task
- **Unified Style base:** Confirm that we want to use the card-based styling from `AppearancePage.qml` as the standard style template for all pages.
- **Section Mislabel Auditing:** Confirm if there are specific sections or fields to correct beyond the "Advanced has Advanced inside" naming bug.

## Definition of done for this task
- All settings sub-pages use a unified consistent visual design.
- Section names and labels corrected to remove duplication or naming bugs.
- "Advanced" row moved so it appears directly before the "Language" setting row in SettingsView.
- No console errors on settings navigation; app launches via `run.bat` / `run.sh`.
- Brain updated (STATE/NEXT/SESSION_LOG).
