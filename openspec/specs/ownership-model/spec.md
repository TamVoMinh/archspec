## ADDED Requirements

### Requirement: OWNERS.yaml defines roles, responsibilities, and SLAs
The repository root SHALL contain `OWNERS.yaml` declaring at minimum: an `architecture_lead` role with named owner and `triage_sla_hours`, a `contributors` list with domain assignments, and a `triage_policy` block with `adr_review_required_approvers` and `adr_acceptance_requires`.

#### Scenario: OWNERS.yaml is present with all required sections
- **WHEN** `OWNERS.yaml` is read
- **THEN** it SHALL contain `roles.architecture_lead`, `roles.contributors`, `triage_policy`, and `domain_ownership` keys

#### Scenario: OWNERS.yaml missing architecture_lead fails schema validation
- **WHEN** `OWNERS.yaml` does not define `roles.architecture_lead`
- **THEN** CI schema validation SHALL fail

### Requirement: CODEOWNERS enforces mandatory PR reviewers
`.github/CODEOWNERS` SHALL map each AOS path to its responsible owners such that:
- `architecture/model/` changes require the architecture lead
- `schemas/` changes require the architecture lead
- ADR files touching a domain require that domain's owner

#### Scenario: Service model PR requires architecture lead review
- **WHEN** a PR modifies any file under `architecture/model/`
- **THEN** GitHub SHALL automatically request a review from the architecture lead

#### Scenario: Domain-specific ADR requires domain owner review
- **WHEN** a PR adds an ADR file whose name contains a service name (e.g., `billing`)
- **THEN** GitHub SHALL automatically request review from the billing domain owner

### Requirement: Domain ownership covers all services in services.yaml
Every service key in `architecture/model/services.yaml` SHALL have a corresponding entry in `OWNERS.yaml` under `domain_ownership`.

#### Scenario: Service with defined owner
- **WHEN** `services.yaml` contains a service `billing` and `domain_ownership.billing` is set in `OWNERS.yaml`
- **THEN** the ownership check SHALL pass

#### Scenario: Service without defined owner
- **WHEN** `services.yaml` contains a service with no corresponding `domain_ownership` entry in `OWNERS.yaml`
- **THEN** CI SHALL emit a warning identifying the unowned service
