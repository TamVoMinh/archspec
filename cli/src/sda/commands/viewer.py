"""
sda graph view / serve — the dockview knowledge-graph viewer.

`view`  exports a single self-contained HTML (model + documents embedded) that opens
        offline.
`serve` runs a read-only local server (GET /model, /doc/<id>) for the same app,
        reflecting live edits.

Both use the prebuilt single-file web bundle (web/dist/index.html), located from the
installed package or, in a source checkout, from the repo's web/dist.
"""

import json
import yaml
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint

from sda.commands.index import assemble_graph
from sda.discovery import ARCH_DIR, INBOX_DIR, MODEL_DIR, discover_partitions, discover_problem_files, load_all_services

ADR_DIR = Path("architecture/adr")
GRAPH_FILE = Path("architecture/graph.html")
ADR_TEMPLATE = "TEMPLATE.md"


def _bundle_html() -> str:
    """Return the prebuilt single-file viewer HTML (installed package or repo web/dist)."""
    try:
        ref = resources.files("sda") / "viewer" / "index.html"
        with resources.as_file(ref) as p:
            if p.exists():
                return p.read_text(encoding="utf-8")
    except (ModuleNotFoundError, FileNotFoundError, AttributeError):
        pass
    dev = Path(__file__).resolve().parents[4] / "web" / "dist" / "index.html"
    if dev.exists():
        return dev.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "Viewer bundle not found. Build the web app (`pnpm --filter @archspec/web build`) "
        "or install a release wheel that bundles it."
    )


def _problem_markdown(data: dict) -> str:
    lines = [f"# {data.get('id', '?')}: {data.get('title', '')}", ""]
    for key in ("source", "type", "status", "system", "created_at"):
        if data.get(key):
            lines.append(f"- {key}: {data[key]}")
    for section in ("symptoms", "constraints", "tags"):
        items = data.get(section) or []
        if items:
            lines += ["", f"## {section.capitalize()}"] + [f"- {i}" for i in items]
    return "\n".join(lines)


def _service_detail(name: str, meta: dict) -> str:
    out = {k: v for k, v in (meta or {}).items() if not k.startswith("_")}
    return yaml.dump({name: out}, sort_keys=True, allow_unicode=True)


def build_viewer_data(project_dir: Path) -> dict:
    """Build {model, documents} for the viewer from the project sources."""
    graph, partitions = assemble_graph(project_dir)
    systems = sorted({name for name, _ in partitions})

    model: dict = {"schemaVersion": 1, "graph": graph}
    if systems:
        model["systems"] = systems

    documents: dict[str, dict] = {}

    # ADRs (root + per-partition) → markdown.
    adr_dirs = [project_dir / ADR_DIR] + [p / "adr" for _, p in partitions]
    for d in adr_dirs:
        if d.exists():
            for f in sorted(d.glob("*.md")):
                if f.name == ADR_TEMPLATE:
                    continue
                doc_id = f.stem.upper()
                documents[doc_id] = {"id": doc_id, "contentType": "markdown", "text": f.read_text(encoding="utf-8")}

    # Problems → markdown.
    for f in discover_problem_files(project_dir / INBOX_DIR):
        with f.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        pid = data.get("id") or f.stem.upper()
        documents[pid] = {"id": pid, "contentType": "markdown", "text": _problem_markdown(data)}

    # Services → service-detail.
    model_dirs = [project_dir / MODEL_DIR] + [p / "model" for _, p in partitions]
    for md in model_dirs:
        if md.exists():
            all_services, _groups, _errs = load_all_services(md)
            for name, meta in all_services.items():
                documents[name] = {"id": name, "contentType": "service-detail", "text": _service_detail(name, meta)}

    return {"model": model, "documents": documents}


def _inject_data(html: str, data: dict) -> str:
    payload = json.dumps(data).replace("</", "<\\/")  # safe inside <script>
    return html.replace("</head>", f"<script>window.__ARCHSPEC_DATA__ = {payload};</script></head>", 1)


def view(
    output: Annotated[Path, typer.Option("--output", "-o", help="Output HTML path")] = GRAPH_FILE,
    open_browser: Annotated[bool, typer.Option("--open", help="Open in a browser after writing")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Export a self-contained, offline interactive viewer (model + docs embedded)."""
    html = _inject_data(_bundle_html(), build_viewer_data(project_dir))
    out_path = output if output.is_absolute() else project_dir / output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    rprint(f"[green]✓[/green] Wrote self-contained viewer to {out_path}")
    if open_browser:
        webbrowser.open(out_path.resolve().as_uri())


def serve(
    port: Annotated[int, typer.Option(help="Port to listen on")] = 4173,
    host: Annotated[str, typer.Option(help="Host to bind")] = "127.0.0.1",
    open_browser: Annotated[bool, typer.Option("--open", help="Open in a browser")] = False,
    project_dir: Annotated[Path, typer.Option(help="Project root directory")] = Path("."),
) -> None:
    """Serve the viewer with a read-only API that reflects live project edits."""
    bundle = _bundle_html()
    pd = project_dir

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, bundle.encode("utf-8"), "text/html; charset=utf-8")
            elif path == "/model":
                data = build_viewer_data(pd)["model"]
                self._send(200, json.dumps(data).encode("utf-8"), "application/json")
            elif path.startswith("/doc/"):
                doc_id = path[len("/doc/"):]
                docs = build_viewer_data(pd)["documents"]
                doc = docs.get(doc_id)
                if doc is None:
                    self._send(404, b'{"error":"not found"}', "application/json")
                else:
                    self._send(200, json.dumps(doc).encode("utf-8"), "application/json")
            else:
                self._send(404, b"not found", "text/plain")

        def log_message(self, *_args) -> None:  # silence default logging
            pass

    httpd = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    rprint(f"[green]✓[/green] Serving ArchSpec viewer at [bold]{url}[/bold]  [dim](Ctrl-C to stop)[/dim]")
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        rprint("\n[dim]stopped[/dim]")
    finally:
        httpd.server_close()
