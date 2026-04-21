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
system: payments     # optional — target partition name

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

### The `system:` Field

When a project uses **partitioned architecture** (multiple systems in one repository), the `system:` field routes problems to the correct partition.

- The value must match a partition directory name under `architecture/` (e.g., `payments`, `catalog`).
- Problems with a valid `system:` appear in both the partition index and the master index.
- Problems without `system:` (or with a value that doesn't match any partition) appear in the master index only and are flagged as "unrouted" by `sda check`.
- In flat-mode projects (no partitions), the field is ignored and optional.

Use `--system` on `sda capture` to set it at creation time:

```bash
sda capture "Auth issue" --system payments --source slack
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

## File Layouts

Problems support two layouts — flat files and folders. Both are discovered automatically.

### Flat layout (default)

```
architecture/inbox/
  PROB-001.yaml
  PROB-002.yaml
```

### Folder layout (when attachments exist)

```
architecture/inbox/
  PROB-003/
    PROB-003.yaml
    attachments/
      original-email.msg
      screenshot.png
```

Use `--attach` on `sda capture` to create the folder layout automatically. You can also create it manually — place the YAML file inside a folder named after the problem ID.

> **Migration note:** Existing flat layouts continue to work unchanged. Folder layout is opt-in. You can mix both in the same inbox. However, having the same PROB-ID in both layouts is an error.

---

## Capturing Problems

```bash
# Fastest path — scaffolds a draft immediately
sda capture "API latency spike" --source slack --type performance

# Target a specific system/partition
sda capture "Auth issue" --system payments --source slack

# With attachments — automatically creates folder layout
sda capture "Ping test retirement" --source email --attach ~/notification.msg

# Multiple attachments
sda capture "EIT cable issue" --source meeting --attach report.pdf --attach photo.jpg

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
