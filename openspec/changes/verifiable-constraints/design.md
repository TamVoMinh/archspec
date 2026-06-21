## Context

SDA's first-class purpose is to make architectural *decisions* first-class: captured, traceable,
queryable, **verifiable in CI**, and AI-legible. Benchmarked against that purpose, SDA delivers
most of it — except the verification promise it makes loudest. This change closes that loop.

### Benchmark — SDA vs. its own first-class objective

| # | First-class objective | SDA delivers it via | Score |
|---|---|---|---|
| 1 | Every problem captured before solutions | `sda capture` → inbox | ✅ Met |
| 2 | Every decision traces back to a problem | ADR `links:` + index | ⚠️ Partial — cross-partition backlink bug (`linked_adrs: []`) |
| 3 | Every commit references its decision | — (no linter) | ❌ Gap |
| 4 | **Every constraint in a decision validated in CI** | `sda check` (scaffolding only) | ⚠️ **Partial — this change** |
| 5 | Every service has owner + review date | `services.yaml` + `sda check` | ✅ Met |
| 6 | Decisions first-class, versioned in Git | ADRs in-repo | ✅ Met |
| 7 | Architecture is queryable | `sda index` + `sda graph` | ✅ Met (caveat #2) |
| 8 | AI-legible map | `index.yaml` + model export | ✅ Met |
| 9 | No signal lost (capture intake) | `sda capture` | ✅ Met |
| 10 | Lightweight, Git-native, runs in CI | pip CLI + Actions + YAML/MD | ✅ Met |
| 11 | De-bottleneck the architect | OWNERS + SLAs + PR gates | ✅ Met |

Score: 8 Met / 2 Partial / 1 Gap. #4 is the headline — `sda check` verifies the scaffolding
*around* decisions, not the architectural constraints *inside* them. #2 (a bug) and #3 (commit
linkage) are smaller, related follow-ups, out of scope here.

## Goals / Non-Goals

**Goals**
- Let an ADR declare machine-checkable architectural constraints over SDA's existing model.
- Enforce accepted ADRs' constraints in `sda check` (errors; fails `--strict` in CI).
- Keep it methodology-neutral; be the engine that methodology packs build templates on.

**Non-Goals**
- Not a general policy/predicate DSL — a small, dependency-shaped constraint set for v1.
- Not verifying against running systems or source code — only against the SDA model (services,
  `depends_on`, labels, partitions). (Code-level conformance is a separate, larger problem.)
- Not commit→decision linkage (#3) or the backlink bug (#2) — tracked separately.

## Decisions

### Decision 1: Constraints live in the ADR (the decision that declares them)
**Choice:** An ADR declares constraints in a `## Constraints` section containing a fenced
```yaml block. They travel with the decision, render in the viewer, and version in Git.
**Rationale:** The purpose is "constraints *in a decision*." A separate constraints file would
divorce the rule from its rationale. Reuses the existing ADR-parsing pattern (metadata block,
affected-services section).

### Decision 2: Verify over the model SDA already has
**Choice:** Constraints are evaluated against the service `depends_on` graph plus service
attributes (`type`, classification `labels`, `system`, `deprecated`) — the data already in the
index. No new model is required.
**Rationale:** Closes the loop with what exists; no dependency on code analysis or a new layer.

### Decision 3: v1 constraint kinds + selectors
**Choice:**
- `forbid` — no `depends_on` edge from a `from` selector to a `to` selector.
- `allowed-only-via` — `from` may reach `to` only through a `via` selector (gateway/ACL pattern).
- **Selectors** match a service when all given keys match: `name`, `type`, `label: {dim: val}`,
  `system`, `deprecated`.
**Rationale:** These two cover the real cases (layering bans, boundary/ACL routing, "no direct DB
from frontend", "no cross-partition dep except via an approved service"). More kinds (cycles,
must-own) can come later.

### Decision 4: Only `accepted` ADRs bind; violations are errors
**Choice:** Constraints from `accepted` ADRs are enforced as errors (fail `--strict`). `proposed`
/`superseded` ADRs' constraints are ignored. Each violation reports the ADR id and the offending
edge.
**Rationale:** Mirrors the existing accepted-ADR rules; only ratified decisions constrain.

### Decision 5: Engine for methodology packs
**Choice:** These primitives are methodology-neutral; a `methodology-packs` pack (DDD first) can
ship higher-level constraint *templates* (context-map ACL/OHS rules) that expand to `forbid` /
`allowed-only-via`, with no core change.

## Example

```yaml
# in an ADR under "## Constraints"
- id: apps-integrate-via-gateway
  description: fulfillment services reach the platform area only through the approved gateway
  allowed-only-via:
    from: { label: { area: fulfillment } }
    to:   { label: { area: platform } }
    via:  { name: gateway }
- id: no-direct-db-from-frontend
  forbid:
    from: { type: frontend }
    to:   { type: postgres }
```

## Risks / Trade-offs

- **Markdown parsing fragility** — mitigated by a single fenced ```yaml block under a fixed
  `## Constraints` heading (same robustness as the metadata block).
- **False positives / over-strict** — start with `forbid`/`allowed-only-via` only; clear
  violation messages naming the ADR and edge so it's actionable.
- **Scope creep toward a policy engine** — explicitly bounded to dependency-shaped rules in v1.

## Open Questions

1. Constraint block format — fenced ```yaml under `## Constraints` (lean) vs a dedicated
   `constraints:` key in a sidecar. (Lean: in-ADR fenced block.)
2. Should a `forbid-cycle` (acyclic within a scope) be in v1 or deferred?
3. Cross-partition selectors — confirm `system` selector semantics for "no cross-system dep
   except via X".
4. Warn vs error for constraints from a `proposed` ADR (preview), or ignore entirely (v1: ignore).

## Migration

Additive. ADRs without a `## Constraints` section are unchanged. Existing `sda check` behavior is
unchanged; constraint checks only fire when constraints are declared.
