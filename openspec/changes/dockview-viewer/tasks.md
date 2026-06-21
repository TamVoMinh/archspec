## 1. Frontend scaffold & build pipeline

- [x] 1.1 Add `web/` workspace: Vite + React + TypeScript + Tailwind, configured for a static build and a dev server
- [x] 1.2 Add `packages/model/`: the graph-model JSON schema (incl. a **schema version** field) + generated TS types — the contract both planes use
- [ ] 1.3 Wire TS type generation from the Python model schema (single source of truth)
- [x] 1.4 Decide and document monorepo tooling (npm/pnpm workspaces) and scripts (`build`, `dev`)
- [x] 1.5 Package the prebuilt `web/` bundle into the Python wheel via `pyproject.toml` package-data (scripts/build-viewer.sh stages it; verified present in built wheel)
- [x] 1.6 Update CI/release to build the frontend bundle before packaging the wheel (publish.yml: web job + staging step)

## 2. Dockview shell & global states

- [x] 2.1 Add dockview and mount the workbench (tabs, split groups, floating)
- [x] 2.2 Apply Tailwind theme/styling to the shell (light panels on dark dockview chrome for readability)
- [x] 2.3 Implement a sensible default layout on launch (at minimum `graph-view` visible) when no saved layout exists
- [ ] 2.4 Implement layout serialize/restore (open question: localStorage for `view`, dotfile for `serve`)
- [ ] 2.5 Empty/loading/error states: empty-model getting-started guidance, model load/parse failure screen, per-panel inline error that does not crash the workbench
- [ ] 2.6 Schema-version handling: detect unsupported model version and show a version-mismatch message instead of mis-rendering
- [ ] 2.7 Verify split/tab/close + state behaviors against the dockview-shell spec scenarios

## 3. Event bus, store & routing

- [x] 3.1 Implement the FE pub/sub bus (typed, fire-and-forget) with the v1 vocabulary: `model.loaded`, `selection.changed`, `document.open`, `graph.highlight`, `panel.mounted`, `panel.disposed`
- [x] 3.2 Implement the shared store holding current selection + loaded model; expose read-on-mount for late-mounting panels
- [x] 3.3 Implement the data-source seam (pull): embedded model in `view`, read fetch in `serve` — kept off the bus
- [x] 3.4 Implement `document.open` routing: dispatch to a panel handling the content type + mode; deterministic pick when multiple; clear message when none
- [x] 3.5 Resolve open question: `document.open` reuse-active-panel vs new-tab policy; encode the chosen behavior
- [x] 3.6 Resolve open question: graph↔doc bidirectional highlight in v1 or one-way

## 4. Panel registry & first-party panels

- [x] 4.1 Implement the panel registry + manifest shape `{ id, title, icon, handles, capability }`; register panels by id with dockview
- [x] 4.2 Implement view/serve capability handling: graceful degradation for `serve`-only panels opened in `view` (router excludes ineligible panels, surfaces no-handler message)
- [x] 4.3 Implement node→content mapping: ADR→markdown, problem→record, service→detail-from-`services.yaml`, group→focus/filter subgraph; emit `document.open` with the right content type
- [x] 4.4 `graph-view` panel (Cytoscape): render the model incl. `depends_on` edges; **distinguish partitions (`system`) and render `group` nodes/children**; emit `selection.changed`; subscribe to `graph.highlight`
- [x] 4.5 `markdown` panel (Marked + Prism): render ADR/problem markdown; **sanitize** output (links/attachment resolution lands with the §5 data path)
- [x] 4.6 `mermaid` panel: render fenced mermaid diagrams (lazy-loaded via Vite code-split); rendered inline in the document panel for `` ```mermaid `` blocks
- [x] 4.7 `search` panel (Fuse): fuzzy search across problems/ADRs/services; selecting a result drives selection/open via the bus
- [x] 4.8 Icons (Lucide) across panels and tabs

## 5. CLI integration (`sda graph view` / `serve`)

- [x] 5.1 `sda graph view`: produce a self-contained Vite export with the model + referenced documents embedded; opens offline with no external requests (attachments land with links/attachments work)
- [x] 5.2 `sda graph serve`: read-only local server (`GET /model`, `GET /doc/<id>`) serving the same app; rebuilds per request so it reflects live edits; no write endpoints
- [x] 5.3 Preserve CLI conventions: `--project-dir`, `--output`, `--open`; `graph` is now a group (`static`/`view`/`serve`)
- [ ] 5.4 (Optional) `serve` file-watcher → `model.changed` push over SSE/WS (per open question)
- [ ] 5.5 Retire the standalone `graph.html` generator once `graph-view` reaches parity; update docs and `sda graph` help

## 6. Docs, verification & migration

- [x] 6.1 Update `readme.md` CLI table and `docs/concepts/knowledge-graph.md` for `sda graph view`/`serve`; add `web/README.md`
- [ ] 6.2 Frontend tests: bus events, store read-on-mount, panel registry, routing (multi/no handler), serve-only degradation, sanitization, empty/error/version states
- [x] 6.3 Verify view-mode export is self-contained (no external refs); verify serve-mode reflects edits (rebuilds per request)
- [x] 6.4 Run end-to-end: `sda graph serve` on `example/` (real data over HTTP) + sample fixture for partitions/groups/mermaid/search
- [x] 6.5 Confirm `native-knowledge-graph` data model carries over unchanged (`assemble_graph` reuse; tests green)
