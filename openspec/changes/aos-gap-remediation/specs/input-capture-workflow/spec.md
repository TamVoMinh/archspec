## ADDED Requirements

### Requirement: Inbox problem files support a draft status
The `status` field on inbox problem YAML files SHALL accept `draft` as a valid value. A `draft` problem file MAY have empty `services` and `symptoms` lists. Draft files SHALL not block CI.

#### Scenario: Draft file with empty services passes CI
- **WHEN** a problem file has `status: draft`, `services: []`, and `symptoms: []`
- **THEN** schema validation SHALL pass

#### Scenario: Active file with empty services fails CI
- **WHEN** a problem file has `status: active` and `services: []`
- **THEN** schema validation SHALL fail, requiring at least one service

### Requirement: Draft problems are triaged within the SLA defined in OWNERS.yaml
The system SHALL define a 48-hour triage SLA for draft inbox items in `OWNERS.yaml`. Outstanding drafts beyond the SLA SHALL be surfaced in monitoring.

#### Scenario: Draft SLA is defined in OWNERS.yaml
- **WHEN** `OWNERS.yaml` is read
- **THEN** `triage_policy.inbox_sla_hours` SHALL be present with a numeric value

#### Scenario: Stale drafts are detectable
- **WHEN** a problem file has `status: draft` and `created_at` is more than `inbox_sla_hours` hours ago
- **THEN** a staleness report or CI warning SHALL identify it as overdue for triage

### Requirement: aos capture command scaffolds a draft problem file
Running `aos capture "<title>"` SHALL create a new file at `architecture/inbox/PROB-<next-id>.yaml` pre-filled with `status: draft`, `source: adhoc`, and `created_at` set to today's date. All other fields SHALL be empty placeholders.

#### Scenario: Capture command creates a draft file
- **WHEN** `aos capture "API timeout investigation"` is run
- **THEN** a new file `PROB-XXX.yaml` SHALL exist in `architecture/inbox/` with `title: "API timeout investigation"`, `status: draft`, and `created_at: <today>`

#### Scenario: Next ID is auto-incremented
- **WHEN** the highest existing problem ID is `PROB-005`
- **THEN** the new file SHALL be named `PROB-006.yaml`
