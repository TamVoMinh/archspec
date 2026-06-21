# Classification — Labeling & Categorizing Architecture

ArchSpec stays methodology-neutral at its core. To divide and conquer at scale — hundreds of
services, problems, and decisions — you **classify** artifacts along named **dimensions**.
Methodologies (DDD, C4, …) are second-class **packs** that supply vocabularies and rules on top;
the core only knows dimensions and values.

## Labels

Any architecture entity — a problem, a service, an ADR, or a partition/system — can carry a
`labels` map of `dimension → value`:

```yaml
# services.yaml
billing:
  type: api
  labels: { area: payments, criticality: core }
```

```yaml
# a problem
labels: { area: payments }
```

```markdown
<!-- an ADR's ## Metadata block -->
- labels: area=payments, criticality=core
```

```yaml
# architecture/<partition>/partition.yaml  — labels a boundary/system
labels: { criticality: core }
```

`labels` is always optional, and `tags` remains a free-form, unvalidated escape hatch.

## Dimensions

Dimensions and their controlled vocabularies are declared in `architecture/classification.yaml`.
The core ships neutral defaults:

| Dimension | Default | Meaning |
|---|---|---|
| `area` | open (any value) | which part of the system |
| `criticality` | open (any value) | how much it matters |
| `lifecycle` | `active` / `deprecated` / `retired` | maturity / state |

Close a vocabulary to have it validated:

```yaml
# architecture/classification.yaml
dimensions:
  criticality:
    values: [core, supporting, generic]   # now validated by `sda check`
  team:
    values: ~                             # a project-defined open dimension
```

## Validation

`sda check` validates label values against the vocabulary:

- value outside a **closed** dimension's `values` → **error** (fails `--strict`)
- a dimension declared **without** `values` (open) → any value accepted
- a label using a dimension **not declared** at all → **warning**
- `tags` are never validated

Structural shape (`labels` is a string→string map) is checked by the YAML schema; the
value-against-vocabulary check is config-driven and lives in `sda check`.

## Using classification

- **Query**: labels are written into `architecture/index.yaml`, so `yq` can filter by them.
- **Navigate**: the viewer's Explorer can **group by any dimension** (Area, Criticality, …),
  not just structural axes — with an "Unlabeled" bucket for entities missing a value.
- **AI**: labels travel with the model export, so agents get classification context.

## Methodologies as packs (second class)

A methodology pack is just configuration: it supplies vocabularies (and, later, relationship
types and fitness-function checks) without changing the core schema. For example, a **DDD pack**
sets `criticality: {core, supporting, generic}` (subdomain classification) — so a *bounded
context* is simply a partition/system labeled with a `criticality`. The core never learns the
word "subdomain"; it just validates the values.
