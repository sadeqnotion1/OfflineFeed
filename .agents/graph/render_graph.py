#!/usr/bin/env python3
"""
render_graph.py -- turn .agents/graph/graph.json into a browsable graph.html.

Dependency-free (standard library only). Renders an interactive radial layout
using inline SVG + vanilla JS, so it opens offline in any browser.

Usage:
    python .agents/graph/render_graph.py            # writes graph.html next to graph.json
    python .agents/graph/render_graph.py --open      # also try to open it in the browser

This is a clean, self-contained renderer shipped with the OfflineFeed brain. Edit
graph.json (not this script) to change the map.
"""
from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH_JSON = HERE / "graph.json"
GRAPH_HTML = HERE / "graph.html"

LAYER_COLORS = {
    "backend": "#06B6D4",
    "frontend": "#8B5CF6",
    "infra": "#22C55E",
}
DEFAULT_COLOR = "#94A3B8"

# The HTML/CSS/JS shell. Placeholders __PROJECT__ / __DATA__ / __COLORS__ /
# __DEFAULT__ are filled by str.replace (no .format, so braces stay literal).
HTML_SHELL = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__PROJECT__ - knowledge graph</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; background: #0A0A14; color: #E2E8F0;
         font-family: Inter, system-ui, Segoe UI, Arial, sans-serif; }
  header { padding: 20px 24px 8px; }
  header h1 { margin: 0; font-size: 18px; letter-spacing: .2px; }
  header p { margin: 6px 0 0; font-size: 13px; color: #94A3B8; }
  #legend { display: flex; gap: 16px; padding: 8px 24px 0; flex-wrap: wrap; font-size: 12px; color: #CBD5E1; }
  #legend span { display: inline-flex; align-items: center; gap: 6px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
  #wrap { position: relative; padding: 8px 12px 24px; }
  svg { width: 100%; height: auto; max-height: 78vh; display: block; }
  line { stroke: #334155; stroke-width: 1.2; opacity: .7; }
  circle { cursor: pointer; stroke: #0A0A14; stroke-width: 2; transition: r .15s ease; }
  text.lbl { fill: #CBD5E1; font-size: 10px; pointer-events: none; }
  #tip { position: fixed; max-width: 320px; padding: 10px 12px; border-radius: 10px;
         background: #111827; border: 1px solid #334155; color: #E2E8F0; font-size: 12px;
         pointer-events: none; opacity: 0; transition: opacity .15s ease; z-index: 9; }
  #tip b { color: #fff; }
  @media (prefers-reduced-motion: reduce) { circle, #tip { transition: none; } }
</style>
</head>
<body>
<header>
  <h1>__PROJECT__ - knowledge graph</h1>
  <p>Query, don't dump. Hover a node for its description. Edit graph.json to change this map.</p>
</header>
<div id="legend"></div>
<div id="wrap">
  <svg id="svg" viewBox="0 0 1000 640" preserveAspectRatio="xMidYMid meet"></svg>
  <div id="tip"></div>
</div>
<script>
const GRAPH = __DATA__;
const COLORS = __COLORS__;
const DEFAULT = "__DEFAULT__";
const SVGNS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("svg");
const tip = document.getElementById("tip");
const W = 1000, H = 640, cx = W / 2, cy = H / 2, R = Math.min(W, H) * 0.38;
const nodes = GRAPH.nodes || [], edges = GRAPH.edges || [];
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
  const a = pos[e.from], b = pos[e.to];
  if (!a || !b) return;
  svg.appendChild(el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y }));
});
nodes.forEach(function (n) {
  const p = pos[n.id];
  const color = COLORS[n.layer] || DEFAULT;
  const c = el("circle", { cx: p.x, cy: p.y, r: 9, fill: color });
  c.addEventListener("mouseenter", function () { c.setAttribute("r", 12); });
  c.addEventListener("mousemove", function (ev) {
    tip.style.opacity = 1;
    tip.style.left = (ev.clientX + 14) + "px";
    tip.style.top = (ev.clientY + 14) + "px";
    tip.innerHTML = "<b>" + n.id + "</b><br>" + (n.type || "") + " · " + (n.layer || "") +
                    "<br>" + (n.desc || "");
  });
  c.addEventListener("mouseleave", function () { c.setAttribute("r", 9); tip.style.opacity = 0; });
  svg.appendChild(c);
  const short = n.id.split("/").filter(Boolean).pop();
  const t = el("text", { x: p.x + 12, y: p.y + 3 });
  t.setAttribute("class", "lbl");
  t.textContent = short;
  svg.appendChild(t);
});
const legend = document.getElementById("legend");
Object.keys(COLORS).forEach(function (k) {
  const s = document.createElement("span");
  s.innerHTML = '<i class="dot" style="background:' + COLORS[k] + '"></i>' + k;
  legend.appendChild(s);
});
</script>
</body>
</html>
"""


def load_graph() -> dict:
    if not GRAPH_JSON.exists():
        sys.exit("[render_graph] graph.json not found at %s" % GRAPH_JSON)
    try:
        return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit("[render_graph] graph.json is not valid JSON: %s" % e)


def build_html(graph: dict) -> str:
    project = str(graph.get("project", "Project"))
    payload = json.dumps({"nodes": graph.get("nodes", []), "edges": graph.get("edges", [])})
    return (
        HTML_SHELL.replace("__PROJECT__", project)
        .replace("__DATA__", payload)
        .replace("__COLORS__", json.dumps(LAYER_COLORS))
        .replace("__DEFAULT__", DEFAULT_COLOR)
    )


def main() -> None:
    graph = load_graph()
    GRAPH_HTML.write_text(build_html(graph), encoding="utf-8")
    print(
        "[render_graph] wrote %s (%d nodes, %d edges)"
        % (GRAPH_HTML, len(graph.get("nodes", [])), len(graph.get("edges", [])))
    )
    if "--open" in sys.argv:
        webbrowser.open(GRAPH_HTML.as_uri())


if __name__ == "__main__":
    main()
