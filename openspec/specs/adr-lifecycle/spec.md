## ADDED Requirements

### Requirement: ADR status field is mandatory
Every ADR file in `architecture/adr/` SHALL contain a `status` field in its `## Metadata` block. Valid values are `proposed`, `accepted`, `rejected`, `superseded`, and `deprecated`.

#### Scenario: Valid ADR passes CI
- **WHEN** an ADR file contains `- status: accepted` in its `## Metadata` block
- **THEN** the CI schema check SHALL pass with no errors

#### Scenario: Missing status field fails CI
- **WHEN** an ADR file does not contain a `status` field
- **THEN** the CI check SHALL fail and report the filename and missing field

#### Scenario: Invalid status value fails CI
- **WHEN** an ADR file contains `- status: in-review` (not a valid state)
- **THEN** the CI check SHALL fail and report the invalid value

### Requirement: ADR state machine is enforced
The system SHALL enforce the following valid state transitions. Transitions outside this set SHALL be rejected by CI.
- `proposed` → `accepted`
- `proposed` → `rejected`
- `accepted` → `superseded`
- `accepted` → `deprecated`

#### Scenario: Superseded ADR must name its replacement
- **WHEN** an ADR has `- status: superseded` in its metadata
- **THEN** the CI check SHALL verify that `superseded_by` is set to a non-null ADR identifier

#### Scenario: Superseded ADR without replacement fails CI
- **WHEN** an ADR has `- status: superseded` and `- superseded_by: ~`
- **THEN** the CI check SHALL fail with a message indicating the missing `superseded_by` value

### Requirement: Accepted ADRs may not reference deprecated services
No `accepted` ADR SHALL reference a service in `services.yaml` that carries a `deprecated: true` flag.

#### Scenario: Accepted ADR references active service
- **WHEN** an accepted ADR lists a service that exists and is not deprecated
- **THEN** the CI check SHALL pass

#### Scenario: Accepted ADR references deprecated service
- **WHEN** an accepted ADR references a service marked `deprecated: true`
- **THEN** the CI check SHALL fail with a message identifying the ADR and the deprecated service
