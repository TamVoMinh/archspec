## Context

The SDA CLI (`sda`) scans `architecture/inbox/` for problem files using a flat glob: `PROB-[0-9]*.yaml`. Services are read from a single `architecture/model/services.yaml`. Both assumptions break in real-world usage:

1. **Inbox**: Architecture problems arrive with attachments (emails, screenshots, PDFs). When a user places `PROB-003.yaml` inside a `PROB-003/` folder with co-located attachments, the scanner silently ignores it.
2. **Services**: Large enterprises organize services into product hierarchies (platform → apps → microservices). A single flat file becomes unwieldy and offers no grouping or scoping.

Current scanner code:
- `index.py` line 65: `inbox.glob("PROB-[0-9]*.yaml")` — flat files only
- `validators/services.py`: reads one `services.yaml` — no recursive discovery
- `capture.py`: always writes a bare file — no folder creation

## Goals / Non-Goals

**Goals:**
- Problem files in `PROB-XXX/PROB-XXX.yaml` folder layout are discovered by `sda index`, `sda check`, and `sda status`
- `sda capture --attach <file>...` creates a folder layout and copies attachments in
- `sda capture` without `--attach` continues to create flat files (backward compatible)
- `architecture/model/` supports subdirectories, each containing a `services.yaml` — the folder name implies a group/parent
- `sda index` merges all discovered `services.yaml` files and reflects hierarchy in `index.yaml`
- `sda status` reports service counts per group when hierarchy exists
- All existing flat layouts continue to work without changes

**Non-Goals:**
- GUI or interactive attachment picker — `--attach` takes file paths only
- Nested folders within a problem folder (e.g., `PROB-003/sub/`) — one level deep is sufficient
- Service hierarchy deeper than 2 levels — product → service is the target; deeper nesting is future work
- Renaming or moving existing `PROB-XXX.yaml` into folders automatically — that's a manual migration

## Decisions

### 1. Dual-path problem discovery

**Decision**: Extend the glob to match both `PROB-[0-9]*.yaml` (flat) and `PROB-[0-9]*/PROB-[0-9]*.yaml` (folder).

**Rationale**: Minimal change — the scanner runs two globs and merges results. No schema changes needed. The YAML content is identical in both layouts.

**Alternative considered**: Require all problems in folders. Rejected — too much friction for simple captures without attachments.

### 2. Folder creation on `--attach`

**Decision**: When `--attach` is provided, `sda capture` creates `PROB-XXX/PROB-XXX.yaml` and copies each attached file into `PROB-XXX/`. Without `--attach`, behavior is unchanged (bare file).

**Rationale**: The folder is only useful when there are attachments. Forcing folders for every problem adds noise.

**Alternative considered**: Always create folders, even without attachments. Rejected — unnecessary complexity for simple problems; breaks existing muscle memory.

### 3. Filesystem-based service hierarchy

**Decision**: `sda index` recursively discovers all `services.yaml` files under `architecture/model/`. Each subdirectory name becomes a group. Services in `architecture/model/services.yaml` are root-level. Services in `architecture/model/payments/services.yaml` belong to group `payments`.

**Rationale**: The filesystem IS the hierarchy — no schema changes to `services.yaml` itself. Users organize by creating folders, which is natural. Mirrors how monorepos use `package.json` or `CODEOWNERS` in subdirectories.

**Alternative considered**: Add a `children:` or `parent:` field inside `services.yaml`. Rejected — adds schema complexity and requires users to maintain cross-references manually. Filesystem hierarchy is self-evident and enforced by the OS.

### 4. Index representation of hierarchy

**Decision**: In `index.yaml`, add an optional `group` field to service nodes. Root services have no group. Grouped services have `group: <folder-name>`. The group itself appears as a node of `type: group`.

```yaml
graph:
  payments:
    type: group
    children: [svc-orders, svc-cache, svc-worker]
  svc-orders:
    type: service
    group: payments
    problems: [PROB-001]
    adrs: []
```

**Rationale**: Flat graph nodes remain queryable with `yq`. The `group` field is additive — existing queries that don't filter on it still work.

## Risks / Trade-offs

- **[Duplicate problem IDs]**: If both `PROB-001.yaml` and `PROB-001/PROB-001.yaml` exist, there's a conflict. → Mitigation: `sda check` reports an error if the same PROB-ID appears in both flat and folder layouts.
- **[Service name collisions across groups]**: A service named `api` in two different groups would collide in the flat graph. → Mitigation: Service names must be globally unique. `sda check` reports duplicates. Future: consider namespacing as `group/service`.
- **[Migration effort]**: Existing users with flat layouts need no changes. Users who manually created folders before this fix need no changes either — they'll just start working.
- **[Index schema change]**: Adding `group` and `type: group` to `index.yaml` is additive but could break consumers that expect only `problem`, `adr`, `service` types. → Mitigation: Document in changelog; the `type` field was already extensible.
