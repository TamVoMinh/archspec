## Why

SDA's first-class job is to make architectural problems and decisions traceable, queryable,
verifiable, and AI-legible — methodology-neutral. As teams scale they need to **classify and
categorize** problems and artifacts to divide and conquer (by area, importance, maturity). The
risk is baking one methodology's ontology (DDD bounded contexts, C4 layers) into the core,
which turns SDA into a DDD/C4 tool and forces everyone to conform.

The fix is a clean split: the **core** provides a thin, methodology-neutral **classification**
capability (label artifacts and problems along named dimensions with controlled vocabularies);
**methodologies plug in** as second-class packs that merely supply vocabularies, relationship
types, and checks. This change captures the first-class core piece.

## What Changes

- Add a `labels` map (dimension → value) to **problems and artifacts** (services/components).
- Add **configurable classification dimensions** with controlled vocabularies in config. The
  core ships neutral defaults — `area`, `criticality`, `lifecycle` — and `tags` remains the
  unstructured escape hatch. The core never hardcodes methodology-specific vocabularies.
- **`sda check`** validates label values against the declared vocabulary.
- The **index** carries labels so they're queryable; the viewer can **group by any dimension**;
  **AI export** includes labels so agents get classification context.
- Methodologies (DDD, C4, Team Topologies) become **second-class packs** that supply
  vocabularies (+ later, relationship types and fitness functions). DDD's "bounded context" is
  just a `system` boundary labeled with a `criticality` value interpreted by the DDD pack — no
  DDD types in the core. The pack format is a separate, later change; this change only makes the
  core plugin-ready.

## Capabilities

### New Capabilities
- `artifact-classification`: a methodology-neutral labeling system — problems and artifacts
  carry values along configurable, validated classification dimensions, consumed by check,
  index, the viewer, and AI export.

### Modified Capabilities
<!-- Consumed by existing capabilities (yaml-schema-validation, knowledge-graph-index,
staleness-detection/check, and the viewer's panel-plugins); those gain awareness of labels but
their core requirements are unchanged. Reconciled at archive time. -->

## Impact

- **Schemas**: `problem.schema.yaml` and `service.schema.yaml` gain an optional `labels` map;
  config gains a `classification.dimensions` block.
- **CLI**: `sda check` validates labels; `sda index` includes labels on nodes.
- **Viewer**: Explorer "Group by" generalizes to any dimension (the `model-tree-explorer`
  groupings become data-driven rather than hardcoded).
- **AI export**: labels travel with the model/documents.
- **Backward compatible**: `labels` is optional and additive; projects without it are unchanged.
- **Enables**: a future `methodology-packs` change (DDD pack first) with zero core schema change.
