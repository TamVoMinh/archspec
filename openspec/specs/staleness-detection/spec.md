## ADDED Requirements

### Requirement: Services in services.yaml carry a last_reviewed field
Every service entry in `architecture/model/services.yaml` SHALL include a `last_reviewed` field in ISO 8601 date format (`YYYY-MM-DD`) and an `owner` field containing an email address.

#### Scenario: Service entry with both fields passes validation
- **WHEN** a service entry has `last_reviewed: 2026-01-10` and `owner: jane@company.com`
- **THEN** schema validation SHALL pass

#### Scenario: Service entry missing last_reviewed field fails validation
- **WHEN** a service entry does not contain `last_reviewed`
- **THEN** the staleness check script SHALL flag the service with `MISSING last_reviewed: <service-name>`

### Requirement: check-staleness.py detects services not reviewed within the staleness threshold
`scripts/check-staleness.py` SHALL read `architecture/model/services.yaml` and flag any service whose `last_reviewed` date is more than 180 days before today.

#### Scenario: Service reviewed within threshold passes
- **WHEN** a service's `last_reviewed` is 90 days ago
- **THEN** the script SHALL not flag it

#### Scenario: Service reviewed outside threshold is flagged
- **WHEN** a service's `last_reviewed` is 200 days ago
- **THEN** the script SHALL output `STALE (200d): <service-name> — last reviewed <date>`

#### Scenario: Service missing last_reviewed is flagged separately
- **WHEN** a service entry exists but has no `last_reviewed` field
- **THEN** the script SHALL output `MISSING last_reviewed: <service-name>`

### Requirement: Staleness check runs in CI as a non-blocking warning
`scripts/check-staleness.py` SHALL be executed in CI on every push. By default it SHALL exit with code `0` even when stale services are detected (warning mode). Teams MAY switch to blocking mode by changing the exit code to `1`.

#### Scenario: Staleness warnings appear in CI output
- **WHEN** one or more services are stale
- **THEN** CI SHALL log the warning messages and still report the step as successful in the default configuration
