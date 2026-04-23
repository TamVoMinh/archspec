## ADDED Requirements

### Requirement: Per-partition breakdown in status
When partitions exist, `sda status` SHALL display a per-partition breakdown showing problem counts, ADR counts, and service counts for each partition.

#### Scenario: Status with two partitions
- **WHEN** partitions `payments` and `catalog` exist
- **WHEN** `payments` has 2 problems, 1 ADR, 3 services
- **WHEN** `catalog` has 1 problem, 0 ADRs, 1 service
- **THEN** `sda status` SHALL display a section for each partition with its counts

#### Scenario: Unrouted problems shown separately
- **WHEN** PROB-005 has no `system:` field
- **THEN** `sda status` SHALL show unrouted problems in a separate line or summary

### Requirement: Status backward compatible without partitions
When no partitions exist, `sda status` SHALL display the current flat format with no partition sections.

#### Scenario: No partitions
- **WHEN** `discover_partitions()` returns an empty list
- **THEN** `sda status` output SHALL be identical to current behavior

### Requirement: Systems count in status header
When partitions exist, `sda status` SHALL show a "Systems" row listing the count and names of discovered partitions.

#### Scenario: Systems row displayed
- **WHEN** partitions `payments` and `catalog` exist
- **THEN** `sda status` SHALL display "Systems  2 (catalog, payments)" or equivalent
