## Context

The index builder (`cli/src/sda/commands/index.py`) already promotes every service in
`services.yaml` to a graph node, but it never reads `depends_on`, so the service dependency
map is absent. There is no HTML output anywhere in the codebase, and `sda check` validates ADR
lifecycle, staleness, and ownership — but never checks that referenced services exist. Issue #7
asks to bring a prototype's capabilities (full service map, interactive visual, one-command
build) into the tool. The CLI is Typer + `rich`; the project is offline/git-native by design.

## Goals / Non-Goals

**Goals**
- Model `depends_on` as service-to-service edges in the index.
- Provide a native, self-contained, offline interactive visualization.
- One command to regenerate all derived artifacts.
- Validate that service references resolve.

**Non-Goals**
- "Dossiers" mentioned in the issue — no existing implementation to build on.
- Cross-partition dependency resolution (a `depends_on` target is resolved within its own
  partition's registry).
- Committing generated HTML by default (kept git-ignored; CI-build documented).

## Decisions

### Decision 1: Record `depends_on` on service nodes (declarative in the index)
**Choice:** `_build_graph()` attaches `depends_on: [...]` to every service node; existence is
NOT enforced here.
**Rationale:** Mirrors how the index already records unvalidated problem/ADR references — the
index is a projection, `sda check` is the validator. Keeps the index generation side-effect-free
and fast.
**Alternatives considered:** A separate top-level `edges:` list (rejected — inconsistent with
the existing node-keyed, embedded-link shape and harder to `yq`).

### Decision 2: Extract `assemble_graph(project_dir) -> (graph, partitions)`
**Choice:** Pull the flat-vs-partitioned master-graph assembly out of `index()` into a reusable
function; `index`, `graph`, and `build` all consume it.
**Rationale:** One source of truth for graph shape (including the partitioned merge and
`system:` annotation). Avoids duplicating partition logic in the new commands.
**Alternatives considered:** Having `graph`/`build` read the committed `index.yaml` (rejected —
would render stale data and couple to the on-disk manifest format).

### Decision 3: Cytoscape.js, vendored and inlined; vanilla HTML/CSS/JS
**Choice:** Bundle `cytoscape.min.js` + the fcose layout stack (`cytoscape-fcose`, `cose-base`,
`layout-base`, all MIT) into `cli/src/sda/assets/` and inline them into the output via Python
string templating (`json.dumps` for data). No framework, no build step.
**Rationale:** Satisfies the "single offline file" requirement (no CDN, CSP-safe), matches the
project's git-native ethos, and Cytoscape scales better than vis-network for larger graphs with
richer layouts. Frameworkless keeps the output a double-clickable file.
**Alternatives considered:** CDN `<script src>` (rejected — needs internet, external dep);
vis-network (viable, but Cytoscape chosen for layout flexibility/scale); D3 (too much
hand-built interaction); a JS framework (breaks the single-file requirement).
**Fallback:** if fcose registration fails at runtime, the layout degrades to Cytoscape's
built-in `cose`.

### Decision 4: Severity of reference validation
**Choice:** `depends_on` → missing target is an **ERROR**; problem/ADR service references to a
missing service are **WARNINGS**.
**Rationale:** A broken `depends_on` is a structural-integrity defect in the model, so CI
(`--strict`) should fail. Problem/ADR references are looser (a service may be a typo or not yet
modeled), so they warn without blocking. Partitioned problem refs validate against the union of
all partitions, since the inbox is shared.

## Risks / Trade-offs

- **Vendored JS size** — inlining makes `graph.html` ~0.7MB. Acceptable for a git-ignored,
  offline artifact; documented.
- **`assemble_graph` refactor touches the `sda index` hot path** — mitigated by the existing
  `test_index.py` suite plus new `depends_on` assertions.
- **Cross-partition `depends_on`** — a target in another partition reports as unknown; flagged
  and documented as a follow-up.

## Migration Plan

Additive and backward compatible. Existing repos gain `depends_on` on service nodes the next
time they run `sda index`/`sda build`; no restructuring required. New commands are opt-in.
