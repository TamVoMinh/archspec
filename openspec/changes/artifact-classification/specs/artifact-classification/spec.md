## ADDED Requirements

### Requirement: All architecture entities carry classification labels
Every architecture entity SHALL support an optional `labels` map of `dimension → value` —
problems, ADRs, components (services), and boundaries (systems/partitions) — classifying it
along named dimensions. `labels` is optional (absent labels are valid). Boundaries MUST be
labelable, since a methodology pack expresses concepts like a DDD bounded context as a `system`
plus a `criticality` label.

#### Scenario: A service is labeled
- **WHEN** a service declares `labels: { area: payments, criticality: core }`
- **THEN** the model SHALL record those labels on the service

#### Scenario: A problem is labeled
- **WHEN** a problem declares `labels: { area: payments }`
- **THEN** the model SHALL record that label on the problem

#### Scenario: A boundary is labeled
- **WHEN** a system/partition declares `labels: { criticality: core }`
- **THEN** the model SHALL record that label on the boundary (so a pack can treat it as, e.g., a
  core-subdomain bounded context)

#### Scenario: An ADR is labeled
- **WHEN** an ADR declares a label (e.g. `area: payments`)
- **THEN** the model SHALL record it so decisions are findable by that dimension

#### Scenario: Labels are optional
- **WHEN** an entity declares no `labels`
- **THEN** it SHALL remain valid

### Requirement: Boundary labels have a defined location
Because partitions are directories rather than files, a system/partition SHALL have a defined
place to carry its `labels` (a per-partition metadata file, e.g. `architecture/<partition>/`
metadata). The root (flat) project SHALL likewise have a place for project-level labels.

#### Scenario: Partition metadata holds labels
- **WHEN** a partition has a metadata file declaring `labels`
- **THEN** `sda` SHALL read those labels and attach them to that partition/system

### Requirement: Configurable dimensions; vocabularies open by default
The core SHALL ship a small set of default dimension **names** — `area`, `criticality`,
`lifecycle` — and SHALL NOT hardcode methodology-specific vocabularies. `area` and `criticality`
SHALL default to **open** (no fixed values), so a project or a methodology pack supplies the
vocabulary; `lifecycle` MAY ship a neutral default vocabulary (e.g. `active`, `deprecated`,
`retired`). Projects SHALL be able to declare additional dimensions and override any vocabulary.
A free-form `tags` list SHALL remain available as an unconstrained escape hatch.

#### Scenario: Default dimension names available, open vocab
- **WHEN** no classification config is provided
- **THEN** the `area`, `criticality`, `lifecycle` dimensions SHALL be available
- **THEN** `area` and `criticality` SHALL accept any value (open) until a project/pack closes them

#### Scenario: Project or pack closes a vocabulary
- **WHEN** config (or a methodology pack) sets `criticality` values to a specific set
- **THEN** that set SHALL become the vocabulary validated for `criticality`

#### Scenario: Project declares a new dimension
- **WHEN** config declares a dimension beyond the defaults
- **THEN** that dimension SHALL be available for labeling and validation

### Requirement: Label values are validated against the vocabulary
`sda check` SHALL validate label values against the declared vocabulary: a value outside a
dimension's declared `values` SHALL be an error; a dimension declared without `values` SHALL
accept any value; `tags` SHALL never be validated. Structural validation (that `labels` is a
string→string map) MAY be done by the YAML schema (yamale), but value-against-vocabulary
validation is config-driven and lives in `sda check`, not the static schema.

#### Scenario: Out-of-vocabulary value fails
- **WHEN** a dimension declares a closed vocabulary and an artifact uses a value not in it
- **THEN** `sda check` SHALL report an error

#### Scenario: Open dimension accepts any value
- **WHEN** a dimension is declared without `values`
- **THEN** any value for that dimension SHALL be accepted

### Requirement: Labels are surfaced for query, navigation, and AI
Labels SHALL be carried into the generated index (so they are queryable), exposed to the viewer
so it can group/filter by any dimension, and included in AI export so agents receive
classification context.

#### Scenario: Labels appear in the index
- **WHEN** the index is generated for a labeled artifact
- **THEN** the artifact's node SHALL include its labels

#### Scenario: Group by a dimension
- **WHEN** the viewer groups by a classification dimension
- **THEN** artifacts SHALL be grouped by their value on that dimension (with a leftover bucket
  for artifacts that have no value)

### Requirement: Classification is methodology-neutral and plugin-ready
The core classification SHALL define only dimensions and values, not methodology semantics.
Methodology-specific vocabularies, node stereotypes, relationship types, and checks SHALL be
supplied by external packs as configuration, without changing the core schema.

#### Scenario: A methodology pack supplies a vocabulary without core change
- **WHEN** a methodology pack declares the `criticality` vocabulary `{core, supporting, generic}`
- **THEN** the core SHALL accept and validate those values with no change to the core schema

### Requirement: Labels do not duplicate existing first-class fields
Existing first-class fields SHALL remain the source of truth and SHALL NOT be silently shadowed
by labels: a problem's `type`/`source`/`status`, a service's `type`/`deprecated`, and ADR
lifecycle stay as-is. `labels` is for additional, cross-cutting classification (e.g. `area`).
A dimension SHALL NOT redefine an existing first-class field; where overlap is desired (e.g. a
`lifecycle` view), it SHALL be derived from the existing field rather than duplicated.

#### Scenario: Existing fields are not duplicated by labels
- **WHEN** a problem has `status: active` and also carries labels
- **THEN** `status` SHALL remain the source of truth for status
- **THEN** labels SHALL NOT introduce a second, conflicting status value
