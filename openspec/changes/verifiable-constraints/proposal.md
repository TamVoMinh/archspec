## Why

Benchmarking SDA against its **own** first-class purpose (why-archspec.md), it meets ~8 of its 11
stated promises. The one gap that undercuts its core thesis is **verification**:

> "A decision that cannot be verified is aspirational documentation. ArchSpec closes the loop —
> decisions define constraints, and those constraints are validated automatically."

Today `sda check` validates the *governance scaffolding* around decisions (ADR structure,
lifecycle, staleness, ownership, reference existence, label vocabularies) — but **not the
architectural constraints the ADRs themselves declare**. An ADR may state "the API layer
integrates with the data store only through the approved service"; nothing checks it. The loop is
not closed. This change closes it.

(The full benchmark, including the two smaller gaps — #2 cross-partition ADR↔problem backlink and
#3 commit→decision linkage — is recorded in design.md. This change targets #4, the headline.)

## What Changes

- An ADR may declare **machine-checkable constraints** — architectural fitness functions — in a
  `## Constraints` section (a fenced ```yaml block), expressed over the model SDA already has:
  services, `depends_on`, classification labels, partitions, and `deprecated`.
- **`sda check` enforces constraints from `accepted` ADRs** against the dependency graph; a
  violation is an **error** (fails `--strict` in CI). This is what "closes the loop."
- v1 constraint kinds: `forbid` (no dependency from A→B) and `allowed-only-via` (A may reach B
  only through C). Selectors match services by `name`, `type`, `label`, `system`, `deprecated`.
- Methodology-neutral primitives — a future `methodology-packs` pack (DDD) can ship constraint
  *templates* (e.g. context-map ACL rules) that expand to these primitives, with no core change.

## Capabilities

### New Capabilities
- `constraint-verification`: ADRs declare architectural constraints that `sda check` verifies
  against the service/dependency model in CI — turning accepted decisions into enforced rules.

## Impact

- **CLI**: a new `sda check` validator that parses ADR constraint blocks and evaluates them
  against the `depends_on` graph (flat + partitioned).
- **ADR template/schema**: an optional `## Constraints` section convention; documented.
- **Docs**: `docs/concepts/decisions.md` gains the constraints section; a verification note in
  the knowledge-graph/check docs.
- **Backward compatible**: ADRs without a `## Constraints` section are unaffected.
- **Foundation for `methodology-packs`**: packs supply constraint templates over this engine.
