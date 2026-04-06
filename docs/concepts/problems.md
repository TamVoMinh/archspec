# Problems — Architecture Inbox

Architecture inputs arrive from everywhere: Slack threads, Jira tickets, meetings, personal notes. Without a capture discipline, they vanish.

The **inbox** is the first layer of ArchSpec — a structured place where all architecture-relevant problems are normalised into a queryable format before any decision is made.

---

## Rule

> No decision without an inbox entry.

Every ADR must link to at least one `PROB-*.yaml` file. This enforces traceability: you can always trace a decision back to the problem that motivated it.

---

## Problem File Format

```yaml
id: PROB-001
title: API latency spike on billing service
source: slack           # slack | jira | github | meeting | email | adhoc
type: performance       # performance | security | reliability | cost | ux | compliance | other
created_at: 2026-04-01
status: active          # draft | active | resolved

services:
  - api-gateway
  - billing

symptoms:
  - p95 latency > 2s
  - timeout errors on checkout

constraints:
  - cannot scale DB vertically

tags:
  - urgent
  - production
```

---

## Problem Lifecycle

```
draft   →  active   →  resolved
```

- **draft** — captured but not yet triaged. Services and symptoms may be empty.
- **active** — triaged, fully described, being investigated.
- **resolved** — an ADR has addressed the problem (link the ADR via `links:` in the ADR file).

---

## Capturing Problems

```bash
# Fastest path — scaffolds a draft immediately
sda capture "API latency spike" --source slack --type performance

# From Jira/GitHub — configure a webhook to call this automatically
sda capture "Issue title from Jira" --source jira

# Template if you prefer manual editing
cp architecture/inbox/PROB-TEMPLATE.yaml architecture/inbox/PROB-002.yaml
```

---

## Triage SLA

Draft problems must be triaged within the SLA defined in `OWNERS.yaml` (default: 48 hours). `sda check` will flag overdue drafts.

During triage:
1. Fill in `services` and `symptoms`
2. Change `status` to `active`
3. Open a PR — 1 reviewer required (any contributor)
