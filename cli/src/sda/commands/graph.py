"""
sda graph — render the knowledge graph as a self-contained, interactive HTML file.

Usage:
  sda graph                       # write architecture/graph.html
  sda graph --output graph.html   # custom output path
  sda graph --open                # open in the default browser after writing

The output is a single offline file: Cytoscape.js and its fcose layout are inlined,
so there are no external/CDN requests. Edges include service-to-service `depends_on`.
"""

import json
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from sda.commands.index import assemble_graph

GRAPH_FILE = Path("architecture/graph.html")
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Vendored, MIT-licensed. Loaded in dependency order; fcose is registered at runtime.
_ASSET_FILES = [
    "layout-base.js",
    "cose-base.js",
    "cytoscape-fcose.js",
    "cytoscape.min.js",
]

_TYPE_META = {
    "problem": {"color": "#e8590c", "label": "Problem"},
    "adr": {"color": "#1c7ed6", "label": "ADR"},
    "service": {"color": "#2f9e44", "label": "Service"},
    "group": {"color": "#868e96", "label": "Group"},
}


def _to_elements(graph: dict) -> tuple[list[dict], dict]:
    """Convert the node-keyed graph into Cytoscape elements + summary stats."""
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()

    present = set(graph.keys())

    def add_edge(src: str, tgt: str, kind: str) -> None:
        if src not in present or tgt not in present or src == tgt:
            return
        key = (src, tgt, kind)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append({"data": {"id": f"{src}__{kind}__{tgt}", "source": src, "target": tgt, "kind": kind}})

    hotspots: list[tuple[str, int]] = []

    for key, node in graph.items():
        ntype = node.get("type", "service")
        data = {"id": key, "label": key, "ntype": ntype}
        if node.get("system"):
            data["system"] = node["system"]
        if node.get("group"):
            data["group"] = node["group"]
        nodes.append({"data": data})

        if ntype == "problem":
            for adr in node.get("linked_adrs", []):
                add_edge(key, adr, "addresses")
            for svc in node.get("services", []):
                add_edge(key, svc, "affects")
        elif ntype == "adr":
            for prob in node.get("linked_problems", []):
                add_edge(prob, key, "addresses")
            for svc in node.get("linked_services", []):
                add_edge(key, svc, "affects")
        elif ntype == "service":
            for dep in node.get("depends_on", []):
                add_edge(key, dep, "depends_on")
            heat = len(node.get("problems", [])) + len(node.get("adrs", []))
            if heat:
                hotspots.append((key, heat))
        elif ntype == "group":
            for child in node.get("children", []):
                add_edge(key, child, "contains")

    stats = {
        "problems": sum(1 for n in graph.values() if n.get("type") == "problem"),
        "adrs": sum(1 for n in graph.values() if n.get("type") == "adr"),
        "services": sum(1 for n in graph.values() if n.get("type") == "service"),
        "edges": len(edges),
        "hotspots": sorted(hotspots, key=lambda x: (-x[1], x[0]))[:10],
    }
    return nodes + edges, stats


def _render_html(elements: list[dict], stats: dict, *, partitioned: bool) -> str:
    inlined = []
    for name in _ASSET_FILES:
        path = ASSETS_DIR / name
        if not path.exists():
            raise typer.Exit(_missing_asset(path))
        inlined.append(f"<script>/* {name} */\n{path.read_text(encoding='utf-8')}\n</script>")
    scripts = "\n".join(inlined)

    elements_json = json.dumps(elements)
    hotspot_rows = "".join(
        f'<li><span class="hs-name">{name}</span><span class="hs-count">{count}</span></li>'
        for name, count in stats["hotspots"]
    ) or '<li class="empty">none</li>'

    return _HTML_TEMPLATE.format(
        scripts=scripts,
        elements_json=elements_json,
        n_problems=stats["problems"],
        n_adrs=stats["adrs"],
        n_services=stats["services"],
        n_edges=stats["edges"],
        hotspot_rows=hotspot_rows,
        layout_mode="cose" if partitioned else "fcose",
    )


