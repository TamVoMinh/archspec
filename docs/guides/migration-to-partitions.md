# Migrating to Partitioned Architecture

This guide walks you through converting a flat SDA project to a multi-partition layout.

---

## When to Partition

Partition when your architecture hub covers **multiple systems** that are distinct enough to warrant separate service models, ADRs, and index files. Common triggers:

- Two or more product lines in the same repo
- Independent teams owning separate subsystems
- You want system-scoped dashboards or CI checks

If you only have one system, stay flat — it's simpler.

---

## Before You Start

1. Ensure `sda check` passes on the current flat layout
2. Run `sda index` to have a fresh baseline
3. Commit all pending changes — the migration involves moving files

---

## Step 1 — Create Partition Directories

Create a directory for each system under `architecture/`. Each must contain at least `model/` or `adr/`:

```bash
mkdir -p architecture/payments/{model,adr}
mkdir -p architecture/catalog/model
```

The partition name is the directory name. Choose names that match your systems (e.g., product names, team boundaries, domain names).

---

## Step 2 — Move Service Models

Move each system's services from the flat `model/` to its partition:

```bash
# If you had architecture/model/services.yaml with all services
# Split it into per-partition files:
mv architecture/model/services.yaml architecture/payments/model/services.yaml

# Create a new one for the other partition:
cat > architecture/catalog/model/services.yaml << 'EOF'
services:
  catalog-api:
    type: api
    last_reviewed: 2026-01-15
EOF
```

Remove the root `architecture/model/` directory once all services are moved — `sda check` will ignore it in partitioned mode.

---

## Step 3 — Move ADRs

Move system-specific ADRs to their partition:

```bash
mv architecture/adr/003-payments-specific.md architecture/payments/adr/
```

Keep cross-system ADRs in the root `architecture/adr/` — they'll appear in the master index only.

---

## Step 4 — Add `system:` to Problems

Tag each inbox problem with the partition it belongs to:

```yaml
# architecture/inbox/PROB-001.yaml
id: PROB-001
title: Auth latency spike
system: payments    # ← add this
```

New problems can use `--system`:

```bash
sda capture "New issue" --system payments --source slack
```

Problems without a `system:` field will appear in the master index as "unrouted" and `sda check` will warn about them.

---

## Step 5 — Regenerate and Verify

```bash
sda index     # generates per-partition + master indexes
sda check     # validates per-partition services, ADRs, and system: fields
sda status    # shows the partitioned overview
```

Expected output from `sda status`:

```
       ArchSpec Status (partitioned)
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ Partition  ┃ Problems ┃ ADRs ┃ Services ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
│ catalog        │        1 │    0 │        1 │
│ payments │        2 │    1 │        3 │
│ (root)     │        0 │    1 │        — │
└────────────┴──────────┴──────┴──────────┘

Systems: 2 (catalog, payments)  Total problems: 3
```

---

## How Partition Detection Works

SDA auto-discovers partitions by scanning direct children of `architecture/`:

- A directory containing `model/` or `adr/` → partition
- Reserved names (`inbox`, `model`, `adr`) → never a partition
- Files → ignored

No configuration needed. Add or remove a partition by creating or deleting the directory.
