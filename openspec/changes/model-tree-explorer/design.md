## Context

`dockview-viewer` provides a flat fuzzy-search panel as the navigation surface. The real target
is hundreds of services and documents across systems, where a flat list can't be browsed. The
Explorer replaces it with a hierarchical, virtualized tree that also searches. The viewer stays
a panels-only dockview workbench; this is a richer first-party panel, not a new subsystem.

## Goals / Non-Goals

**Goals**
- Browse the architecture by a meaningful hierarchy, switchable by the viewer.
- Search integrated into the tree (filter), not a separate flat list.
- Stay responsive at hundreds–thousands of nodes.

**Non-Goals**
- Not a filesystem browser (see Decision 1).
- No editing/creation from the tree (the viewer is read-only).
- No new model-contract fields.

## Decisions

### Decision 1: Browse the model, not the filesystem
**Choice:** Folders are logical (system / type / group); leaves are artifacts (problems, ADRs,
services).
**Rationale:** Services aren't files — hundreds live inside a few `services.yaml` files, so a
literal file tree would surface `services.yaml`, not the services you want to browse. The model
tree exposes every artifact as a navigable leaf.
**Alternatives:** Filesystem mirror (rejected — hides services); hybrid (deferred).

### Decision 2: Group-by toggle, not one fixed hierarchy
**Choice:** A selector re-roots the tree by **system**, **type**, or **service group** (status
is a candidate too).
**Rationale:** Roles navigate differently — architects by system, triagers by problem/status,
dependency work by group. One fixed tree serves none of them well at scale. (VS Code is
filesystem-only; a catalog like Backstage groups by kind/owner/system — ArchSpec is the latter.)

### Decision 3: Search is a tree filter
**Choice:** Typing narrows the tree to matching leaves plus their ancestor folders (fuzzy via
Fuse), with the match highlighted; clearing restores the full tree.
**Rationale:** Keeps one navigation surface — browse and query in the same place — instead of a
separate list. A keyboard quick-open palette is a possible complement (open question).

### Decision 4: Virtualize the tree
**Choice:** Render only visible rows (e.g. react-arborist, which is purpose-built: virtualized,
keyboard nav, built-in filtering), rather than a hand-rolled recursive render.
**Rationale:** Hundreds–thousands of rows must scroll smoothly; naive rendering won't.
**Alternatives:** Hand-rolled tree + tanstack-virtual (more control, more code).

## Risks / Trade-offs

- **Large embedded data**: at thousands of artifacts the `view` export embeds all docs and grows
  large; `serve` (fetch on demand) is the scale answer. Possibly lazy-load doc bodies.
- **Tree/graph sync complexity**: bidirectional reveal and graph-scoping add coupling — kept as
  open questions, not v1 commitments.
- **Library lock-in**: react-arborist shapes the tree UI; acceptable for the scale benefit.

## Open Questions

1. **Graph scoping** — should selecting a *folder* (e.g. a system) scope/filter the graph to
   that subtree? This is the feature that tames a 200-node graph, but needs a new bus event.
2. **Reveal in Explorer** — should selecting a node in the graph expand + select its row in the
   tree (bidirectional)?
3. **Quick-open palette** — a Ctrl/Cmd-P fuzzy jump in addition to the in-tree filter?
4. **Default Group-by** — system, or type?
5. **Status as a grouping** — include "group by status" (draft/active/resolved, ADR lifecycle)?
6. **Tree library** — react-arborist vs hand-rolled + tanstack-virtual.
7. **Keyboard/accessibility** — target level for tree keyboard navigation (arrows/enter/type-ahead); react-arborist provides much of this, so likely a verification item rather than a build item.

## Migration

Replace the `search` panel registration with `explorer` in the default layout (the locked left
rail). The bus contract is unchanged for v1, so other panels are unaffected. The `dockview-
viewer` search requirement is retired when this lands.

## Archive order & reconciliation

- Archive **with or immediately after `dockview-viewer`**. This change **supersedes** that
  change's `search` panel: at archive, remove/REMOVE the "Fuzzy search across the model"
  requirement and the `search` entry in "First-party panels" so the main specs describe only
  the `explorer`. (If dockview-viewer is archived first, add an explicit `## REMOVED
  Requirements` delta here for that requirement.)
- The Explorer's group-by becomes **data-driven over classification dimensions** once
  `artifact-classification` lands — reconcile the hardcoded `system/type/group` wording with
  the dimension-driven behavior at archive.
