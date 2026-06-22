# Brain Changelog

## v2 — 2026-06-22 — configured for OfflineFeed
- Filled `AGENTS.md` project block with the real OfflineFeed stack + repo layout.
- Captured the maintainer's 23-item bug/feature list into `ROADMAP.md` as milestones M1–M10,
  each mapped to real OfflineFeed files, with a traceability table.
- Seeded `STATE.md`, `NEXT.md`, `DECISIONS.md`, `SESSION_LOG.md` from the real project state.
- Seeded `graph/graph.json` with OfflineFeed's real modules + a dependency-free `render_graph.py`.
- Wrote `prompts/start.md`, `prompts/wrap-up.md`, and `brain/PROMPTS.md` pinned to the OfflineFeed repo.

## v2 — base scaffold (from CreateProject starter pack)
- `AGENTS.md` boot sequence with explicit read order.
- Brain split into STATE / NEXT / ROADMAP / PLAYBOOK / DECISIONS / SESSION_LOG / PROMPTS.
- Append-only DECISIONS.md (the "why" memory) + SESSION_LOG.md.
- graph/ with conceptual repo map + HTML renderer ("query, don't dump").
- Formalized New-Chat Protocol, Output Contract, Auto-proceed policy, Quality Gate.
