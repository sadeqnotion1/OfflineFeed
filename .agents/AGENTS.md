# AGENTS.md — Repo & Graph Orientation

> Read this **first** in every session. It tells you what the repo is, where the
> brain lives, and how to load context in the right order. Do not write code or
> propose changes until you have completed the boot sequence below.

## Project

- **Name:** OfflineFeed
- **Repo:** https://github.com/sadeqnotion1/OfflineFeed
- **One-line purpose:** Windows-first desktop app that pulls RSS / news / X(Twitter) / Telegram channels, stores them for offline reading, and can forward content to Telegram — a Telegram-Desktop-style three-pane reader.
- **Primary stack:** PySide6 + QML desktop frontend + local Python HTTP backend (Feed Server on 127.0.0.1:8080).

## Boot sequence (in order, every session)

1. `brain/STATE.md`     → where we are
2. `brain/NEXT.md`      → the ONE next task + what to hand you
3. `brain/ROADMAP.md`   → the **current milestone only**
4. `brain/PLAYBOOK.md`  → roles + session loop + protocols
5. `brain/DECISIONS.md` → skim the latest decisions (the "why")
6. `graph/graph.json`   → **query as needed; never dump it in full**
7. `skills/index.md`    → discover skills; load one if it matches NEXT.md (say "none found" if absent)

## Prompts

- `prompts/start.md`   → the #START kickoff prompt.
- `prompts/wrap-up.md` → the #WRAP_UP closing prompt.

## Repo layout (high level)

> Follows the Project Scaffolding Standard: minimal root, fewest folders, run files + README + .gitignore at root.

```text
OfflineFeed/
├── backend/                 # Feed Server + libs + tools + offline viewer + config
│   ├── run_offlinefeed.py   # smart launcher (diagnose -> launch); run.bat/run.sh call this
│   ├── gui_server.py        # HTTP API on 127.0.0.1:8080; fetch/dedupe/cache/thumbnails/retention
│   ├── offline_reader.py    # server-rendered offline reader page (deep link ?reader=...)
│   ├── offline_viewer/      # offline web viewer assets (HTML/JS + JSON)
│   ├── twscrape/            # twscrape RSS shim for X(Twitter) (Path B, 127.0.0.1:8081)
│   ├── feed_store.py        # durable feed snapshot persistence
│   ├── cache_retention.py   # archive/zip old cached posts (>14d)
│   └── docs/                # DEBUG.md, design notes
├── frontend/                # the desktop UI only
│   ├── app.py               # PySide6 app entry / bootstrap (attaches to backend on :8080)
│   ├── bridge.py            # QObject slots/signals bridge (UI <-> backend)
│   ├── qml/                 # Main.qml, themes/, components/, assets/
│   ├── debug.py             # debug logging
│   └── doctor.py            # diagnostics (python -m frontend.doctor)
├── .agents/                 # this brain
├── run.bat / run.sh         # thin wrappers -> python backend/run_offlinefeed.py (ALREADY WORKING)
├── README.md
└── .gitignore
```

## Graph orientation

- The knowledge graph (`graph/graph.json`) maps modules, files, and their relationships.
  Use it to answer "what calls what" / "where does X live" **without** reading the whole codebase.
- **Query, don't dump.** Pull only the nodes/edges you need. See `graph/README.md`.
- Regenerate the visual `graph/graph.html` with `python .agents/graph/render_graph.py`.

## Hard rules (summary — full rules in PLAYBOOK.md)

- Work on **only** the task in `NEXT.md`. No "while I'm here" changes.
- Don't fabricate state, tasks, decisions, or file contents.
- Keep edits minimal, additive, anchored. Back up before destructive changes.
- Never break what already works — especially the working `run.bat` / `run.sh` and `gui_server.py` on :8080.
- A direct chat instruction from the maintainer overrides this brain.

## Project Rules (from .agent)

- **No Temporary Files in Root**: Do not create temporary folders or backup directories (such as `backup_*`) directly in the project root directory.
- **Immediate Cleanup**: Any backup directories created during fix execution must be completely cleaned up/deleted once the task is finished.
- **Use Scratch Directory**: For temporary file creation or processing, utilize the designated scratch directory (`<appDataDir>\brain\<conversation-id>/scratch/`) instead of the project repository.

