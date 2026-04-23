## 1. Inbox Folder Layout — Problem Discovery

- [x] 1.1 Add a second glob `PROB-[0-9]*/PROB-[0-9]*.yaml` to the problem scanner in `cli/src/sda/commands/index.py`
- [x] 1.2 Merge results from both globs, deduplicating by problem ID
- [x] 1.3 Add duplicate detection — error if same PROB-ID exists in both flat and folder layouts
- [x] 1.4 Update `cli/src/sda/commands/check.py` to discover problems using the same dual-glob logic
- [x] 1.5 Write tests: flat-only, folder-only, mixed, and duplicate scenarios

## 2. Capture with Attachments

- [x] 2.1 Add `--attach` option (multiple allowed) to `sda capture` in `cli/src/sda/commands/capture.py`
- [x] 2.2 Validate each `--attach` path exists before creating any files
- [x] 2.3 When `--attach` is provided: create `PROB-XXX/` folder, write `PROB-XXX.yaml` inside, copy attached files preserving original filenames
- [x] 2.4 When `--attach` is not provided: preserve existing flat file behavior
- [x] 2.5 Update the next-ID calculation to also scan `PROB-XXX/` folders for existing IDs
- [x] 2.6 Write tests: capture with single attachment, multiple attachments, non-existent path, and no attachment (backward compat)

## 3. Hierarchical Service Model

- [x] 3.1 Add recursive `services.yaml` discovery in `cli/src/sda/commands/index.py` — walk `architecture/model/` subdirectories
- [x] 3.2 Assign `group` field to services based on their subdirectory name
- [x] 3.3 Create `type: group` nodes in `index.yaml` with `children` lists
- [x] 3.4 Root-level services (in `architecture/model/services.yaml`) have no group — backward compatible
- [x] 3.5 Add global service name uniqueness check to `cli/src/sda/validators/services.py`
- [x] 3.6 Extend staleness and ownership validation to all discovered `services.yaml` files
- [x] 3.7 Update `sda status` to show per-group service counts when hierarchy exists
- [x] 3.8 Write tests: root-only, single group, multiple groups, duplicate service name across groups

## 4. Documentation

- [x] 4.1 Update `docs/concepts/problems.md` — document the folder layout convention
- [x] 4.2 Update `docs/concepts/knowledge-graph.md` — document `type: group` nodes and `group` field
- [x] 4.3 Update `README.md` CLI reference — document `--attach` flag on `sda capture`
- [x] 4.4 Add migration note: existing flat layouts continue to work, folder layout is opt-in
