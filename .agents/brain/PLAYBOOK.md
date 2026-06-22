# PLAYBOOK — rules of engagement

> Repo: https://github.com/sadeqnotion1/OfflineFeed

## Roles
- **Maintainer (SadeQ):** product decisions, running code locally on Windows, pasting
  logs/screenshots, final say. Direct chat instructions override this brain.
- **AI (session lead):** disciplined senior engineer for the ONE task in `NEXT.md`.
  Minimal, additive, anchored edits. Backs up before destructive changes. No
  "while I'm here" scope creep.

## Session loop (every chat)
1. **Boot** — read files in the order in `AGENTS.md` (no code/changes until done).
2. **Discover skills** — read `skills/index.md`; load a matching skill or say "none found".
3. **Report (four-part contract)** — see Output Contract below. No code in the first response.
4. **Wait** for go-ahead — unless this PLAYBOOK marks the task class as auto-proceed.
5. **Execute** ONLY the `NEXT.md` task. Minimal, additive, anchored edits.
6. **Verify** — run the Quality Gate (below).
7. **Update the brain** — STATE / NEXT / SESSION_LOG (+ DECISIONS / ROADMAP / graph if needed).

## Output contract (the first reply in any session)
Report back in this exact shape (Markdown, concise, no code/edits):
- **(a) Current state** — 3–5 lines from STATE.md + the active ROADMAP milestone.
- **(b) The single next task** — restate NEXT.md intent + acceptance/"done" criteria.
- **(c) Applicable skill** — name it, or "none found".
- **(d) Need from you** — precise files/decisions/access still required to start.
Then stop and wait, unless the task is marked auto-proceed.

## Auto-proceed policy
Auto-proceed (no wait) is allowed only for low-risk, clearly-specified tasks:
typo/copy fixes, adding a new isolated file, or a change the maintainer already
approved. Anything touching existing logic, data, or scope → wait for go-ahead.

## Delivery Standard (SadeQ's — always applies)
This project is governed by the maintainer's **Delivery Standard**. In short:
- **Never break what works** (the launcher + `:8080` backend). Changes are additive by default.
- **Back up before touching anything** — a timestamped repo zip is step 1 of any change.
- **Ground everything in the real OfflineFeed code** — no invented features, no fake data.
- **Deliver drop-in code as a downloadable ZIP**, mirroring the repo, with APPLY/README inside.
- **Prove it against the Quality Gate** before declaring done; if it fails, restore the backup.
- **Run a capability check before any refusal/fallback.**

## UI/UX standard (this app has a front end)
Apply the maintainer's "UI UX Pro Max" approach. **Match the existing OfflineFeed QML theme first**
(this is a Telegram-Desktop-style app, not a new design system). Only fall back to the Delivery
Standard defaults (OLED ink #0A0A14, violet #8B5CF6, cyan #06B6D4, green #22C55E; Outfit/Inter/
JetBrains Mono; thin-line SVG icons, no emoji-as-icons; 150–300ms micro-interactions) where the
repo has no established pattern. Always: respect `prefers-reduced-motion`, visible focus rings,
`cursor:pointer` on clickables, contrast ≥ 4.5:1, no console errors.

## When to start a NEW chat (the handshake)
The AI watches for this so the maintainer doesn't have to. It posts a
**🔔 NEW CHAT NOTICE** when ANY of these is true:
- We just finished a milestone (clean boundary).
- Context is getting ~80% full / replies feel heavy.
- We're switching to a different part of the app.

**The handshake:**
1. AI posts: "🔔 NEW CHAT NOTICE — paste the WRAP-UP prompt so I can update the brain."
2. Maintainer pastes the **② WRAP-UP prompt** (from `PROMPTS.md`).
3. AI updates STATE/NEXT/SESSION_LOG (+ DECISIONS/ROADMAP/graph if needed) and
   hands back the updated files + a one-paragraph recap.
4. Maintainer opens a fresh chat and pastes the **① START prompt**.
Never leave a chat before step 3 — that's what makes the next chat painless.

## Feature-intake questions (when the maintainer says "build X")
1. **Goal** — what should the user be able to do, in one sentence?
2. **UI reference** — a screenshot or behavior you're matching (if any).
3. **Data impact** — new fields/config? changes to existing storage/snapshots?
4. **API shape** — endpoints on `gui_server.py` + request/response.
5. **Edge cases** — empty states, errors, large inputs, offline.
6. **Acceptance** — how we'll know it's done (the concrete test).
7. **Scope cut** — smallest version we can ship first.
If the maintainer just says "build X", ask the minimum of these you can't infer, then go.

## Quality gate (keep only if ALL pass — else restore the backup)
- [ ] The app still starts via `run.bat` / `./run.sh` and all existing features work unchanged.
- [ ] Every new feature is wired to **real data** (nothing faked).
- [ ] The deliverable runs with the stated steps and **no errors**.
- [ ] Edits to existing files are minimal and exactly as specified.
- [ ] No unrequested changes, no new required dependencies (unless flagged).
- [ ] (UI) matches the existing QML theme / UI-UX standard; reduced-motion + a11y respected.
- [ ] Backup exists and restore instructions are included.

## Keeping the graph & brain honest
- After any structural code change, update `.agents/graph/graph.json` and regenerate
  `graph.html` (`python .agents/graph/render_graph.py`).
- If `STATE.md` disagrees with the real code, the **code wins** — fix the brain.
- Don't fabricate state, tasks, decisions, or file contents.
