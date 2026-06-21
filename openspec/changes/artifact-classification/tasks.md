## 1. Schema & config

- [x] 1.1 Add an optional `labels` map (dimension → value) to `schemas/problem.schema.yaml` and `schemas/service.schema.yaml` (structural only — `map(str())`)
- [x] 1.2 Boundary/partition labels via `architecture/<partition>/partition.yaml`; ADR labels via the `## Metadata` `- labels:` line. (Flat project-level labels deferred — a flat project is a single implicit context; label its components.)
- [x] 1.3 Define the `classification.dimensions` config block: default dimension **names** `area`/`criticality`/`lifecycle`; `area`+`criticality` open by default, `lifecycle` neutral vocab; projects may add dimensions / close vocabularies
- [x] 1.4 Decide config location (reuse `openspec/config.yaml` vs a dedicated architecture config) — open question 4
- [x] 1.5 Update scaffold templates (`services.yaml`, `PROB-TEMPLATE.yaml`, partition metadata) to show `labels`; keep `tags` as the free-form escape hatch

## 2. Classification core (Python)

- [x] 2.1 Load classification config + defaults; expose the active dimensions/vocabularies
- [x] 2.2 Read `labels` off problems, services, ADRs (graph nodes) and partitions (master-index manifest entries); all validated by sda check
- [x] 2.4 Reconcile labels with existing first-class fields (problem type/source/status, service type/deprecated, ADR lifecycle): no shadowing; derive overlapping views rather than duplicate
- [x] 2.3 Resolve open questions: single vs multi-value per dimension (lean single); allow user-defined dimensions (lean yes)

## 3. Validation (`sda check`)

- [x] 3.1 `validate_labels`: closed-vocab value not in `values` → error; open dimension → any value; `tags` never validated
- [x] 3.2 Wire into flat + partitioned check lists
- [x] 3.3 Tests: valid labels pass; out-of-vocab → error (+ `--strict` exit 1); open dimension accepts any; missing labels valid

## 4. Surfacing (index, viewer, AI)

- [x] 4.1 Include labels on index nodes (queryable via `yq`)
- [x] 4.2 Make the viewer Explorer group-by data-driven over classification dimensions (reconcile with `model-tree-explorer`'s hardcoded system/type/group)
- [x] 4.3 Include labels in the AI/view export so agents receive classification context

## 5. Docs, tests & verification

- [x] 5.1 Tests: schema accepts labels; index carries labels; check validation matrix
- [x] 5.2 Docs: `docs/concepts/problems.md` + a classification concept doc; readme note
- [x] 5.3 Verify end-to-end on `example/`: label flows to index + check validates; viewer group-by is data-driven over dimensions
- [x] 5.4 Confirm backward compatibility: projects without `labels` unchanged

## 6. Follow-up (separate change)

- [x] 6.1 Stub the future `methodology-packs` change (DDD pack first): pack format supplying vocabularies + relationship types + fitness functions, with no core schema change
