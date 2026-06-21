## ADDED Requirements

### Requirement: ADRs declare machine-checkable constraints
An ADR SHALL be able to declare architectural constraints in a `## Constraints` section
containing a fenced `yaml` block (the section is optional). Each constraint has an `id`, an
optional `description`, and one constraint kind.
Constraints are expressed over the existing model — services and their `depends_on`, plus service
attributes (`type`, classification `labels`, `system`, `deprecated`). An ADR with no `##
Constraints` section is valid and unconstrained.

#### Scenario: A constraint is declared in an ADR
- **WHEN** an ADR's `## Constraints` block declares a `forbid` rule with `from`/`to` selectors
- **THEN** `sda` SHALL parse it as a constraint belonging to that ADR

#### Scenario: ADRs without constraints are unaffected
- **WHEN** an ADR has no `## Constraints` section
- **THEN** it SHALL remain valid and contribute no constraints

### Requirement: Constraint kinds and selectors
The core SHALL support at least two constraint kinds:
- `forbid` — there SHALL be no `depends_on` edge from any service matching `from` to any service
  matching `to`.
- `allowed-only-via` — a service matching `from` MAY depend on a service matching `to` only
  through a service matching `via`; a direct `from → to` edge SHALL be a violation.
A **selector** matches a service when every key it specifies matches: `name`, `type`,
`label` (dimension→value), `system`, `deprecated`.

#### Scenario: Forbid a direct dependency
- **WHEN** a `forbid` constraint bans `{type: frontend} → {type: postgres}` and a frontend
  service declares `depends_on` a postgres service
- **THEN** that edge SHALL be a violation

#### Scenario: Allowed-only-via routing
- **WHEN** an `allowed-only-via` constraint requires `from area=fulfillment` to reach
  `area=platform` only `via` service `gateway`, and a fulfillment service depends directly on a
  platform service
- **THEN** that direct edge SHALL be a violation

### Requirement: sda check enforces accepted-ADR constraints in CI
`sda check` SHALL evaluate the constraints declared by `accepted` ADRs against the model's
dependency graph and report each violation as an **error** (so `sda check --strict` fails in CI).
Constraints from `proposed` or `superseded` ADRs SHALL NOT be enforced. This SHALL work in both
flat and partitioned layouts.

#### Scenario: Violation fails strict check
- **WHEN** an accepted ADR's constraint is violated by the current service model
- **THEN** `sda check` SHALL report an error naming the ADR and the offending edge
- **THEN** `sda check --strict` SHALL exit non-zero

#### Scenario: Clean model passes
- **WHEN** all accepted ADRs' constraints are satisfied
- **THEN** `sda check` SHALL report no constraint errors

#### Scenario: Non-accepted ADR constraints are not enforced
- **WHEN** a `proposed` ADR declares a constraint that the model violates
- **THEN** `sda check` SHALL NOT fail on it (the decision isn't ratified)

### Requirement: Constraints are methodology-neutral primitives
The constraint kinds and selectors SHALL reference only model attributes (no methodology-specific
vocabulary). Methodology packs MAY supply higher-level constraint templates that expand to these
primitives, without changing the core.

#### Scenario: A pack template expands to core primitives
- **WHEN** a methodology pack defines a context-map "anti-corruption layer" rule
- **THEN** it SHALL expand to `forbid` / `allowed-only-via` constraints the core already verifies,
  with no core schema change
