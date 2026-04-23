## ADDED Requirements

### Requirement: Inbox YAML status field accepts draft, active, and resolved values
The `status` field on inbox problem files SHALL be optional. When present, it MUST be one of `draft`, `active`, or `resolved`. An absent `status` field SHALL be treated as `active` by tooling.

#### Scenario: File with status draft is valid
- **WHEN** an inbox YAML file contains `status: draft`
- **THEN** schema validation SHALL pass

#### Scenario: File with status active is valid
- **WHEN** an inbox YAML file contains `status: active`
- **THEN** schema validation SHALL pass

#### Scenario: File with invalid status value fails validation
- **WHEN** an inbox YAML file contains `status: pending`
- **THEN** schema validation SHALL fail and report the invalid value

#### Scenario: File with no status field is valid
- **WHEN** an inbox YAML file has no `status` key
- **THEN** schema validation SHALL pass, treating the entry as active

### Requirement: Draft inbox files allow empty services and symptoms
When `status: draft` is set, the `services` and `symptoms` fields SHALL accept empty lists (`[]`) without failing validation. When `status` is `active` or `resolved`, `services` and `symptoms` SHALL require at least one entry each.

#### Scenario: Active file with empty services fails
- **WHEN** a problem file has `status: active` and `services: []`
- **THEN** schema validation SHALL fail requiring at least one service

#### Scenario: Draft file with empty symptoms passes
- **WHEN** a problem file has `status: draft` and `symptoms: []`
- **THEN** schema validation SHALL pass
