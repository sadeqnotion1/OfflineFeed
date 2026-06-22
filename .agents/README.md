# `.agents/` — the OfflineFeed project brain

This folder is the AI's memory and operating manual for OfflineFeed. It lets any AI chat
(or any model) boot with full project context and continue work with **zero context loss**.

## The loop
1. AI reads `AGENTS.md` → `brain/STATE.md` → `brain/NEXT.md` → `brain/ROADMAP.md`
   (current milestone only) → `brain/PLAYBOOK.md`.
2. AI queries `graph/graph.json` only for the nodes/edges it needs (never dumps it).
3. AI discovers `skills/` and loads a matching skill, or declares "none found".
4. AI reports the four-part status (a/b/c/d) and waits, unless PLAYBOOK says proceed.
5. After the task, AI updates `STATE.md`, `NEXT.md`, `SESSION_LOG.md` (+ `DECISIONS.md` / graph).

## The two prompts
- **① START** — paste at the top of every new chat (`prompts/start.md`). The AI reads the brain and
  restates the current task.
- **② WRAP-UP** — paste when the AI posts a 🔔 NEW CHAT NOTICE (`prompts/wrap-up.md`). The AI updates
  the whole brain so the next chat continues seamlessly.

Full copies of both also live in `brain/PROMPTS.md`.

## Files
```text
.agents/
├── AGENTS.md           # read first — project block + boot sequence + repo layout
├── README.md           # this file
├── CHANGELOG.md        # brain version log
├── brain/
│   ├── STATE.md        # where we are right now (source of truth; code wins on conflict)
│   ├── NEXT.md         # the ONE next task (no multitasking)
│   ├── ROADMAP.md      # milestones M1–M10 (the 23-item list, mapped to real code)
│   ├── PLAYBOOK.md     # rules of engagement + Delivery Standard + Quality Gate
│   ├── DECISIONS.md    # append-only "why" record (ADR)
│   ├── SESSION_LOG.md  # append-only session history
│   └── PROMPTS.md      # the ① START and ② WRAP-UP prompts
├── graph/
│   ├── graph.json      # conceptual map of OfflineFeed's real modules
│   ├── render_graph.py # turns graph.json into a browsable graph.html (no deps)
│   └── README.md       # query-don't-dump recipes
└── prompts/
    ├── start.md        # ① START
    └── wrap-up.md      # ② WRAP-UP
```

## Maintenance contract
- Keep files **small and current**. STATE/NEXT are living docs; prune aggressively.
- `DECISIONS.md` and `SESSION_LOG.md` are append-only. Never rewrite history; add a new entry.
- Edits to the brain are **minimal, additive, anchored**. Back up before destructive change.

_Brain v2 · configured for OfflineFeed on 2026-06-22._
