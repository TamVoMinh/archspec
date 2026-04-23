## ADDED Requirements

### Requirement: Discover partitions by structure
The CLI SHALL discover partitions by scanning direct children of `architecture/`. A child directory is a partition if it contains a `model/` subdirectory, an `adr/` subdirectory, or both. The directory name becomes the partition name.

#### Scenario: Directory with model/ is a partition
- **WHEN** `architecture/payments/model/` exists
- **THEN** the CLI SHALL discover `payments` as a partition

#### Scenario: Directory with adr/ is a partition
- **WHEN** `architecture/catalog/adr/` exists (no model/)
- **THEN** the CLI SHALL discover `catalog` as a partition

#### Scenario: Directory without model/ or adr/ is not a partition
- **WHEN** `architecture/docs/` exists but contains neither `model/` nor `adr/`
- **THEN** the CLI SHALL NOT treat `docs` as a partition

#### Scenario: Reserved directories are never partitions
- **WHEN** `architecture/inbox/model/` exists
- **THEN** the CLI SHALL NOT treat `inbox` as a partition

#### Scenario: Reserved names
The CLI SHALL reserve the directory names `inbox`, `model`, and `adr` so they are never treated as partitions, regardless of their contents.

### Requirement: Partitions returned in sorted order
The CLI SHALL return discovered partitions sorted alphabetically by name.

#### Scenario: Multiple partitions discovered
- **WHEN** `architecture/` contains directories `catalog/model/` and `payments/model/`
- **THEN** `discover_partitions()` SHALL return `[catalog, payments]` in that order

### Requirement: Empty result means flat mode
When `discover_partitions()` returns an empty list, all commands SHALL behave identically to the current single-partition behavior. No change in paths, no change in output format.

#### Scenario: No partitions exist
- **WHEN** `architecture/` contains only `inbox/`, `model/`, and `adr/` (no partition directories)
- **THEN** `discover_partitions()` SHALL return an empty list
- **THEN** all commands SHALL use `architecture/model/`, `architecture/adr/`, and `architecture/index.yaml` as before
