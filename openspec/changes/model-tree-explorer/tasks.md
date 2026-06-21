## 1. Tree model

- [x] 1.1 Add a `buildTree(model, groupBy)` helper that turns the GraphModel into a tree of folders + artifact leaves (pure, unit-testable)
- [x] 1.2 Implement groupings: `system`, `type`, `service group` (group nodes + children); decide the default (open question)
- [x] 1.3 Compute folder counts (leaves contained, recursively) for each folder
- [x] 1.4 Leftover bucket: collect artifacts with no value for the active grouping under an explicit "Unscoped"/"Ungrouped" folder (e.g. unrouted problems / root ADRs under group-by-system; problems/ADRs and group-less services under group-by-group)
- [x] 1.5 Deterministic ordering: folders first, then leaves, each sorted by id/label
- [x] 1.6 Tests: each grouping produces correct folders/leaves; services in one services.yaml appear as individual leaves; counts correct; leftover bucket populated; stable order

## 2. Explorer panel

- [x] 2.1 Add a virtualized tree library (e.g. react-arborist) or hand-rolled tree + tanstack-virtual (resolve open question)
- [x] 2.2 `panels/ExplorerPanel.tsx`: render the tree (folders expand/collapse, leaves), styled with the design tokens
- [x] 2.3 Group-by toggle control that re-roots the tree without reloading the model
- [x] 2.4 Integrated filter over id/label (react-arborist searchTerm): narrow to matching leaves + ancestor folders; clear restores full tree. (Title search pending — titles not in the model yet; see 5.5)
- [x] 2.5 Show folder counts in the row
- [x] 2.6 Leaf select → emit `selection.changed` + `document.open`; folder toggle emits neither
- [x] 2.7 Reflect current selection (highlight the selected row when visible), including selection originating from the graph
- [x] 2.8 Empty-model state: show getting-started guidance instead of a blank rail

## 3. Wire into the workbench

- [x] 3.1 Register `explorer` in the panel set; place it in the locked left rail in the default layout
- [x] 3.2 Remove the `search` panel registration (superseded); keep the Fuse dependency for the filter
- [x] 3.3 Confirm the rail stays fixed-width when documents open/close (existing constraint)

## 4. Open questions to resolve (design.md)

- [ ] 4.1 Graph scoping: should selecting a folder (e.g. a system) scope/filter the graph? If yes, define the bus event and wire it
- [ ] 4.2 Reveal-in-Explorer: should a graph selection expand + select the matching tree row (bidirectional)?
- [ ] 4.3 Quick-open palette (Ctrl/Cmd-P) in addition to the in-tree filter?
- [ ] 4.4 Status as a grouping (problem status / ADR lifecycle)?

## 5. Docs, tests & verification

- [ ] 5.1 Frontend tests: tree build per grouping, filter behavior, leaf-vs-folder selection, counts
- [ ] 5.2 Update `docs/concepts/knowledge-graph.md` and `web/README.md` for the Explorer (replaces search)
- [ ] 5.3 Verify on the `example/` project and a large synthetic model (hundreds of nodes) — browse, group-by switch, filter, scroll stay responsive
- [ ] 5.4 Reconcile the superseded `search` panel from dockview-viewer (remove its requirement/tasks at archive time)
- [ ] 5.5 Surface artifact titles in the model (Python index + model TS type) so the filter can match titles, not only ids
