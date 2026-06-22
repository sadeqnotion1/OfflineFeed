# Skills Registry

Skills are specialized, reusable playbooks the session lead can load for specific task types.
During boot, the AI reads this index; if a skill matches the task in `NEXT.md`, it loads that
skill's `SKILL.md` and follows it **exactly**. If none match, it says "none found" and proceeds
with PLAYBOOK defaults.

> Configured for OfflineFeed · https://github.com/sadeqnotion1/OfflineFeed

## How to use
1. Match the `NEXT.md` task against the **When to use** column below.
2. Open `skills/<name>/SKILL.md` and follow it step by step.
3. If a skill has scripts/refs, run/read them as instructed inside `SKILL.md`.
4. Loading a skill is not enough — **apply its checklist** and report the outcome.

## Registered skills

| Skill | When to use | Path | Canonical source |
|-------|-------------|------|------------------|
| graphify | Map the repo / keep the knowledge graph fresh after any structural change; answer "how does X connect to Y" / "what's the architecture" | `skills/graphify/SKILL.md` | Notion: "Graphify Protocol" |
| ui-animation-review | Any frontend/QML work (ROADMAP M1–M8): review motion, micro-interactions, theming, focus/contrast, reduced-motion before declaring UI done | `skills/ui-animation-review/SKILL.md` | Notion: "Design Engineering & Animation Review" |
| _template | Reference for authoring new skills (not a real skill) | `skills/_template/SKILL.md` | — |

> Keep "When to use" specific enough that matching is unambiguous.

## Status / TODO
- `graphify/SKILL.md` — ✅ included (repo-ready, condensed from your Graphify Protocol page).
- `ui-animation-review/SKILL.md` — ⚠️ **stub**. Paste the body of your Notion page
  "Design Engineering & Animation Review — Skill (emilkowalski/skills)" into it. It wasn't
  duplicated here to avoid shipping a fabricated copy.

## Authoring a new skill
1. Copy `skills/_template/` to `skills/<your-skill>/`.
2. Fill in `SKILL.md` (purpose, when-to-use, inputs, procedure, output, guardrails, checklist).
3. Add a row to the table above.
