# Multi-Team Setup

ArchSpec scales from a single architect to a team of architects with minimal additional structure. Here's how to configure it for a team.

---

## When to Use This Guide

- You have 2+ architects contributing ADRs
- You have multiple service domains with different owners
- You need clear escalation paths for conflicting decisions

---

## Step 1 — Define domain ownership

Map every service to an owner in `OWNERS.yaml`:

```yaml
roles:
  architecture_lead:
    name: Jane Smith
    email: jane@company.com
    triage_sla_hours: 48
    deputy: alex@company.com    # ← set a deputy for continuity

  contributors:
    - name: Alex Kim
      email: alex@company.com
      domain: billing
    - name: Sam Lee
      email: sam@company.com
      domain: api-gateway
    - name: Jordan Park
      email: jordan@company.com
      domain: auth

domain_ownership:
  billing: alex@company.com
  api-gateway: sam@company.com
  auth: jordan@company.com
  database: jane@company.com
```

---

## Step 2 — Configure CODEOWNERS

Map each domain's ADR path to its owner:

```
architecture/adr/          @jane-smith        # arch lead reviews all ADRs
architecture/adr/*billing* @alex-kim          # billing domain owner
architecture/adr/*gateway* @sam-lee           # api-gateway domain owner
architecture/adr/*auth*    @jordan-park       # auth domain owner
architecture/model/        @jane-smith        # arch lead for service model changes
schemas/                   @jane-smith        # arch lead for schema changes
OWNERS.yaml                @jane-smith
```

---

## Step 3 — Create GitHub PR labels

In repository Settings → Labels, create:

| Label | Colour | Meaning |
|---|---|---|
| `adr/proposed` | `#0075ca` | Open for comment |
| `adr/accepted` | `#0e8a16` | Approved and merged |
| `adr/rejected` | `#e4e669` | Closed with rationale |
| `adr/contested` | `#d93f0b` | Conflicting views — arch lead required |

---

## Step 4 — Configure branch protection

In repository Settings → Branches, for your default branch:

- Require PR before merging
- Require approvals: **2**
- Require review from Code Owners: **enabled**
- Restrict who can push: architecture lead only (for `architecture/model/` and `schemas/`)

---

## Step 5 — Document the conflict resolution policy

`OWNERS.yaml` already contains the default policy under `governance.conflict_resolution`. Adjust it to match your team's norms:

```yaml
governance:
  conflict_resolution: |
    If two contributors submit conflicting ADRs on the same service within 7 days,
    the architecture lead schedules a joint session within 3 business days.
    The session outcome is a new ADR that supersedes both.
```

---

## Operating Rhythm

| Cadence | Activity |
|---|---|
| Daily | Triage draft inbox problems (48h SLA) |
| Weekly | Review `sda status` output, check for stale services |
| Per PR | `sda check --strict` runs in CI automatically |
| Monthly | Run `sda index`, review knowledge graph for patterns |
| Quarterly | Review `last_reviewed` dates on all services |

---

## Scaling Beyond 5 Architects

At this scale, consider:

- Sub-teams with their own `OWNERS.yaml` per service cluster
- Monthly architecture review sessions where contested ADRs are resolved
- A rolling "architecture lead" rotation to distribute triage load
- `sda status` output posted automatically to a `#arch-health` channel weekly
