## Why

The Architecture Operating System (AOS) design has strong principles but seven concrete gaps that prevent it from being trustworthy at scale: an underspecified knowledge graph, no YAML schema enforcement, no ADR lifecycle, no ownership model, high-friction input capture, no staleness detection, and no multi-architect governance. Without closing these gaps, the system will silently rot within months of adoption.

## What Changes

- Add `status` field and state machine to the ADR template and enforce it in CI
- Define YAML schemas for inbox problems and the service model, with CI validation
- Introduce `OWNERS.yaml` and `CODEOWNERS` to name accountable owners for every architecture artifact
- Build a file-based knowledge graph generator (`aos-index.py`) that auto-produces `architecture/index.yaml` from existing YAML and ADRs
- Add `last_reviewed` fields to `services.yaml` entries and a CI staleness check script
- Define a tiered input capture workflow with `status: draft` support to reduce friction
- Establish an ADR RFC process using Git PR labels and a documented conflict resolution policy

## Capabilities

### New Capabilities

- `adr-lifecycle`: ADR status state machine (`proposed → accepted → superseded | deprecated`) with CI enforcement rules
- `yaml-schema-validation`: YAML schemas for inbox problems and service model entries, enforced in CI via `yamale`
- `ownership-model`: `OWNERS.yaml` defining roles, triage SLAs, and domain owners; `CODEOWNERS` enforcing PR review requirements
- `knowledge-graph-index`: Python script that generates a flat `architecture/index.yaml` knowledge graph from existing inbox YAML and ADR frontmatter; queryable via `yq`
- `staleness-detection`: `last_reviewed` field on service entries and `scripts/check-staleness.py` CI warning script
- `input-capture-workflow`: Draft status support for inbox entries, `aos capture` CLI command, and per-source capture guidelines (Slack, Jira, meetings)
- `multi-architect-governance`: Git PR label lifecycle (`adr/proposed → adr/accepted | adr/rejected | adr/contested`) and conflict resolution policy documented in `OWNERS.yaml`

### Modified Capabilities

- `adr-template`: Existing ADR format gains required `status`, `date`, and `superseded_by` fields in a `## Metadata` block
- `inbox-schema`: Existing inbox YAML gains optional `status: draft | active | resolved` field for triage workflow

## Impact

- `architecture/` folder structure: gains `index.yaml` (auto-generated), `schemas/` directory
- `scripts/` folder: gains `aos-index.py` and `check-staleness.py`
- All existing ADR files: require backfilling of `status` field
- All existing `services.yaml` entries: require backfilling of `last_reviewed` and `owner` fields
- CI pipeline: gains YAML schema validation step and staleness warning step
- Git repository root: gains `OWNERS.yaml` and updates to `.github/CODEOWNERS`
- No external service dependencies introduced (all tooling is file-based + Python)
