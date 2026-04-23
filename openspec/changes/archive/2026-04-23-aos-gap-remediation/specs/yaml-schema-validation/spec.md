## ADDED Requirements

### Requirement: Schema files exist for all AOS YAML types
The repository SHALL contain schema files at:
- `schemas/problem.schema.yaml` for inbox problem files
- `schemas/service.schema.yaml` for `services.yaml` entries
- `schemas/adr.schema.yaml` for ADR frontmatter metadata blocks

#### Scenario: Schema files are present in the repository
- **WHEN** the repository is cloned fresh
- **THEN** all three schema files SHALL exist under `schemas/`

### Requirement: Problem inbox files are validated against schema in CI
Every YAML file under `architecture/inbox/` SHALL be validated against `schemas/problem.schema.yaml` on every CI run. Files that fail validation SHALL block the merge.

#### Scenario: Valid problem file passes validation
- **WHEN** a problem YAML file contains all required fields (`id`, `title`, `source`, `type`, `created_at`, `services`, `symptoms`) with correct types
- **THEN** CI validation SHALL pass

#### Scenario: Problem file with invalid source value fails validation
- **WHEN** a problem YAML file has `source: teams` (not in the allowed enum)
- **THEN** CI validation SHALL fail and report the file path and the invalid field

#### Scenario: Problem file missing required field fails validation
- **WHEN** a problem YAML file is missing the `services` field
- **THEN** CI validation SHALL fail and report the missing field

### Requirement: Service model file is validated against schema in CI
`architecture/model/services.yaml` SHALL be validated against `schemas/service.schema.yaml` on every CI run.

#### Scenario: Valid service model passes validation
- **WHEN** every service entry has valid optional and required fields according to the schema
- **THEN** CI SHALL pass

#### Scenario: Service entry with unknown field type fails validation
- **WHEN** a service has `type: lambda` (not in the allowed enum)
- **THEN** CI SHALL fail and identify the offending service entry

### Requirement: Schema violations block merge
CI MUST exit with a non-zero code when any YAML file fails schema validation. Merging to the default branch SHALL be blocked until the schema error is resolved.

#### Scenario: Schema failure prevents merge
- **WHEN** a PR contains a problem YAML file that fails schema validation
- **THEN** the CI check SHALL fail and the PR merge button SHALL be disabled by GitHub branch protection
