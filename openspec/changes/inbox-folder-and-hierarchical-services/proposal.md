## Why

The SDA CLI assumes a flat structure for both the inbox (`PROB-*.yaml` as bare files) and the service model (single `services.yaml`). In practice, architecture problems arrive with attachments (emails, screenshots, PDFs) and service models grow beyond a single flat list in large enterprises. Without native support, users work around these limits manually — breaking `sda index` and `sda check` in the process.

Confirmed during first real-world usage on Payments (arch-hub):
- PROB-003 placed in a folder (`PROB-003/PROB-003.yaml`) with attachments → `sda index` does not discover it
- 5 services in a product hierarchy (payments → svc-orders, svc-cache, svc-worker) but no way to express parent-child relationships

## What Changes

- **Inbox folder scanning**: `sda index`, `sda check`, and `sda capture` recognize both `PROB-XXX.yaml` (flat) and `PROB-XXX/PROB-XXX.yaml` (folder) layouts in `architecture/inbox/`
- **`sda capture --attach`**: New flag to attach files when capturing a problem — auto-creates a folder instead of a bare file
- **Hierarchical service model**: Support split `services.yaml` files in subdirectories under `architecture/model/` — the folder structure defines the hierarchy
- **`sda index` merges service files**: The indexer recursively discovers all `services.yaml` files under `architecture/model/` and merges them into `index.yaml` with parent-child relationships

## Capabilities

### New Capabilities
- `inbox-folder-layout`: Support for `PROB-XXX/PROB-XXX.yaml` folder-based problems with co-located attachments, alongside the existing flat file layout
- `capture-attach`: `--attach` flag on `sda capture` to copy files into a problem folder
- `hierarchical-services`: Split `services.yaml` into subdirectories with recursive discovery and parent-child relationships in the index

### Modified Capabilities

## Impact

- **`cli/src/sda/commands/index.py`**: Problem scanner glob pattern must also match `PROB-*/PROB-*.yaml`; service scanner must recursively discover `services.yaml` files
- **`cli/src/sda/commands/capture.py`**: Add `--attach` option, conditionally create folder layout
- **`cli/src/sda/validators/services.py`**: Must handle multiple `services.yaml` files
- **`cli/src/sda/commands/check.py`**: Must find problems in both flat and folder layouts
- **`schemas/`**: YAML schema for `services.yaml` may need `children` or `group` field
- **`docs/concepts/problems.md`**: Document the folder layout convention
- **`docs/concepts/knowledge-graph.md`**: Document hierarchical service model
- **Backward compatible**: Existing flat layouts continue to work unchanged
