## ADDED Requirements

### Requirement: ADR template includes a Metadata block
Every new ADR file SHALL begin with a `## Metadata` section containing `status`, `date`, `superseded_by`, and `links` fields before any other content sections.

#### Scenario: New ADR created from template has Metadata block
- **WHEN** a contributor creates a new ADR using the official template
- **THEN** the file SHALL contain `## Metadata` as the first section with all four required fields

#### Scenario: ADR without Metadata block fails CI
- **WHEN** an ADR file is added that contains no `## Metadata` section
- **THEN** the CI ADR structure check SHALL fail and identify the file

### Requirement: ADR template includes all standard sections
Every ADR SHALL contain the sections `## Context`, `## Decision`, `## Alternatives`, `## Consequences`, and `## Affected Services` in that order after `## Metadata`.

#### Scenario: ADR with all required sections passes structure check
- **WHEN** an ADR file contains all six required sections in order
- **THEN** CI SHALL pass the ADR structure check

#### Scenario: ADR missing Alternatives section fails structure check
- **WHEN** an ADR omits `## Alternatives`
- **THEN** CI SHALL fail and report the missing section
