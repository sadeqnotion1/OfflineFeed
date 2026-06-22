# graph/ — OfflineFeed knowledge graph

`graph.json` is the machine-readable map of OfflineFeed, built with the **Graphify Protocol**
(see `.agents/skills/graphify/SKILL.md`). Use it to answer "what calls what" / "where does X live" /
"how does a flow cross layers" **without** re-reading the whole repo. `GRAPH_REPORT.md` is the
human/AI digest (god nodes, communities, surprising connections, the "why", suggested questions).

## Schema (Graphify)
```json
{
  "meta":  { "repo": "sadeqnotion1/OfflineFeed", "generated": "ISO-8601",
             "node_count": 74, "edge_count": 134 },
  "nodes": [{ "id": "gui_server", "label": "gui_server.py", "type": "file",
              "location": "gui_server.py:1", "community": "backend",
              "summary": "...", "degree": 22 }],
  "edges": [{ "source": "bridge:_get", "target": "ep:news", "type": "calls",
              "confidence": "EXTRACTED", "evidence": "..." }]
}
```
- node `type`: `file` | `module` | `class` | `function` | `method` | `variable` | `table` | `resource` | `endpoint` | `config` | `concept` | `rationale` | `doc`
- node grouping key: **`community`** (e.g. `backend`, `bridge`, `ui`, `bootstrap`, `diagnostics`, `config`)
- edge endpoints: **`source`** / **`target`** (node ids)
- edge `type`: `imports` | `calls` | `inherits` | `implements` | `instantiates` | `reads` | `writes` | `references` | `configures` | `depends_on` | `explains`
- edge `confidence`: `EXTRACTED` (read from code) | `INFERRED` | `AMBIGUOUS`

## Query, don't dump
Never paste the whole file into a chat. Pull only what you need with `jq` (note the **real** field
names — `community`, `source`/`target`, `degree`):

```bash
# God nodes: most-connected hubs
jq '.nodes | sort_by(-.degree) | .[0:6] | .[] | {label, community, degree}' .agents/graph/graph.json

# Everything in the backend community
jq '.nodes[] | select(.community=="backend") | {label, summary}' .agents/graph/graph.json

# What does the bridge file talk to? (outgoing edges)
jq '.edges[] | select(.source|startswith("bridge")) | {source, target, type}' .agents/graph/graph.json

# Who touches thumbnails / images / avatars? (ROADMAP M3/M4)
jq '.nodes[] | select(.summary|test("thumbnail|image|avatar";"i")) | {label, location}' .agents/graph/graph.json

# Only the guessed edges (verify before trusting)
jq '.edges[] | select(.confidence!="EXTRACTED")' .agents/graph/graph.json
```

## Regenerate the visual
```bash
python .agents/graph/render_graph.py        # writes .agents/graph/graph.html (colors by community, sizes by degree)
```
The renderer validates that every edge endpoint is a real node id and warns on dangling edges.
Open `graph.html` in a browser. Keep `graph.json` + `GRAPH_REPORT.md` in sync after structural
code changes — re-run Graphify incrementally (don't shrink the graph silently).
