# Getting Started

Set up ArchSpec in an existing repository in under 10 minutes.

---

## Prerequisites

- Python 3.11+
- Git repository

---

## 1. Install the CLI

```bash
pip install sda-cli
```

---

## 2. Scaffold the project

Run this from the root of your target repository:

```bash
sda init
```

This creates:

```
architecture/
  inbox/              ← PROB-TEMPLATE.yaml (blank problem template)
  adr/                ← TEMPLATE.md (blank ADR template)
  model/
    services.yaml     ← empty service model
  index.yaml          ← empty knowledge graph (auto-generated)
OWNERS.yaml           ← governance config (fill in your team)
.github/
  workflows/
    sda-checks.yml    ← CI checks
```

---

## 3. Fill in OWNERS.yaml

Open `OWNERS.yaml` and add your team details:

```yaml
roles:
  architecture_lead:
    name: Your Name
    email: you@company.com
    triage_sla_hours: 48
```

And add your services to `domain_ownership`:

```yaml
domain_ownership:
  api-gateway: you@company.com
```

---

## 4. Add your services

Open `architecture/model/services.yaml` and list your system's services:

```yaml
services:
  api-gateway:
    type: api
    depends_on: [auth, billing]
    owner: you@company.com
    last_reviewed: 2026-04-06

  billing:
    depends_on: [database]
    owner: you@company.com
    last_reviewed: 2026-04-06
```

---

## 5. Capture your first problem

```bash
sda capture "API latency spike on checkout" --source slack --type performance
```

This creates `architecture/inbox/PROB-001.yaml`. Open it and fill in the `services` and `symptoms` fields.

---

## 6. Run checks

```bash
sda check
```

If there are no errors, your ArchSpec setup is working. Commit everything and open a PR.

---

## 7. Enable CI

The `sda init` scaffolded `.github/workflows/sda-checks.yml`. Enable it by committing it to your repo. On every push, CI will run:

- `sda check --strict` — block on any ADR or ownership errors
- `yamale` schema validation on all YAML files
- `sda index --validate` — warn if the knowledge graph is stale

---

## Next Steps

- [Your First ADR](first-adr.md) — create and accept your first architecture decision
- [Knowledge Graph](../concepts/knowledge-graph.md) — querying your architecture
- [Governance](../concepts/governance.md) — ownership model and PR review requirements
