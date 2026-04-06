<p align="center">
  <strong>ArchSpec</strong><br>
  <em>The lightweight framework for Spec-Driven Architecture (SDA).</em>
</p>

<p align="center">
  <a href="https://github.com/TamVoMinh/archspec/actions"><img alt="CI" src="https://github.com/TamVoMinh/archspec/actions/workflows/sda-checks.yml/badge.svg" /></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11+-blue?style=flat-square" />
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green?style=flat-square" />
</p>

---

You practice TDD so tests drive your code.
**Spec-Driven Architecture (SDA) means decision specs drive your system.**

Every engineering change has a problem behind it. Every problem has a decision that addresses it. Every decision has consequences that shape your system. SDA makes that chain explicit, traceable, and enforceable — for every type of architect.

ArchSpec is the CLI tool that makes SDA stick.

```
→ no decision without a problem — traceability is enforced
→ no implementation without a decision spec — ADRs precede engineering
→ Git is the database — no servers, no dashboards, no extra tools
→ Markdown + YAML — readable by humans and AI alike
→ one architect or a team — same discipline, same system
```

> [!TIP]
> **New to ArchSpec?** Run `sda init` in any repo, then follow [Getting Started](docs/guides/getting-started.md). You'll have your first problem captured and ADR open in under 10 minutes.

---

## See it in action

```text
$ sda capture "checkout times out under load" --source slack --type performance
╭─────────────────────────── PROB-001 ───────────────────────────╮
│ Created: architecture/inbox/PROB-001.yaml                      │
│ Next: fill in services and symptoms, set status → active       │
╰────────────────────────────────────────────────────────────────╯

$ sda check
✓ No errors   2 warning(s)
  ⚠ PROB-001 is draft — triage within 48h (SLA: 48h)
  ⚠ billing service not reviewed in 180+ days

$ # write ADR-001-caching.md → open PR with label: adr/proposed

$ sda index
Generated architecture/index.yaml
3 nodes — PROB-001 → ADR-001 → [api-gateway, billing]

$ sda status
╭──────────────────── ArchSpec Status ───────────────────────╮
│  Problems   1 total   1 active   0 draft                    │
│  ADRs       1 total   1 accepted   0 proposed               │
│  Services   4 total   none stale                            │
│  Index      fresh (today)                                   │
╰────────────────────────────────────────────────────────────╯
```

---

## Why this exists

Architecture work generates constant signal — Slack threads, incident retros, Jira tickets, hallway conversations. Without a **capture discipline**, that signal evaporates. Without an **ADR practice**, decisions become tribal knowledge. Without a **knowledge graph**, nobody can answer *"what services are affected by this change?"*

ArchSpec gives you one Git-native place where all three live together, enforce each other, and stay queryable — for technical architects, solution architects, product architects, and software architects alike.

<details>
<summary><strong>How it compares</strong></summary>

**vs. a wiki** — Write-once, never queried, no lifecycle enforcement. ArchSpec files are structured, versioned, and machine-checkable.

**vs. Confluence ADR pages** — No CI integration, no cross-linking, no staleness detection. ArchSpec checks run on every push.

**vs. OpenSpec** — OpenSpec drives feature development (SDD). ArchSpec drives system architecture (SDA). Different scope, same philosophy.

**vs. nothing** — Decisions become folklore. Six months later, nobody knows why the system is shaped the way it is.

</details>

---

## Quick Start

```bash
pip install sda-cli
cd your-repo
sda init
```

`sda init` scaffolds the full structure — inbox, ADR template, service model, OWNERS.yaml, and a ready-to-use GitHub Actions CI workflow.

---

## CLI Reference

| Command | What it does |
|---|---|
| `sda init` | Scaffold a new SDA project from templates |
| `sda capture "title"` | Create a draft problem in `architecture/inbox/` |
| `sda check [--strict]` | Validate ADR lifecycle, staleness, and ownership |
| `sda index [--validate]` | Generate or validate `architecture/index.yaml` |
| `sda status` | Health overview — problems, ADRs, services, index age |

---

## Docs

→ **[Getting Started](docs/guides/getting-started.md)** — first steps in 10 minutes<br>
→ **[Your First ADR](docs/guides/first-adr.md)** — step-by-step walkthrough<br>
→ **[Multi-Team Setup](docs/guides/multi-team.md)** — domain ownership and conflict resolution<br>
→ **[Problems](docs/concepts/problems.md)** — inbox schema and triage lifecycle<br>
→ **[Decisions](docs/concepts/decisions.md)** — ADR format, state machine, PR labels<br>
→ **[Knowledge Graph](docs/concepts/knowledge-graph.md)** — querying architecture with `yq`<br>
→ **[Governance](docs/concepts/governance.md)** — OWNERS.yaml, CODEOWNERS, review policy<br>
→ **[Mental Model](docs/mental-model.md)** — the philosophy behind SDA<br>

---

## License

MIT
