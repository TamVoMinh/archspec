## ADDED Requirements

### Requirement: Validate system field matches partition
`sda check` SHALL warn when a problem's `system:` value does not match any discovered partition name.

#### Scenario: System matches partition
- **WHEN** PROB-001 has `system: payments`
- **WHEN** partition `payments` exists
- **THEN** `sda check` SHALL NOT produce a warning for PROB-001

#### Scenario: System does not match any partition
- **WHEN** PROB-005 has `system: unknown-system`
- **WHEN** no partition named `unknown-system` exists
- **THEN** `sda check` SHALL produce a warning: "PROB-005 references system 'unknown-system' but no matching partition exists"

#### Scenario: No system field is acceptable
- **WHEN** PROB-006 has no `system:` field
- **WHEN** partitions exist
- **THEN** `sda check` SHALL produce an informational warning: "PROB-006 has no system field — will not appear in any partition index"

### Requirement: Per-partition service validation
When partitions exist, `sda check` SHALL validate services in each partition's `model/services.yaml` independently, applying staleness and ownership checks per partition.

#### Scenario: Stale service in one partition
- **WHEN** `architecture/payments/model/services.yaml` has a service not reviewed in 180+ days
- **THEN** `sda check` SHALL flag that service as stale, indicating it belongs to partition `payments`

#### Scenario: Root model dir ignored when partitions exist
- **WHEN** partitions exist
- **WHEN** `architecture/model/services.yaml` also exists (leftover from flat layout)
- **THEN** `sda check` SHALL ignore `architecture/model/services.yaml` and only validate per-partition service files

### Requirement: Per-partition ADR validation
When partitions exist, `sda check` SHALL validate ADRs in each partition's `adr/` directory plus root-level `architecture/adr/`.

#### Scenario: ADR in partition validated
- **WHEN** `architecture/payments/adr/002-caching.md` exists
- **THEN** `sda check` SHALL apply ADR lifecycle validation to it

### Requirement: Capture with optional system flag
`sda capture` SHALL accept an optional `--system` flag to pre-assign the `system:` field in the generated problem YAML.

#### Scenario: Capture with system flag
- **WHEN** user runs `sda capture "title" --system payments`
- **THEN** the generated PROB YAML SHALL include `system: payments`

#### Scenario: Capture without system flag
- **WHEN** user runs `sda capture "title"` (no --system)
- **THEN** the generated PROB YAML SHALL NOT include a `system:` field
