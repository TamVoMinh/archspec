## Why

Consumers running `sda` on real architecture workspaces have to build custom generator
scripts on top of `sda index` output to get two things the tool doesn't provide: a usable
**visual** of the knowledge graph, and a **full service map** that shows service-to-service
dependencies. `depends_on` is already declared in `services.yaml` and the schema, but the
index never reads it, so the dependency map is invisible. There is no visualization at all,
and no validation that service references (in `depends_on`, problems, or ADRs) actually point
at registered services. This forces every consumer to maintain bespoke, drifting tooling.

See GitHub issue #7.

## What Changes

- `sda index` now records each service's `depends_on` list on its service node, so the graph
  models the service-to-service dependency map (not just problem/ADR → service references).
- New command **`sda graph`** renders the knowledge graph as a single self-contained,
  interactive HTML file. The graph engine (Cytoscape.js) is vendored and inlined — the file
  opens fully offline, with no CDN or network dependency. It shows every registered service,
  all four edge types (problem→ADR, problem→service, ADR→service, service→service
  `depends_on`), a fullscreen toggle, click-to-highlight, and an insight sidebar with counts
  and service hotspots.
- New command **`sda build`** regenerates every derived artifact (index + graph) in one step,
  so a single source edit is reflected everywhere without a manual multi-step regen.
- `sda check` gains service-reference validation: every `depends_on` target must be a
  registered service (error); problem and ADR service references that don't exist are warnings.
- Generated HTML is kept out of git: `sda init` adds a `.gitignore` rule, and building in CI
  is documented as the commit-free alternative.

## Capabilities

### New Capabilities
- `service-dependency-edges`: Service nodes in the index carry their declared `depends_on`,
  exposing the service-to-service dependency map in the knowledge graph.
- `interactive-graph`: `sda graph` emits a self-contained, offline, interactive HTML
  visualization of the full knowledge graph (all services + all edge types + hotspots).
- `build-orchestration`: `sda build` regenerates all derived artifacts (index + graph) in one
  command.
- `service-reference-validation`: `sda check` validates that `depends_on` targets and
  problem/ADR service references resolve to registered services.

### Modified Capabilities
<!-- No existing specs are reworded; knowledge-graph-index gains depends_on via the new capability -->

## Impact

- **CLI source**: `index.py` (`depends_on` in `_build_graph`, extracted `assemble_graph`),
  new `commands/graph.py` and `commands/build.py`, `commands/check.py` (new checks wired in),
  `validators/services.py` and `validators/adr.py` (existence validators), `main.py`
  (register `graph`, `build`), `scaffold.py` (`.gitignore` rule), `pyproject.toml`
  (vendored `assets/*.js` packaged).
- **New assets**: `cli/src/sda/assets/` vendors Cytoscape.js + the fcose layout stack (MIT).
- **index.yaml schema**: service nodes gain a `depends_on` list. Backward compatible —
  additive only.
- **Output hygiene**: `architecture/graph.html` is generated and git-ignored by default.
- **No breaking changes**: existing flat and partitioned behavior is preserved; the
  `depends_on` field is additive.
