## 1. Partition Discovery

- [x] 1.1 Add `discover_partitions(arch_dir)` to `cli/src/sda/discovery.py` — scan direct children, return list of `(name, path)` tuples for dirs containing `model/` or `adr/`
- [x] 1.2 Reserve directory names `inbox`, `model`, `adr` — never treated as partitions
- [x] 1.3 Return partitions sorted alphabetically by name
- [x] 1.4 Write tests: partition with model/, partition with adr/, non-partition dir, reserved names, empty architecture/, mixed

## 2. Partitioned Index

- [x] 2.1 Refactor `_build_graph()` in `index.py` to accept optional partition scope (partition path, partition-scoped ADR dir, partition-scoped model dir, routed problems)
- [x] 2.2 Add problem routing logic: match problem `system:` field to partition name, collect unrouted problems separately
- [x] 2.3 When partitions exist: iterate partitions, build per-partition graph, write `architecture/<partition>/index.yaml`
- [x] 2.4 Build master index merging all partition graphs + root-level ADRs + unrouted problems, add `systems:` top-level key and `system:` field on each node
- [x] 2.5 When no partitions exist: preserve current behavior exactly (no `systems:` key, same paths)
- [x] 2.6 Root-level ADRs (`architecture/adr/`) appear in master index only, not in any partition index
- [x] 2.7 Write tests: single partition index, two partitions, unrouted problem in master only, root ADR in master only, no-partitions backward compat

## 3. Partitioned Check

- [x] 3.1 Update `check.py` to call `discover_partitions()` and branch on result
- [x] 3.2 When partitions exist: validate per-partition `model/services.yaml` and `adr/` plus root-level `adr/`
- [x] 3.3 Add `system:` field validation — warn if value doesn't match any partition name
- [x] 3.4 Add warning for problems with no `system:` field when partitions exist
- [x] 3.5 Ignore root `architecture/model/services.yaml` when partitions exist (leftover from flat layout)
- [x] 3.6 Write tests: system mismatch warning, missing system warning, per-partition service validation, backward compat

## 4. Partitioned Status

- [x] 4.1 Update `status.py` to detect partitions and display per-partition breakdown (problems, ADRs, services per partition)
- [x] 4.2 Add "Systems" row listing count and names when partitions exist
- [x] 4.3 Show unrouted problems count separately
- [x] 4.4 When no partitions exist: preserve current flat display exactly
- [x] 4.5 Write tests: status with partitions, status without partitions

## 5. Capture --system Flag

- [x] 5.1 Add `--system` option to `sda capture` in `capture.py`
- [x] 5.2 When `--system` is provided: include `system:` field in generated YAML
- [x] 5.3 When `--system` is not provided: omit `system:` field (current behavior)
- [x] 5.4 Write tests: capture with --system, capture without --system

## 6. Documentation

- [x] 6.1 Update `docs/concepts/problems.md` — document `system:` field and routing behavior
- [x] 6.2 Update `docs/concepts/knowledge-graph.md` — document per-partition indexes and master index
- [x] 6.3 Update `README.md` CLI reference — document `--system` flag on `sda capture`
- [x] 6.4 Add migration guide: how to move from flat layout to partitioned layout
