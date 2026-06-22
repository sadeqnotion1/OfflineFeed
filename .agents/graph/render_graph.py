#!/usr/bin/env python3
"""
render_graph.py -- turn .agents/graph/graph.json into a browsable graph.html.

Dependency-free (standard library only). Renders an interactive radial layout
using inline SVG + vanilla JS, so it opens offline in any browser.

This version reads the **Graphify Protocol** schema that OfflineFeed's graph.json
actually uses:
  meta:  { repo, generated, node_count, edge_count, note }
  nodes: { id, label, type, location, community, summary, degree }
  edges: { source, target, type, confidence, evidence }

It is also backward-compatible with the older seed schema (nodes with `layer`/`desc`,
edges with `from`/`to`), so it works no matter which file is present.

Usage:
    python .agents/graph/render_graph.py            # writes graph.html next to graph.json
    python .agents/graph/render_graph.py --open      # also try to open it in the browser

Edit graph.json (not this script) to change the map. Regenerate the graph itself
with the Graphify Protocol skill (see .agents/skills/graphify/SKILL.md).
"""
from __future__ import annotations

import colorsys
import json
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH_JSON = HERE / "graph.json"
GRAPH_HTML = HERE / "graph.html"


def _node_group(n: dict) -> str:
    """Community is the Graphify grouping key; fall back to the old `layer`."""
    return str(n.get("community") or n.get("layer") or "other")


def _node_desc(n: dict) -> str:
    return str(n.get("summary") or n.get("desc") or "")


def _edge_ends(e: dict):
    """Graphify uses source/target; the old seed used from/to."""
    return e.get("source", e.get("from")), e.get("target", e.get("to"))


def _palette(groups: list[str]) -> dict:
    """Deterministic, evenly-spaced HSL palette so any number of communities is legible."""
    out = {}
    total = max(len(groups), 1)
    for i, g in enumerate(sorted(groups)):
        h = i / total
        r, gr, b = colorsys.hls_to_rgb(h, 0.62, 0.55)
        out[g] = "#%02X%02X%02X" % (int(r * 255), int(gr * 255), int(b * 255))
    return out


def validate(graph: dict) -> list[str]:
    """Quality gate from the Graphify skill: every edge endpoint must be a real node id."""
    ids = {n.get("id") for n in graph.get("nodes", [])}
    problems = []
    for e in graph.get("edges", []):
        s, t = _edge_ends(e)
        if s not in ids:
            problems.append("edge source not a node id: %r" % s)
        if t not in ids:
            problems.append("edge target not a node id: %r" % t)
    return problems


def load_graph() -> dict:
    if not GRAPH_JSON.exists():
        sys.exit("[render_graph] graph.json not found at %s" % GRAPH_JSON)
    try:
        return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("[render_graph] graph.json is not valid JSON: %s" % e)


