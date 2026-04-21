## Why

The SDA CLI assumes a single-system architecture: one `architecture/inbox/`, one `model/services.yaml`, one `adr/` directory, one `index.yaml`. Real-world architecture hubs (like arch-hub) govern multiple systems — Payments, Catalog, shared platform — each with their own services, ADRs, and subgraphs. Currently everything is mixed in a single flat namespace, making it impossible to query "what's going on in system X?" or produce a scoped knowledge graph. The `system:` field was added to problems but the CLI has no structural support for partitions.

## What Changes

- The CLI discovers **partitions** inside `architecture/` by structural convention: any subdirectory containing `model/` or `adr/` is a partition.
- Each partition gets its own `model/services.yaml`, `adr/` directory, and auto-generated `index.yaml`.
- `sda index` produces per-partition indexes plus a master `architecture/index.yaml` that merges all partitions and adds cross-system edges.
- `sda check` validates per-partition service models, ADR references, and checks that problem `system:` fields match existing partitions.
- `sda status` shows a per-partition breakdown (problems, ADRs, services per partition).
- `sda capture` gains an optional `--system` flag to pre-assign the partition during capture.
- The inbox remains shared (`architecture/inbox/`) with global problem IDs. Problems route to partitions via the `system:` field at index time.
- When no partitions are discovered, **all commands behave exactly as before** — full backward compatibility.

## Capabilities

### New Capabilities
- `partition-discovery`: Structural auto-discovery of partitions inside `architecture/`. A directory with `model/` or `adr/` inside is a partition. Reserved names (`inbox`) are excluded. Returns an ordered list of partitions with name and path.
- `partitioned-index`: Per-partition `index.yaml` generation scoped to that partition's services, ADRs, and routed problems. Master `index.yaml` merges all partitions and annotates nodes with `system:` field. Unrouted problems (no `system:` field) appear in master only.
- `partitioned-status`: Per-partition breakdown in `sda status` output — problem counts, ADR counts, service counts per partition. Falls back to current flat display when no partitions exist.
- `partition-validation`: `sda check` validates that problem `system:` values match existing partition names, flags unrouted problems as warnings, and runs per-partition service/ADR checks.

### Modified Capabilities
<!-- No existing specs to modify -->

## Impact

- **CLI source**: `discovery.py` (new partition scanner), `index.py`, `check.py`, `status.py`, `capture.py` all need partition-awareness
- **File layout**: Repos adopting partitions restructure from `architecture/{model,adr}/` to `architecture/<partition>/{model,adr}/`. Existing flat repos are unaffected.
- **index.yaml schema**: Per-partition indexes are new files. Master index gains `systems:` top-level key and `system:` field on nodes.
- **Problem YAML schema**: `system:` field becomes meaningful (routed at index time, validated at check time). Currently optional, remains optional.
- **No breaking changes**: Repos without partitions see zero behavioral change.
