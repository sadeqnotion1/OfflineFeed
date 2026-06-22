# Graphify — build/refresh the OfflineFeed knowledge graph

> Repo-ready condensation of your Notion skill "Graphify Protocol — Build a Repo Knowledge Graph".
> The Notion page remains the source of truth; this file is what the session lead loads in-repo.
> Distilled from safishamsi/graphify (MIT).

## Purpose / when to invoke
This skill takes a repo (or a set of changed files) and produces a queryable knowledge graph
(`graph.json` + `GRAPH_REPORT.md` + optional `graph.html`) so you reason by *querying structure*
instead of re-reading source.
Trigger phrases: "map this repo", "how does X connect to Y", "what's the architecture",
"build/refresh the graph", "update the graph after this change".

## Inputs
- Required: repo root (default: this repo) and write access to `.agents/graph/`.
- Optional (default): scope = changed files only when refreshing; full tree on first build.

## Procedure
1. **Scope** — enumerate the tree; respect `.gitignore`/`.graphifyignore`; skip `node_modules/`,
   build output, vendored/generated files. Bucket by code / schema / infra / config / docs.
2. **Structural extraction (EXTRACTED)** — parse code AST-style; emit `imports`/`calls`/`inherits`/
   `implements`/`instantiates` edges you can read literally. Lean on this as ground truth.
3. **Semantic & rationale (the "why")** — from docstrings and `# NOTE/WHY/HACK/TODO`, create
   `rationale`/`concept` nodes linked with `explains`; create `table`/`resource`/`endpoint`/`config`
   nodes and cross-link layers (function → endpoint → config → doc).
4. **Communities** — cluster densely-connected nodes; give each a real name
   (e.g. `backend`, `bridge`, `ui`, `bootstrap`, `diagnostics`, `config`).
5. **Insights** — derive god nodes (rank by `degree`), surprising cross-community edges, and 4–5
   suggested questions.
6. **Emit artifacts** — write the three outputs below, then run the validator.

## Output
- Files: `.agents/graph/graph.json` (source of truth), `.agents/graph/GRAPH_REPORT.md` (digest),
  `.agents/graph/graph.html` (via `python .agents/graph/render_graph.py`).
- **`graph.json` MUST include all four top-level keys** (this is the fix vs. the current file, which
  omits `communities` + `insights`):
  ```json
  {
    "meta":  { "repo": "...", "generated": "ISO-8601", "node_count": 0, "edge_count": 0 },
    "nodes": [{ "id": "...", "label": "...", "type": "...", "location": "path:line",
                "community": "...", "summary": "...", "degree": 0 }],
    "edges": [{ "source": "...", "target": "...", "type": "...",
                "confidence": "EXTRACTED|INFERRED|AMBIGUOUS", "evidence": "..." }],
    "communities": [{ "id": "backend", "name": "Feed Server backend & scrapers", "node_ids": ["..."] }],
    "insights": { "god_nodes": ["..."], "surprising_connections": [{ "edge": ["a","b"], "why": "..." }],
                  "suggested_questions": ["..."] }
  }
  ```

## Rules & guardrails
- Never assert an edge without `evidence`. Tag every edge's `confidence`; code edges should be
  `EXTRACTED`, guesses `INFERRED`/`AMBIGUOUS` — never silently guess.
- Compute `degree` from the emitted edges (don't hand-set it, or it drifts).
- Refresh **incrementally**: re-extract only changed files and union-merge. Don't shrink the graph
  silently — if a rebuild has fewer nodes, confirm files were actually deleted before replacing.
- Every edge endpoint must be an existing node `id`.
- Direct chat instructions override this page.

## Quality checklist
- [ ] Ignore rules respected; no `node_modules`/build noise as nodes.
- [ ] Every edge has `confidence` + `evidence`; code edges are `EXTRACTED`.
- [ ] Communities have real names; god nodes / surprising connections / suggested questions filled.
- [ ] Cross-layer edges exist where applicable (code ↔ config ↔ endpoint ↔ doc).
- [ ] `graph.json` includes `meta`, `nodes`, `edges`, `communities`, `insights` and is self-consistent.
- [ ] `render_graph.py` runs with **no dangling-edge warnings**.
- [ ] `graph.json` + `GRAPH_REPORT.md` committed.

## References
- Notion: "Graphify Protocol — Build a Repo Knowledge Graph (AI Skill)" (source of truth).
- safishamsi/graphify · `docs/how-it-works.md` · `ARCHITECTURE.md`.
