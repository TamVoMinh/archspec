## Why

The `dockview-viewer` ships a flat fuzzy-search panel. A flat list works at small scale but
collapses at the real target — hundreds of services and documents across many systems. You
can *query* a flat list but you can't *browse* it: there's no sense of structure, no way to
scan a system's services, no way to narrow the graph to one area. Teams think hierarchically
(by system, by type, by ownership); the viewer should let them navigate that way.

This change replaces the search panel with an **Explorer** panel — a browsable model tree that
*contains* search — sized for hundreds of nodes.

Captures explore-mode thinking; implementation deferred.

## What Changes

- Replace the `search` panel (from `dockview-viewer`) with an **`explorer`** panel.
- The Explorer is a **model tree**, not a filesystem mirror: folders are logical groupings,
  leaves are architecture artifacts (problems, ADRs, services). A literal file tree would hide
  the many services that live inside a few `services.yaml` files.
- A **Group-by toggle** changes the hierarchy — at least **system**, **type**, and **service
  group** — so different roles can navigate the way they think.
- **Search is an integrated filter**: typing narrows the tree to matching leaves plus their
  ancestor folders (fuzzy), rather than a separate flat list.
- Folders show **counts** (e.g. `Services (210)`) so magnitude is visible at a glance.
- Selecting a leaf keeps today's behavior: emit `selection.changed` + `document.open`.
- The tree is **virtualized** so hundreds (or thousands) of rows stay responsive.

## Capabilities

### New Capabilities
- `explorer-panel`: A browsable, virtualized model-tree panel with a Group-by toggle and an
  integrated fuzzy filter, replacing the flat search panel as the viewer's navigation surface.

### Modified Capabilities
<!-- Supersedes the `search` panel from dockview-viewer. That capability is defined only as a
delta in the not-yet-archived dockview-viewer change, so the removal is reconciled at archive
time rather than as a MODIFIED delta here. -->

## Impact

- **web**: replaces `panels/SearchPanel.tsx` with an `panels/ExplorerPanel.tsx`; App registers
  `explorer` in the default layout (the locked left rail) instead of `search`. Likely adds a
  virtualized tree library (e.g. react-arborist). Fuse stays for the filter.
- **Bus**: no new required events for v1 (selection + document.open reused). Graph-scoping and
  reveal-in-explorer are tracked as open questions.
- **dockview-viewer**: its `search` panel + "Fuzzy search across the model" requirement are
  superseded by this change once both land.
- **Scale**: at thousands of artifacts the `view` static export grows large (all docs embedded)
  — `serve` becomes the better mode; the tree itself stays cheap via virtualization.
- No change to the Python model contract.
