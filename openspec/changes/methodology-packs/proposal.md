## Why

`artifact-classification` makes the core a methodology-neutral substrate: entities carry
`labels` along configurable dimensions. The second-class layer — letting a methodology like DDD
plug in its vocabulary, relationship semantics, and checks **without any core schema change** —
is not yet built. This change captures that pack mechanism. **(Stub — to be fleshed out.)**

## What Changes

- Define a **methodology pack** format: configuration that supplies
  - **dimension vocabularies** (e.g. DDD `criticality: {core, supporting, generic}`),
  - **relationship types** (e.g. DDD context-map patterns: ACL, OHS, conformist, shared-kernel,
    customer–supplier, partnership, separate-ways) layered on `depends_on`/context edges,
  - **fitness-function checks** for `sda check` (e.g. "a component may cross a boundary only via
    the declared relationship").
- Ship a **DDD pack** as the first pack (bounded context = a partition + a `criticality` label;
  typed context-map seams), proving the mechanism.
- Optionally a **C4** and **Team Topologies** pack later.

## Capabilities

### New Capabilities
- `methodology-packs`: a pack format and loader that merges methodology vocabularies,
  relationship types, and checks over the neutral core — no core schema change.

## Impact

- Builds entirely on `artifact-classification` (labels/dimensions) and the existing
  relationship model; the core stays first-class and unchanged.
- Out of scope here; this is a placeholder to be expanded into design/specs/tasks when picked up.
