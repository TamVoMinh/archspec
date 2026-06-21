# Knowledge Graph — Querying Architecture

The knowledge graph is ArchSpec's answer to the question: *"How is everything connected?"*

It's not a database. It's a flat YAML file — `architecture/index.yaml` — automatically generated from your inbox problems, ADR files, and service model. It makes your architecture **queryable** without any special tooling.

---

## What it Contains

```yaml
graph:
  PROB-001:
    type: problem
    services: [api-gateway, billing]
    status: active
    linked_adrs: [ADR-012]

  ADR-012:
    type: adr
    status: accepted
    linked_problems: [PROB-001, PROB-003]
    linked_services: [api-gateway, billing]
    superseded_by: ~

  billing:
    type: service
    problems: [PROB-001]
    adrs: [ADR-012]
    depends_on: [database]
```

Node types:
- **problem** — an inbox entry (from flat or folder layout)
- **adr** — a decision record
- **service** — every service in `services.yaml` (referenced or not); may include a `group` field and a `depends_on` list of the services it depends on
- **group** — a service group from hierarchical model, with `children` listing member services

### Service dependencies (`depends_on`)

Every service node carries its declared `depends_on` list, so the graph models the
service-to-service dependency map — not just which services a problem or ADR touches.
`sda check` validates that every `depends_on` target is a registered service (error) and
that problem/ADR service references exist (warning).

### Hierarchical Services

When services are organised into subdirectories under `architecture/model/`, the graph includes group nodes:

```yaml
graph:
  infra:
    type: group
    children: [dns-service, cdn-service]

  dns-service:
    type: service
    group: infra
    problems: [PROB-002]
    adrs: []
```

Root-level services (in `architecture/model/services.yaml`) have no group — fully backward compatible.

---

## Generating the Graph

```bash
sda index                    # generate/overwrite architecture/index.yaml
sda index --validate         # non-blocking: check if the committed index is fresh
```

The graph is regenerated in CI on every push. A stale index triggers a warning (non-blocking by default).

---

## Visualizing the Graph

`sda graph` offers three offline visualizations — all bundled and inlined, no server, no CDN:

```bash
sda graph static            # single-file, zero-dependency interactive graph (Cytoscape)
sda graph view              # self-contained dockview viewer (graph + docs + diagrams + search)
sda graph serve             # local read-only server for the viewer; reflects live edits
```

All show every service (the full registry) and all four edge types — problem→ADR,
problem→service, ADR→service, and service→service `depends_on`.

**`sda graph static`** writes one self-contained `architecture/graph.html` with a fullscreen
toggle and a **service hotspots** sidebar — the lightest option, opens by double-click.

**`sda graph view`** exports a richer self-contained file: a dockview workbench where you can
read ADRs/problems as rendered Markdown (with Mermaid diagrams and syntax-highlighted code),
fuzzy-search nodes, and open documents beside the graph — all offline.

**`sda graph serve`** runs the same workbench from a local read-only server
(`GET /model`, `/doc/<id>`); it rebuilds per request, so edits to your architecture files show
up on refresh.

```bash
sda graph view --output g.html --open   # custom path, open in browser
sda graph serve --port 4173 --open      # serve and open
```

Generated HTML is git-ignored by default (`sda init` adds the rule). Either regenerate locally
with `sda build`, or build it in CI as a published artifact rather than committing it.

### One-command rebuild

```bash
sda build       # regenerate index.yaml + graph.html together
```

Use `sda build` after any source edit so the index and the visualization never drift.

---

## Querying

No special tooling needed — use `yq`:

```bash
# Which services does PROB-001 affect?
yq '.graph.PROB-001.services' architecture/index.yaml

# Which ADRs are linked to PROB-001?
yq '.graph.PROB-001.linked_adrs' architecture/index.yaml

# Which problems and ADRs reference the billing service?
yq '.graph | to_entries | .[] | select(.value.services[]? == "billing")' architecture/index.yaml

# All accepted ADRs
yq '.graph | to_entries | .[] | select(.value.type == "adr" and .value.status == "accepted")' architecture/index.yaml

# All open (active) problems
yq '.graph | to_entries | .[] | select(.value.type == "problem" and .value.status == "active")' architecture/index.yaml
```

---

## Design Principle

> The graph is a **projection** of your architecture, not the source of truth.

The source of truth is the individual YAML and Markdown files. The graph makes them navigable. Never edit `index.yaml` manually — it will be overwritten on the next `sda index` run.

---

## Keeping It Fresh

- Add `sda index --validate` to CI (non-blocking, warns if stale)
- Run `sda index` before opening a PR that adds or modifies problems/ADRs
- `sda status` shows the age of the last index generation

---

## Multi-Partition Architecture

When a project contains multiple systems (partitions), `sda index` generates **per-partition indexes** plus a **master index**.

### How It Works

A partition is any directory under `architecture/` that contains `model/` or `adr/` (excluding reserved names `inbox`, `model`, `adr`):

```
architecture/
  inbox/           # shared — all problems live here
  payments/     # partition
    model/
    adr/
  catalog/             # partition
    model/
  adr/             # root-level ADRs (cross-system)
```

Running `sda index` produces:

```
architecture/
  index.yaml                 # master — all nodes, with systems: key
  payments/index.yaml     # payments partition only
  catalog/index.yaml             # catalog partition only
```

### Master Index

The master index includes all nodes from all partitions plus:
- A top-level `systems:` key listing partition names
- A `system:` field on each node indicating which partition it belongs to
- Root-level ADRs (from `architecture/adr/`)
- Unrouted problems (no `system:` field or system doesn't match a partition)

```yaml
systems:
  - catalog
  - payments
graph:
  PROB-001:
    type: problem
    system: payments
    ...
```

### Per-Partition Index

Each partition index contains only nodes scoped to that system — its routed problems, its services, and its ADRs. No `systems:` key. Useful for system-specific tooling and dashboards.

### Querying by System

```bash
# All problems for payments
yq '.graph | to_entries | .[] | select(.value.system == "payments")' architecture/index.yaml

# All systems
yq '.systems' architecture/index.yaml
```

### Backward Compatibility

Projects without partitions (no partition directories under `architecture/`) continue to produce a single `index.yaml` with no `systems:` key — fully backward compatible.
