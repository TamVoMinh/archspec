## Why

`native-knowledge-graph` shipped a static, self-contained `graph.html` (hand-rolled
Cytoscape + inlined assets). It proves the graph model and rendering, but it's a single fixed
view — you can't read an ADR's rendered markdown, see a diagram, or arrange multiple views
side by side. Consumers want to *explore* the architecture: open the graph next to the ADR it
links to, render diagrams, search. ArchSpec stays a CLI toolkit — this is one more step the
CLI offers: a good, conventional way to **visualize and interact** with what the engine
already produces. It is not a product pivot to a platform/IDE.

This change captures the design exploration (explore mode). Implementation is deferred; specs
and tasks come when we leave exploration.

## What Changes

- `sda graph` grows two delivery modes of **one** viewer app:
  - `sda graph view` — static export (Vite build with the model embedded). Offline,
    shareable, git-friendly. Supersedes the hand-rolled `graph.html` (the data model and edge
    logic carry over; only the rendering is replaced).
  - `sda graph serve` — local server that serves the same app against live data, so edits to
    source files reflect without a re-export.
- The viewer is a **React + Tailwind** app whose shell is **[dockview](https://github.com/mathuo/dockview)**
  (MIT docking/panel manager — tabs, drag-to-split, floating groups, serializable layouts).
- **Plugin model = "every plugin is a dock panel."** The contribution surface is a panel
  registry; there are no commands/menus/decorators contribution types in v1. A panel declares
  `{ id, title, icon, handles: contentType[], capability: view | serve }` plus its React
  component.
- **First-party panels:** `graph-view` (Cytoscape) and `markdown` (Marked) in v1; `mermaid`
  next; **PlantUML deferred to a later plugin** (it needs a backend/network to render, so it
  will be a `serve`-capability panel).
- **Communication between panels is an FE-only event bus** (pub/sub, fire-and-forget). Panels
  never reference each other; they share only the event vocabulary. A small shared store holds
  current selection + the loaded model so late-mounting panels can read current state.
- **The Python backend is read-only.** The viewer never writes; edits happen via files/CLI.
  `serve` is a plain read API (`GET /model`, `GET /doc/<id>`, optionally one SSE/WS "changed"
  nudge). Explicitly **no CQRS, no command bus, no write model.**
- **Build happens at package time**, not at the user's runtime: contributors need Node/Vite;
  the Python wheel ships the prebuilt bundle (like `templates/` and `assets/` today). End users
  `pip install sda-cli` and run `sda graph view` with no Node.

## Capabilities

### New Capabilities
- `dockview-shell`: A dockview-based viewer workbench (tabs, split, float, serializable
  layout) hosting panels, shipped by `sda graph` in `view` (static) and `serve` (live) modes.
- `panel-plugins`: A panel registry where each plugin is a dock panel declaring id, content
  types it handles, and a `view|serve` capability. First-party: graph-view, markdown (then
  mermaid; PlantUML later).
- `viewer-event-bus`: An FE-only pub/sub bus for panel-to-panel coordination (fire-and-forget
  events) plus a small shared store for current selection and the loaded model.

### Modified Capabilities
- `interactive-graph` (from `native-knowledge-graph`): the rendering moves from a hand-rolled
  single HTML file to the dockview `graph-view` panel. The graph data model is unchanged.

## Impact

- **Repo shape**: gains a frontend build — `web/` (React + TS + Tailwind + Vite + dockview)
  and likely `packages/model/` (JSON schema → shared TS types, the contract both sides use).
- **CLI**: `sda graph` gains `view` and `serve` subcommands; a prebuilt frontend bundle is
  packaged into the wheel; `pyproject.toml` package-data extended.
- **Release/CI**: the pipeline must build the frontend bundle before packaging the wheel.
- **End users**: unaffected at install time (no Node); `sda graph view` stays offline.
- **Supersedes**: the hand-rolled `graph.html`; the `depends_on` edges, hotspots, and graph
  model from `native-knowledge-graph` carry forward into the `graph-view` panel.
- **No product change**: ArchSpec remains a CLI toolkit; the viewer is an emitted artifact /
  local convenience, not a service to operate.