def _missing_asset(path: Path) -> int:
    rprint(f"[red]✗[/red] Bundled graph asset not found: {path}\n  Reinstall sda-cli so vendored assets are present.")
    return 1


def graph(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output HTML path")] = GRAPH_FILE,
    html: Annotated[bool, typer.Option("--html/--no-html", help="Emit HTML (default)")] = True,
    open_browser: Annotated[bool, typer.Option("--open", help="Open the file in a browser after writing")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Render the knowledge graph as a self-contained interactive HTML file."""
    full_graph, partitions = assemble_graph(project_dir)
    elements, stats = _to_elements(full_graph)
    document = _render_html(elements, stats, partitioned=bool(partitions))

    out_path = output if output.is_absolute() else project_dir / output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(document, encoding="utf-8")

    rprint(
        f"[green]✓[/green] Wrote interactive graph to {out_path}\n"
        f"  [dim]{stats['problems']} problems · {stats['adrs']} ADRs · "
        f"{stats['services']} services · {stats['edges']} edges[/dim]"
    )

    if open_browser:
        webbrowser.open(out_path.resolve().as_uri())


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ArchSpec — Knowledge Graph</title>
<style>
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #212529; }}
  #app {{ display: flex; height: 100vh; }}
  #sidebar {{ width: 280px; flex: 0 0 280px; background: #f8f9fa; border-right: 1px solid #dee2e6; padding: 18px; overflow-y: auto; }}
  #sidebar h1 {{ font-size: 16px; margin: 0 0 2px; }}
  #sidebar .sub {{ color: #868e96; font-size: 12px; margin-bottom: 16px; }}
  .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 18px; }}
  .stat {{ background: #fff; border: 1px solid #e9ecef; border-radius: 8px; padding: 8px 10px; }}
  .stat .n {{ font-size: 20px; font-weight: 600; }}
  .stat .l {{ font-size: 11px; color: #868e96; text-transform: uppercase; letter-spacing: .04em; }}
  .section-title {{ font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: #868e96; margin: 16px 0 8px; }}
  ul.hotspots {{ list-style: none; padding: 0; margin: 0; }}
  ul.hotspots li {{ display: flex; justify-content: space-between; padding: 5px 8px; border-radius: 6px; font-size: 13px; }}
  ul.hotspots li:nth-child(odd) {{ background: #fff; }}
  ul.hotspots .hs-count {{ font-weight: 600; color: #e8590c; }}
  ul.hotspots .empty {{ color: #adb5bd; font-style: italic; }}
  .legend {{ font-size: 12px; }}
  .legend .row {{ display: flex; align-items: center; gap: 8px; margin: 5px 0; }}
  .legend .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  #main {{ position: relative; flex: 1; }}
  #cy {{ position: absolute; inset: 0; background: #fff; }}
  #fullscreen {{ position: absolute; top: 12px; right: 12px; z-index: 5; background: #fff; border: 1px solid #ced4da;
                 border-radius: 6px; padding: 6px 12px; font-size: 13px; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  #fullscreen:hover {{ background: #f1f3f5; }}
  @media (max-width: 640px) {{ #app {{ flex-direction: column; }} #sidebar {{ width: 100%; flex-basis: auto; max-height: 38vh; }} }}
</style>
</head>
<body>
<div id="app">
  <aside id="sidebar">
    <h1>Knowledge Graph</h1>
    <div class="sub">ArchSpec — generated by <code>sda graph</code></div>
    <div class="stats">
      <div class="stat"><div class="n">{n_problems}</div><div class="l">Problems</div></div>
      <div class="stat"><div class="n">{n_adrs}</div><div class="l">ADRs</div></div>
      <div class="stat"><div class="n">{n_services}</div><div class="l">Services</div></div>
      <div class="stat"><div class="n">{n_edges}</div><div class="l">Edges</div></div>
    </div>
    <div class="section-title">Service hotspots</div>
    <ul class="hotspots">{hotspot_rows}</ul>
    <div class="section-title">Legend</div>
    <div class="legend">
      <div class="row"><span class="dot" style="background:#e8590c"></span> Problem</div>
      <div class="row"><span class="dot" style="background:#1c7ed6"></span> ADR</div>
      <div class="row"><span class="dot" style="background:#2f9e44"></span> Service</div>
      <div class="row"><span class="dot" style="background:#868e96"></span> Group</div>
    </div>
  </aside>
  <div id="main">
    <button id="fullscreen">⛶ Fullscreen</button>
    <div id="cy"></div>
  </div>
</div>
{scripts}
<script>
  var ELEMENTS = {elements_json};
  var layoutName = "{layout_mode}";
  try {{ if (window.cytoscapeFcose) cytoscape.use(window.cytoscapeFcose); }}
  catch (e) {{ layoutName = "cose"; }}
  var cy = cytoscape({{
    container: document.getElementById("cy"),
    elements: ELEMENTS,
    style: [
      {{ selector: "node", style: {{
        "label": "data(label)", "font-size": 10, "text-valign": "center", "text-halign": "center",
        "color": "#fff", "text-outline-width": 2, "width": 26, "height": 26 }} }},
      {{ selector: "node[ntype='problem']", style: {{ "background-color": "#e8590c", "text-outline-color": "#e8590c", "shape": "round-rectangle" }} }},
      {{ selector: "node[ntype='adr']",     style: {{ "background-color": "#1c7ed6", "text-outline-color": "#1c7ed6", "shape": "diamond" }} }},
      {{ selector: "node[ntype='service']", style: {{ "background-color": "#2f9e44", "text-outline-color": "#2f9e44", "shape": "ellipse" }} }},
      {{ selector: "node[ntype='group']",   style: {{ "background-color": "#868e96", "text-outline-color": "#868e96", "shape": "hexagon" }} }},
      {{ selector: "edge", style: {{
        "width": 1.5, "line-color": "#adb5bd", "target-arrow-color": "#adb5bd",
        "target-arrow-shape": "triangle", "curve-style": "bezier", "arrow-scale": 0.8 }} }},
      {{ selector: "edge[kind='depends_on']", style: {{ "line-color": "#495057", "target-arrow-color": "#495057", "width": 2 }} }},
      {{ selector: "edge[kind='affects']",    style: {{ "line-style": "dashed" }} }},
      {{ selector: "edge[kind='addresses']",  style: {{ "line-style": "dotted" }} }},
      {{ selector: "edge[kind='contains']",   style: {{ "line-color": "#ced4da", "target-arrow-shape": "none" }} }},
      {{ selector: ".faded", style: {{ "opacity": 0.15 }} }}
    ],
    layout: {{ name: layoutName, animate: false, randomize: true, padding: 30, nodeDimensionsIncludeLabels: true }}
  }});
  // Click to highlight a node and its neighborhood.
  cy.on("tap", "node", function(evt) {{
    var n = evt.target; var nh = n.closedNeighborhood();
    cy.elements().addClass("faded"); nh.removeClass("faded");
  }});
  cy.on("tap", function(evt) {{ if (evt.target === cy) cy.elements().removeClass("faded"); }});
  // Fullscreen toggle.
  document.getElementById("fullscreen").addEventListener("click", function() {{
    var el = document.getElementById("main");
    if (!document.fullscreenElement) {{ (el.requestFullscreen || el.webkitRequestFullscreen).call(el); }}
    else {{ document.exitFullscreen(); }}
    setTimeout(function() {{ cy.resize(); cy.fit(undefined, 30); }}, 150);
  }});
</script>
</body>
</html>
"""
