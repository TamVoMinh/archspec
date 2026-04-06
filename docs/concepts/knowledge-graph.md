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
```

Three node types:
- **problem** — an inbox entry
- **adr** — a decision record
- **service** — a service referenced by any problem or ADR

---

## Generating the Graph

```bash
sda index                    # generate/overwrite architecture/index.yaml
sda index --validate         # non-blocking: check if the committed index is fresh
```

The graph is regenerated in CI on every push. A stale index triggers a warning (non-blocking by default).

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
