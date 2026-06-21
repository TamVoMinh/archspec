## ADDED Requirements

### Requirement: depends_on targets must be registered services
`sda check` SHALL report an ERROR when a service's `depends_on` lists a name that is not a
registered service in the model. Under `--strict`, such an error SHALL cause a non-zero exit.

#### Scenario: Unknown depends_on target fails strict check
- **WHEN** service `api` declares `depends_on: [ghost]` and `ghost` is not defined
- **THEN** `sda check` SHALL report an error naming `ghost`
- **THEN** `sda check --strict` SHALL exit non-zero

#### Scenario: Valid dependencies pass
- **WHEN** service `api` declares `depends_on: [db]` and `db` is defined
- **THEN** `sda check --strict` SHALL NOT report a dependency error for `api`

### Requirement: Problem and ADR service references are validated
`sda check` SHALL report a WARNING when a problem's `services:` list or an ADR's
`## Affected Services` section references a name that is not a registered service. Warnings SHALL
NOT cause `--strict` to fail.

#### Scenario: Unknown problem service reference warns without failing
- **WHEN** PROB-001 lists service `nope` which is not registered
- **THEN** `sda check` SHALL report a warning naming `nope`
- **THEN** `sda check --strict` SHALL still exit 0 (no errors)

### Requirement: Partitioned reference validation uses the full registry
When partitions exist, `sda check` SHALL validate each partition's `depends_on` against that
partition's registry, and SHALL validate shared-inbox problem references against the union of all
partition registries.

#### Scenario: Partition depends_on validated per partition
- **WHEN** partition `payments` defines `svc-orders` with `depends_on: [missing]` and `missing` is not defined in that partition
- **THEN** `sda check --strict` SHALL exit non-zero with an error naming `missing`
