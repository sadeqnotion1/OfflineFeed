# PROMPTS — the two prompts that run the loop
> Repo: https://github.com/sadeqnotion1/OfflineFeed
>
> Copy/paste these. **① START** at the top of every new chat. **② WRAP-UP** when the AI
> posts a 🔔 NEW CHAT NOTICE. The clean copies also live in `prompts/start.md` and `prompts/wrap-up.md`.

---

## ① START — paste at the top of every new chat
```
Project: OfflineFeed — repo: https://github.com/sadeqnotion1/OfflineFeed
Context source: the .agents/ folder. Pull it from the repo above (path .agents/),
or use what I've attached/pasted. Never improvise project state — if a file isn't
on GitHub and isn't attached, ask me for it by name.

Before doing anything, read these (in order), then report back:
- .agents/AGENTS.md            (repo + graph orientation)
- .agents/brain/STATE.md       (where we are)
- .agents/brain/NEXT.md        (the one next task + what to give you)
- .agents/brain/ROADMAP.md     (current milestone only)
- .agents/brain/PLAYBOOK.md    (roles + session loop)
- .agents/brain/DECISIONS.md   (the "why" — skim latest)
- .agents/graph/graph.json     (query as needed; do NOT dump it)
- .agents/skills/index.md      (load a matching skill, or say "none found")

Report back in this exact shape (Markdown, concise, no code/edits):
- (a) Current state — 3–5 lines from STATE.md + active ROADMAP milestone.
- (b) The single next task — restate NEXT.md intent + acceptance/"done" criteria.
- (c) Applicable skill — name it, or "none found".
- (d) Need from you — precise files/decisions/access still required to start.

Then stop and wait for my go-ahead, unless PLAYBOOK.md marks the task auto-proceed.

Working rules: Follow PLAYBOOK.md and my Delivery Standard. Work on ONLY the task in
NEXT.md — no "while I'm here" changes. Query the graph, don't dump it. Keep edits
minimal, additive, anchored; back up before destructive changes; never break the
working run.bat / run.sh or the :8080 backend.

New-chat protocol: When context gets ~80% full OR we finish the milestone, post a
line beginning exactly 🔔 NEW CHAT NOTICE, say why (context vs. milestone), and
wait for my wrap-up prompt before stopping.

This prompt is overridden by my direct chat instructions.
```

## ② WRAP-UP — paste when I post 🔔 NEW CHAT NOTICE
```
Wrap up this session so the next chat resumes with zero context loss. Do all of:
1. Update .agents/brain/STATE.md  — statuses, what changed, what now works.
2. Update .agents/brain/NEXT.md   — the single next task + what to hand me + done criteria.
3. Append to .agents/brain/SESSION_LOG.md — date, what we did, verified result, exact stop point.
4. If a real decision was made, append it to DECISIONS.md (new Dn entry, append-only).
5. If milestones changed, update ROADMAP.md (mark ✅ / move ← NEXT).
6. If code structure changed, update graph/graph.json (and note to regenerate graph.html).

Return the updated files (or exact diffs) plus a one-paragraph recap. Then stop —
don't start new work. Base everything ONLY on what we actually verified this session.
```