HTML_SHELL = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; background: #0A0A14; color: #E2E8F0;
         font-family: Inter, system-ui, Segoe UI, Arial, sans-serif; }
  header { padding: 18px 24px 6px; }
  header h1 { margin: 0; font-size: 17px; }
  header p { margin: 6px 0 0; font-size: 12px; color: #94A3B8; }
  #legend { display: flex; gap: 14px; padding: 8px 24px 0; flex-wrap: wrap; font-size: 12px; color: #CBD5E1; }
  #legend span { display: inline-flex; align-items: center; gap: 6px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  #wrap { position: relative; padding: 8px 12px 24px; }
  svg { width: 100%; height: auto; max-height: 80vh; display: block; }
  line { stroke: #334155; stroke-width: 1; opacity: .6; }
  line.inferred { stroke-dasharray: 4 3; opacity: .45; }
  circle { cursor: pointer; stroke: #0A0A14; stroke-width: 1.5; transition: stroke-width .15s ease; }
  circle:hover { stroke: #fff; stroke-width: 2.5; }
  text.lbl { fill: #CBD5E1; font-size: 9px; pointer-events: none; }
  #tip { position: fixed; max-width: 340px; padding: 10px 12px; border-radius: 10px;
         background: #111827; border: 1px solid #334155; color: #E2E8F0; font-size: 12px;
         pointer-events: none; opacity: 0; transition: opacity .12s ease; z-index: 9; }
  #tip b { color: #fff; }
  #tip .meta { color: #94A3B8; }
  @media (prefers-reduced-motion: reduce) { circle, #tip { transition: none; } }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <p>__SUB__ Hover a node for details. Dashed edges are INFERRED. Edit graph.json to change the map.</p>
</header>
<div id="legend"></div>
<div id="wrap">
  <svg id="svg" viewBox="0 0 1100 720" preserveAspectRatio="xMidYMid meet"></svg>
  <div id="tip"></div>
</div>
<script>
const GRAPH = __DATA__;
const COLORS = __COLORS__;
const SVGNS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("svg");
const tip = document.getElementById("tip");
const W = 1100, H = 720, cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.40;
const nodes = GRAPH.nodes || [], edges = GRAPH.edges || [];
function grp(n) { return String(n.community || n.layer || "other"); }
function deg(n) { return Number(n.degree || 0); }
// Order nodes by community so clusters sit together around the ring.
nodes.sort(function (a, b) { return grp(a) < grp(b) ? -1 : grp(a) > grp(b) ? 1 : 0; });
const maxDeg = Math.max(1, ...nodes.map(deg));
const pos = {};
nodes.forEach(function (n, i) {
  const a = (2 * Math.PI * i) / Math.max(nodes.length, 1) - Math.PI / 2;
  pos[n.id] = { x: cx + R * Math.cos(a), y: cy + R * Math.sin(a) };
});
function el(tag, attrs) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  return e;
}
edges.forEach(function (e) {
  const s = e.source != null ? e.source : e.from;
  const t = e.target != null ? e.target : e.to;
  const a = pos[s], b = pos[t];
  if (!a || !b) return;
  const ln = el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y });
  if (e.confidence && e.confidence !== "EXTRACTED") ln.setAttribute("class", "inferred");
  svg.appendChild(ln);
});
nodes.forEach(function (n) {
  const p = pos[n.id];
  const color = COLORS[grp(n)] || "#94A3B8";
  const r = 5 + 9 * (deg(n) / maxDeg);
  const c = el("circle", { cx: p.x, cy: p.y, r: r, fill: color });
  c.addEventListener("mousemove", function (ev) {
    tip.style.opacity = 1;
    tip.style.left = (ev.clientX + 14) + "px";
    tip.style.top = (ev.clientY + 14) + "px";
    tip.innerHTML = "<b>" + (n.label || n.id) + "</b><br>" +
      "<span class='meta'>" + (n.type || "") + " · " + grp(n) +
      (n.degree != null ? " · degree " + n.degree : "") +
      (n.location ? "<br>" + n.location : "") + "</span><br>" +
      (n.summary || n.desc || "");
  });
  c.addEventListener("mouseleave", function () { tip.style.opacity = 0; });
  svg.appendChild(c);
  const short = (n.label || n.id).split("/").filter(Boolean).pop();
  const t = el("text", { x: p.x + (p.x >= cx ? 8 : -8), y: p.y + 3 });
  t.setAttribute("class", "lbl");
  if (p.x < cx) t.setAttribute("text-anchor", "end");
  t.textContent = short;
  svg.appendChild(t);
});
const legend = document.getElementById("legend");
Object.keys(COLORS).sort().forEach(function (k) {
  const s = document.createElement("span");
  s.innerHTML = '<i class="dot" style="background:' + COLORS[k] + '"></i>' + k;
  legend.appendChild(s);
});
</script>
</body>
</html>
"""


def build_html(graph: dict) -> str:
    meta = graph.get("meta", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    repo = meta.get("repo", graph.get("project", "Project"))
    title = "%s - knowledge graph" % repo
    sub = "%d nodes · %d edges." % (
        meta.get("node_count", len(nodes)),
        meta.get("edge_count", len(edges)),
    )
    groups = sorted({_node_group(n) for n in nodes})
    payload = json.dumps({"nodes": nodes, "edges": edges})
    return (
        HTML_SHELL.replace("__TITLE__", title)
        .replace("__SUB__", sub)
        .replace("__DATA__", payload)
        .replace("__COLORS__", json.dumps(_palette(groups)))
    )


def main() -> None:
    graph = load_graph()
    problems = validate(graph)
    if problems:
        print("[render_graph] WARNING: %d dangling edge endpoint(s):" % len(problems))
        for p in problems[:10]:
            print("  - " + p)
    GRAPH_HTML.write_text(build_html(graph), encoding="utf-8")
    print(
        "[render_graph] wrote %s (%d nodes, %d edges)"
        % (GRAPH_HTML, len(graph.get("nodes", [])), len(graph.get("edges", [])))
    )
    if "--open" in sys.argv:
        webbrowser.open(GRAPH_HTML.as_uri())


if __name__ == "__main__":
    main()
