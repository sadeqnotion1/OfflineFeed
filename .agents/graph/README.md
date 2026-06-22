# graph/ — OfflineFeed knowledge graph

`graph.json` is a small, hand-maintained conceptual map of OfflineFeed's real modules and how they
relate. Use it to answer "what calls what" / "where does X live" **without** reading the whole repo.

## Schema
```json
{
  "nodes": [{ "id": "backend/gui_server.py", "type": "file", "layer": "backend", "desc": "..." }],
  "edges": [{ "from": "frontend/bridge.py", "to": "backend/gui_server.py", "rel": "http" }]
}
```
- `type`: `file` | `module` | `service` | `concept`
- `layer`: `backend` | `frontend` | `infra`
- `rel`: `http` | `imports` | `renders` | `persists` | `launches` | `serves`

## Query, don't dump
Never paste the whole file into a chat. Pull only what you need, e.g. with `jq`:

```bash
# What does the bridge talk to?
jq '.edges[] | select(.from=="frontend/bridge.py")' .agents/graph/graph.json

# Everything in the backend layer
jq '.nodes[] | select(.layer=="backend")' .agents/graph/graph.json

# Who touches thumbnails / images? (relevant to ROADMAP R4.1)
jq '.nodes[] | select(.desc|test("thumbnail|image|avatar";"i"))' .agents/graph/graph.json
```

## Regenerate the visual
```bash
python .agents/graph/render_graph.py        # writes .agents/graph/graph.html
```
Then open `graph.html` in a browser. Keep `graph.json` in sync after any structural code change.
