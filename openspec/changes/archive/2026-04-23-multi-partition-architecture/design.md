## Context

The SDA CLI currently assumes all architecture artifacts live in a single flat namespace:
- `architecture/inbox/` — all problems
- `architecture/model/services.yaml` — all services
- `architecture/adr/` — all ADRs
- `architecture/index.yaml` — single knowledge graph

This works for single-system repos. But architecture hubs (like arch-hub) govern multiple systems. Problems already carry a `system:` field, but the CLI ignores it. Services from different systems are mixed. There's no way to produce a system-scoped knowledge graph or status report.

The recent `inbox-folder-and-hierarchical-services` change added `discovery.py` with shared discovery utilities and recursive service scanning. This change builds on that foundation.

## Goals / Non-Goals

**Goals:**
- Support per-system partitions with their own services, ADRs, and scoped indexes
- Auto-discover partitions by structural convention (no config file required)
- Route shared-inbox problems to partitions via the `system:` field
- Maintain full backward compatibility — repos without partitions see no change
- Per-partition breakdown in `sda status`
- Validation that `system:` values match existing partitions

**Non-Goals:**
- Nested/recursive sub-partitions (e.g., `payments/svc-orders/`) — future work
- Per-partition inboxes — inbox remains shared
- Per-partition OWNERS.yaml — ownership stays repo-wide
- `sda init` scaffolding for partitions — manual directory creation for now
- Cross-system edge tracking in the master index (e.g., a problem spanning two systems) — future work

## Decisions

### D1: Structural auto-discovery over manifest file

**Decision**: A directory directly under `architecture/` is a partition if it contains `model/` or `adr/` (or both). No config file needed.

**Alternatives considered**:
- *Manifest file* (`architecture/sda.yaml` listing partitions): Explicit but requires maintenance. Doesn't auto-adapt when directories are created.
- *Marker file* (`_partition.yaml` in each partition): Self-describing but litters small files.

**Rationale**: Structural discovery is zero-config and Git-native. Creating `architecture/payments/model/` is enough to register a partition. Same philosophy as `__init__.py` turning a directory into a Python package.

### D2: `inbox` is a reserved directory name

**Decision**: `architecture/inbox/` is always the shared inbox. It is never treated as a partition even if someone creates `inbox/model/` inside it.

**Rationale**: Inbox is a fundamentally different concept from a partition. It holds unrouted problems before system assignment.

### D3: Problems route to partitions via `system:` field

**Decision**: At index time, each problem's `system:` value is matched against partition directory names. A problem with `system: payments` appears in `architecture/payments/index.yaml`. Problems without a `system:` field appear only in the master index.

**Alternatives considered**:
- *Per-partition inboxes*: Problems captured directly into `architecture/payments/inbox/`. Rejected because problems often arrive before their system is known.
- *Routing config*: A mapping of system values to partitions. Rejected as unnecessary when names match directly.

### D4: Global problem IDs with shared inbox

**Decision**: Problem IDs (PROB-001, PROB-002, ...) are globally unique across the entire repo. The inbox is shared.

**Rationale**: Global IDs are unambiguous in cross-system discussions. Per-system IDs would create "PROB-001 in payments vs PROB-001 in catalog" confusion.

### D5: Per-partition index.yaml plus master index

**Decision**: `sda index` produces:
- `architecture/<partition>/index.yaml` — scoped graph for that partition only
- `architecture/index.yaml` — master graph merging all partitions with `system:` annotations on every node

The master index gains a top-level `systems:` key listing discovered partition names.

### D6: Partition-aware discovery functions in discovery.py

**Decision**: Add `discover_partitions(arch_dir)` to `discovery.py`. All commands use this to detect multi-partition mode. When partitions are found, commands iterate over each; when none are found, they use the existing flat paths.

The branching logic lives in each command, not in discovery.py. Discovery provides data; commands decide behavior.

### D7: Per-partition ADR directories

**Decision**: Each partition can have its own `adr/` directory. ADRs in `architecture/<partition>/adr/` are scoped to that partition. A root-level `architecture/adr/` directory holds repo-wide / cross-system ADRs (included in master index, not in any partition index).

## Risks / Trade-offs

- **[Naming collision]** A partition named `model` or `adr` would conflict with the flat-mode directories. → Mitigation: reserve `model`, `adr`, and `inbox` as directory names that cannot be partitions.
- **[System field mismatch]** User types `system: payments_xd` (underscore) but partition is `payments` (dash). → Mitigation: `sda check` flags unmatched `system:` values as warnings.
- **[Migration effort]** Existing repos must restructure directories to adopt partitions. → Mitigation: fully optional, flat repos work unchanged. Document migration steps.
- **[Index size]** Master index duplicates nodes from partition indexes. → Acceptable for the scale of architecture repos (tens to hundreds of nodes, not thousands).
