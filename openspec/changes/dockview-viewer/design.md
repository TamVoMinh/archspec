## Context

ArchSpec is a Python CLI; the source of truth is files in `architecture/` plus the generated
`index.yaml` model. `native-knowledge-graph` added a static `graph.html`. We want richer
*exploration* (read ADRs, see diagrams, arrange views) without turning ArchSpec into a
platform. The viewer is one more CLI step, delivered as a static export (`view`) and a local
server (`serve`). This document records the architecture decided in explore mode; it is not an
implementation.

## Goals / Non-Goals

**Goals**
- A workbench-style viewer: graph + documents + diagrams, arrangeable side by side.
- A small, stable plugin surface: a plugin is a dock panel.
- Decoupled panels via an FE-only event bus.
- Preserve the offline, shareable artifact (`sda graph view`).
- Keep the Python side read-only and trivial.

**Non-Goals**
- Not a VS Code-style extension *ecosystem* (no extension host isolation, no marketplace,
  no public stable API) — that's a possible far-future, not this change.
- No write path from the viewer; no editing of architecture via the UI.
- **No CQRS / command bus / write model** on the backend (see Decision 5).
- No third-party panels in v1 (registry is first-party; could open later).

## Decisions

### Decision 1: dockview as the viewer shell
**Choice:** Use dockview (MIT) for the workbench — tabs, drag-to-split, floating groups,
serializable layouts.
**Rationale:** It is the VS Code *workbench feel* as a library, and it collapses "what is a
plugin?" into "a dock panel." Layout persistence is nearly free.
**Alternatives:** golden-layout (older/heavier), rc-dock, FlexLayout, or react-resizable-panels
(no tabs/docking). dockview is the best modern React fit.

### Decision 2: Plugins are dock panels (panels-only contribution model)
**Choice:** The only contribution type is a panel: `{ id, title, icon, handles: contentType[],
capability: view|serve, component }`, registered with dockview by id.
**Rationale:** One-dimensional, minimal, stable contract. No commands/menus/decorators to
design or version in v1.
**Alternatives:** Full contribution-point manifest / extension host — deferred as overkill for
a viewer.

### Decision 3: One app, two delivery modes (`view` static / `serve` live)
**Choice:** A single React+Tailwind app. `view` = Vite static export with the model embedded
(offline, shareable). `serve` = local server feeding the same app live.
**Rationale:** Panels stay mode-agnostic; the only difference is the data source. Preserves the
offline artifact while enabling a live dev loop.
**Capability gradient:** pure-client panels (graph, markdown, mermaid, search) work in both;
backend-dependent panels (PlantUML) are `serve`-only and degrade gracefully in `view`.

### Decision 4: FE-only event bus for panel communication
**Choice:** Pub/sub bus, fire-and-forget, in the browser only. Panels emit/subscribe by event
type and never reference each other. A small shared store holds current selection + the loaded
model so a late-mounting panel can read current state on mount.
**v1 event vocabulary (minimal):**
- `model.loaded` `{ model }`
- `selection.changed` `{ nodeId }`
- `document.open` `{ id, contentType, hint? }`
- `graph.highlight` `{ nodeIds }`
- `panel.mounted` / `panel.disposed` `{ panelId }`
**Rationale:** Panel coordination is entirely notifications — pub/sub is the whole answer. No
correlation IDs, no command bus.
**Important distinction (not a pattern):** *announce* (push, via the bus) vs *read data* (pull,
from the store / embedded model / a fetch in serve) are separate. Reading data is not an event.

### Decision 5: Backend is read-only — no CQRS
**Choice:** Python produces the model + serves files read-only. `serve` exposes a plain read
API (`GET /model`, `GET /doc/<id>`), optionally one SSE/WS "changed" nudge for reload. No
commands, no write model.
**Rationale:** The viewer never writes (edits go through files/CLI). CQRS separates write/read
models in write-heavy domains — absent here. Recorded explicitly so it doesn't creep back in.

### Decision 6: Build at package time; wheel ships the prebuilt bundle
**Choice:** Contributors build the frontend with Vite; the built bundle is packaged into the
Python wheel (like `templates/`/`assets/`). End users need no Node.
**Rationale:** Tailwind/Mermaid want a build — doing it at package time keeps `sda graph view`
a zero-extra-dependency run for users, and lets Vite code-split heavy libs (e.g. lazy-load
Mermaid only when a diagram is shown).
**Impact:** CI/release must build the frontend before packaging.

