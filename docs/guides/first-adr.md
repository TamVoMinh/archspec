# Your First ADR

This guide walks through creating, reviewing, and accepting an Architecture Decision Record from start to finish.

---

## Scenario

You've been investigating PROB-001 (API latency spike). You've decided to introduce a Redis caching layer. Here's how to record that decision.

---

## Step 1 — Create the ADR file

```bash
cp architecture/adr/TEMPLATE.md architecture/adr/ADR-001-introduce-caching.md
```

---

## Step 2 — Fill in all sections

```md
# ADR-001: Introduce Redis Caching Layer

## Metadata
- status: proposed
- date: 2026-04-06
- superseded_by: ~
- links: [PROB-001]

## Context
PROB-001 identified p95 API latency exceeding 2s on the billing service
under normal load. Database read throughput is the bottleneck. Vertical
DB scaling is ruled out due to cost constraints.

## Decision
Introduce Redis as a read-through cache at the API gateway layer for
billing queries that do not require real-time data.

## Alternatives
**Optimize DB queries**: partial improvement (~20%), does not address peak load
**Scale DB vertically**: rejected — cost constraint per PROB-001
**Add read replicas**: viable long-term, but 6-week lead time; defer

## Consequences
+ Estimated p95 latency reduction: ~60%
+ No DB schema changes required
- Cache invalidation complexity on billing data writes
- New operational dependency: Redis cluster

## Affected Services
- api-gateway
- billing
```

---

## Step 3 — Open a PR with label `adr/proposed`

```bash
git checkout -b adr/introduce-caching
git add architecture/adr/ADR-001-introduce-caching.md
git commit -m "adr: introduce Redis caching layer (proposed)"
git push
# Open PR → add label: adr/proposed
```

CI automatically runs `sda check` and validates the ADR format.

---

## Step 4 — Review period (minimum 5 business days)

During this time:
- The domain owner (billing) reviews the technical approach
- Other contributors may comment
- If there's a competing approach, the PR gets labelled `adr/contested`

---

## Step 5 — Accept the ADR

After 2 approvals (domain owner + architecture lead):

1. Update the ADR file:
   ```md
   - status: accepted
   ```
2. Update the PR label to `adr/accepted`
3. Merge

---

## Step 6 — Update the knowledge graph

```bash
sda index
git add architecture/index.yaml
git commit -m "index: regenerate after ADR-001 acceptance"
```

---

## Step 7 — Mark the problem resolved

Update `architecture/inbox/PROB-001.yaml`:

```yaml
status: resolved
```

---

## Verify

```bash
sda status
# Problems: 1 total  0 active  0 draft  1 resolved
# ADRs:     1 total  1 accepted  0 proposed

sda check
# ✓ All checks passed
```
