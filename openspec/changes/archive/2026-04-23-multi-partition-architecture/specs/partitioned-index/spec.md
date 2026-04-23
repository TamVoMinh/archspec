## ADDED Requirements

### Requirement: Per-partition index generation
When partitions exist, `sda index` SHALL generate one `index.yaml` per partition at `architecture/<partition>/index.yaml`. Each partition index SHALL contain only nodes scoped to that partition: its services (from `<partition>/model/`), its ADRs (from `<partition>/adr/`), and problems routed to it via the `system:` field.

#### Scenario: Partition index contains only scoped nodes
- **WHEN** partitions `payments` and `catalog` exist
- **WHEN** PROB-001 has `system: payments` and PROB-002 has `system: catalog`
- **THEN** `architecture/payments/index.yaml` SHALL contain PROB-001 but NOT PROB-002
- **THEN** `architecture/catalog/index.yaml` SHALL contain PROB-002 but NOT PROB-001

#### Scenario: Partition index includes partition-scoped services
- **WHEN** `architecture/payments/model/services.yaml` defines services `svc-orders` and `svc-cache`
- **THEN** `architecture/payments/index.yaml` SHALL include service nodes for `svc-orders` and `svc-cache`
- **THEN** `architecture/catalog/index.yaml` SHALL NOT include `svc-orders` or `svc-cache`

### Requirement: Master index merges all partitions
`sda index` SHALL always generate `architecture/index.yaml` as the master index. When partitions exist, the master index SHALL merge all partition graphs and add a `system:` field to each node indicating its partition. It SHALL include a top-level `systems:` key listing all discovered partition names.

#### Scenario: Master index with systems key
- **WHEN** partitions `payments` and `catalog` exist
- **THEN** `architecture/index.yaml` SHALL contain `systems: [catalog, payments]`
- **THEN** each node in the master graph SHALL have a `system:` field

#### Scenario: Master index backward compatible without partitions
- **WHEN** no partitions exist
- **THEN** `architecture/index.yaml` SHALL NOT contain a `systems:` key
- **THEN** the graph format SHALL be identical to the current output

### Requirement: Problem routing via system field
Problems from the shared inbox SHALL be routed to partition indexes based on their `system:` YAML field matching the partition directory name.

#### Scenario: Problem routed to matching partition
- **WHEN** PROB-001 has `system: payments`
- **WHEN** partition `payments` exists
- **THEN** PROB-001 SHALL appear in `architecture/payments/index.yaml`

#### Scenario: Problem without system field
- **WHEN** PROB-005 has no `system:` field
- **THEN** PROB-005 SHALL appear in the master `architecture/index.yaml` only
- **THEN** PROB-005 SHALL NOT appear in any partition index

### Requirement: Root-level ADRs in master index only
ADRs in `architecture/adr/` (root level) SHALL appear in the master index but NOT in any partition index. Only ADRs in `architecture/<partition>/adr/` appear in that partition's index.

#### Scenario: Root ADR excluded from partition indexes
- **WHEN** `architecture/adr/001-governance.md` exists
- **WHEN** partitions `payments` and `catalog` exist
- **THEN** ADR-001-GOVERNANCE SHALL appear in `architecture/index.yaml`
- **THEN** ADR-001-GOVERNANCE SHALL NOT appear in `architecture/payments/index.yaml` or `architecture/catalog/index.yaml`

#### Scenario: Partition ADR in partition index
- **WHEN** `architecture/payments/adr/002-caching.md` exists
- **THEN** ADR-002-CACHING SHALL appear in `architecture/payments/index.yaml`
- **THEN** ADR-002-CACHING SHALL appear in `architecture/index.yaml` with `system: payments`