### Decision 7: Supersede the hand-rolled graph.html
**Choice:** The `graph-view` panel (Cytoscape) replaces the standalone `graph.html`; the graph
data model, `depends_on` edges, and hotspots from `native-knowledge-graph` carry forward.
**Rationale:** One viewer codebase. The earlier static file was a stepping stone that proved
the model and edge logic.

## The spine: one model contract

```
   Python schema (source of truth)  ──generate──▶  graph-model TS types
                       │                                   │
                  Python emits                       React/panels consume
   (embedded JSON in `view`; GET /model in `serve`)
```

Get the model schema stable and both planes plus every panel hang off it.

## Risks / Trade-offs

- **New frontend toolchain** (Node/Vite/Tailwind/dockview) in a Python repo — contributor
  setup + CI build cost. End users unaffected.
- **dockview coupling** — the shell library shapes the UI; acceptable given it directly
  delivers the desired UX and is MIT/maintained.
- **`view` bundle size** — Mermaid is heavy; mitigated by Vite code-splitting/lazy-load.
- **Bus discipline** — "panels never reference each other" must be enforced by convention
  (and review), or the decoupling erodes.

## Open Questions (to resolve before specs/tasks)

1. **Open intent** — **Resolved (v1): reuse.** `document.open` reuses the open panel for the
   target content type (one panel per type), updating its params; it creates a panel only when
   none is open. Avoids tab explosion; predictable.
2. **Bidirectional highlight** — **Resolved (v1): one-way (graph → doc).** Selecting a node
   drives the document; `graph.highlight` exists in the vocabulary for a future doc → graph
   path but is not wired in v1.
3. **Layout persistence target:** dockview serialization to localStorage (`view`) and/or a
   dotfile (`serve`) — in v1 or later?
4. **`serve` reload:** does v1 include a file-watcher → `model.changed` push, or is `serve`
   just on-demand reads first?
5. **Monorepo layout / tooling:** `web/` + `packages/model/`; pnpm vs npm; how TS types are
   generated from the Python schema.
6. **Search affordance:** a dedicated search panel vs a global quick-open (Ctrl/Cmd-P) overlay —
   the spec requires fuzzy search but leaves the affordance open.
7. **Accessibility & keyboard navigation:** target level and keyboard model for the workbench —
   not yet specified.
8. **Selection granularity:** v1 is single-node selection; multi-select and edge selection are
   deferred — confirm.
9. **Export form:** single self-contained HTML vs a self-contained directory for `sda graph
   view` (the spec fixes the offline property but not the mechanical form).

## Migration Plan

Additive. `native-knowledge-graph` stays as-is until the `graph-view` panel reaches parity,
then `sda graph view` switches to the dockview build and the standalone `graph.html` generator
is retired. No change to the CLI's data model or to consumer repos.

## Archive order & reconciliation

This change is part of a cluster on the same PR; archive deliberately:
- Archive **after `native-knowledge-graph`** — this change's `interactive-graph` requirement
  builds on (effectively modifies) the one introduced there.
- The **`search` panel here is superseded by `model-tree-explorer`'s `explorer`**. If this
  change archives first, the "Fuzzy search across the model" requirement lands in the main
  specs and `model-tree-explorer` must then carry a REMOVED delta for it. Prefer archiving the
  two together (or explorer immediately after) so the main specs never describe both a search
  panel and an explorer.

## Scope decisions (remaining work)

- **Keep `sda graph static`** — not retiring it (task 5.5 won't-do). `view` is the richer
  dockview workbench, but `static` stays a zero-React, lightweight single-file option; the two
  serve different needs.
- **`search` panel is obsolete** — superseded by `model-tree-explorer`'s Explorer. Its
  requirement is removed at archive (see "Archive order & reconciliation").
- **Deferred (not blocking):** layout persistence (2.4), TS type-gen from the Python schema
  (1.3), serve SSE auto-refresh (5.4, serve already refreshes), and panel-render/sanitization
  tests (need a jsdom setup). The robustness requirements the shell spec demands
  (empty/error/version states, panel isolation) are now implemented and tested.
