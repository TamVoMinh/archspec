# Governance — Ownership and Decision Authority

Architecture systems rot silently when nobody is accountable. ArchSpec makes ownership explicit and enforces it through Git-native tooling.

---

## OWNERS.yaml

`OWNERS.yaml` at the repository root is the authoritative governance document. It defines:

- Who is the **architecture lead** (and their deputy)
- Who owns each **service domain**
- What **SLAs** apply to triage and review
- The **PR review requirement matrix**
- The **conflict resolution policy**

```yaml
roles:
  architecture_lead:
    name: Tam
    email: tam@company.com
    triage_sla_hours: 48

  contributors:
    - name: Saber
      email: saber@company.com
      domain: billing
    - name: Valentin
      email: valentin@company.com
      domain: api-gateway

triage_policy:
  inbox_sla_hours: 48
  adr_review_required_approvers: 2
  adr_acceptance_requires: architecture_lead

domain_ownership:
  billing: saber@company.com
  api-gateway: valentin@company.com
```

---

## CODEOWNERS

`.github/CODEOWNERS` translates `OWNERS.yaml` into PR enforcement:

```
architecture/model/     @arch-lead
schemas/                @arch-lead
architecture/adr/       @arch-lead
```

GitHub automatically requests the right reviewers on every PR.

---

## PR Review Requirements

| Change type | Required approvers |
|---|---|
| New inbox problem | 1 (any contributor) |
| New ADR (`proposed`) | 1 (domain owner) |
| ADR acceptance | 2 (domain owner + arch lead) |
| `services.yaml` change | arch lead |
| `schemas/` change | arch lead |

---

## ADR RFC Label Process

Every ADR PR carries a label that tracks its position in the acceptance lifecycle:

```
adr/proposed  (open, 5 business days minimum)
      ↓
adr/accepted  (2 approvals including arch lead)
      or
adr/contested (conflicting views — arch lead required)
      or
adr/rejected  (closed with rationale in PR)
```

Create these labels in your GitHub repository settings.

---

## Conflict Resolution

> If two contributors submit conflicting ADRs on the same service within 7 calendar days, the architecture lead schedules a joint resolution session within 3 business days.

The resolution is recorded as a **new ADR** that supersedes both conflicting ones. Both originals are updated to `status: superseded` with `superseded_by` pointing to the resolution ADR.

This rule is documented in `OWNERS.yaml` under `governance.conflict_resolution`.

---

## What `sda check` Enforces

- `OWNERS.yaml` has required sections (roles, triage_policy)
- Architecture lead name/email are not placeholders
- All services in `services.yaml` have a `domain_ownership` entry
- Draft problems respect the triage SLA
- Services are reviewed within 180 days
