## Context

SDA's objective purpose is to make problems and decisions first-class: traceable, queryable,
verifiable in CI, and legible to humans and AI. It must stay methodology-neutral so it isn't a
DDD-only or C4-only tool. Teams still need to classify problems and artifacts to divide and
conquer. This change adds that classification to the core as a neutral substrate, and defines
the seam through which methodologies (DDD etc.) plug in as second-class packs.

## Goals / Non-Goals

**Goals**
- A thin, methodology-neutral way to classify problems and artifacts along named dimensions.
- Classification is verifiable (`sda check`), queryable (index), navigable (viewer group-by),
  and carried into AI export.
- Make the core plugin-ready so methodologies add vocabulary/rules without core schema change.

**Non-Goals**
- No methodology-specific node types or relationship semantics in the core (DDD bounded-context,
  C4 container, context-map patterns all live in packs).
- No tactical modeling (aggregates/entities).
- Not a wide-open EAV/property bag — a few well-known dimensions, not arbitrary structure.

## Decisions

### Decision 1: Labels along named dimensions (not free tags, not full EAV)
**Choice:** Artifacts and problems carry a `labels` map of `dimension → value`. Dimensions are a
small, named, controlled set; `tags` stays as the unstructured escape hatch.
**Rationale:** Free tags can't be validated, grouped, or reasoned about; full EAV loses
first-class semantics. Named dimensions give structure the core can verify and tools can group by.

### Decision 2: Controlled vocabularies in config; neutral defaults
**Choice:** Config declares each dimension's allowed values. The core ships neutral defaults —
`area`, `criticality`, `lifecycle` — overridable per project. A dimension with no declared
`values` is open (any value allowed).
**Rationale:** Validation needs a vocabulary; neutral defaults avoid methodology lock-in;
open dimensions allow gradual adoption.

### Decision 3: Classify problems too, not just artifacts
**Choice:** `labels` applies to problems and artifacts alike.
**Rationale:** "Divide and conquer the problem" means classifying problems (by area, criticality)
as much as components — e.g. "all core-area security problems."

### Decision 4: Boundaries stay structural; classification is orthogonal
**Choice:** Boundaries remain the existing `system`/partition (containment); classification is
orthogonal `labels`. A DDD "bounded context" = a `system` + a `criticality` label, interpreted
by the DDD pack — not a new core node type.
**Rationale:** Keeps structure (core) and meaning (methodology) cleanly separated.

### Decision 5: Methodologies are second-class packs (separate, later)
**Choice:** A pack supplies vocabularies (+ later relationship types and fitness functions) as
config. DDD is the first pack. This change only makes the core plugin-ready; the pack format and
DDD pack are a follow-up change.
**Rationale:** Honors the first-class-core / second-class-methodology split; avoids scope creep.

## Risks / Trade-offs

- **Vocabulary drift / over-classification**: too many dimensions/values becomes noise — ship a
  minimal default set and let teams extend deliberately.
- **Validation severity**: out-of-vocabulary value on a closed dimension should be an error
  (verifiable), unknown/open dimensions a warning — needs to be tuned to not block adoption.
- **Viewer coupling**: `model-tree-explorer` groupings should become data-driven over dimensions
  rather than hardcoded `system/type/group`; reconciled when both land.

## Open Questions

1. **User-defined dimensions** — allow projects to declare brand-new dimensions beyond the
   defaults, or fix the set + `tags`? (Lean: allow declaring new dimensions in config.)
2. **Single vs multi-value** — can an artifact have multiple values on one dimension (e.g. two
   areas)? (Lean: single value per dimension for v1; `tags` for many-to-many.)
3. **Validation severity** — closed-vocab violation = error; open-dimension value = allowed;
   unknown dimension = warning? Confirm.
4. **Config location** — reuse `openspec/config.yaml`, or a dedicated `architecture` config?
5. **Pack format** (deferred to the methodology-packs change) — how a pack merges vocabularies,
   relationship types, and checks.

## Migration

Additive and backward compatible. `labels` is optional; projects adopt dimensions gradually.
The future `methodology-packs` change (DDD pack first) builds on this with no core schema change.

## Archive order & reconciliation

- At archive, the delta touches existing main specs additively: `inbox-schema` and
  `yaml-schema-validation` (the `labels` field), `knowledge-graph-index` (labels on nodes),
  `adr-template` (the `- labels:` metadata line), and the check/staleness capability (the new
  label validation). These merge in cleanly — no contradictions.
- Archive **before `methodology-packs`** — that change depends on this one (packs supply
  vocabularies/rules over these dimensions).
- The viewer's Explorer group-by is data-driven over these dimensions; coordinate the wording
  with `model-tree-explorer` at archive.
