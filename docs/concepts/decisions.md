# Decisions — Architecture Decision Records

An ADR (Architecture Decision Record) is the core output of ArchSpec. It captures **what was decided, why, and what the consequences are** — permanently and traceably.

---

## Format

Every ADR file (`architecture/adr/ADR-XXX-name.md`) must contain:

```md
# ADR-012: Introduce Caching Layer

## Metadata
- status: accepted
- date: 2026-04-06
- superseded_by: ~
- links: [PROB-001, PROB-003]
- labels: area=payments, criticality=core   # optional — classification (see Classification doc)

## Context
What situation led to this decision? Reference problem IDs.

## Decision
State the decision clearly and directly.

## Alternatives
**Option A**: description — **Rejected because**: reason
**Option B**: description — **Rejected because**: reason

## Consequences
+ Positive outcome
- Trade-off or risk

## Affected Services
- api-gateway
- billing
```

---

## Status Lifecycle

```
proposed  →  accepted  →  superseded
                       →  deprecated
          →  rejected
```

| Status | Meaning |
|---|---|
| `proposed` | Open for review — minimum 5 business days |
| `accepted` | 2 approvals received, including architecture lead |
| `rejected` | Closed — rationale recorded in PR |
| `superseded` | Replaced by a newer ADR — `superseded_by` must be set |
| `deprecated` | No longer applies — service or system removed |

---

## Rules

- Every ADR **must** link to at least one `PROB-*` problem via the `links:` field
- Every ADR **must** list its affected services
- `superseded` ADRs **must** set `superseded_by: ADR-XXX`
- `accepted` ADRs **must not** reference `deprecated: true` services

`sda check` enforces all of these rules automatically.

---

## PR Label Lifecycle

Use Git PR labels to track ADR progression through review:

| Label | Meaning |
|---|---|
| `adr/proposed` | Open for comment |
| `adr/contested` | Conflicting views — arch lead required |
| `adr/accepted` | Approved and merged |
| `adr/rejected` | Closed with recorded rationale |

---

## Creating an ADR

```bash
# Copy the template
cp architecture/adr/TEMPLATE.md architecture/adr/ADR-012-caching-layer.md

# Edit it — fill in all sections
# Open a PR with label: adr/proposed
```

See [Your First ADR](../guides/first-adr.md) for a full walkthrough.
