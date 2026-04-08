# Integration — Connecting Sources to the Inbox

Architecture signal arrives from many sources. ArchSpec does not try to own those sources. It provides a CLI toolkit that normalizes any input into a structured, traceable problem file in Git.

Between the source and the CLI, you need one thing: **a queue** — a dumb pipe that holds messages until something picks them up.

---

## The pattern

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  SOURCE      │────▶│  QUEUE       │────▶│  PROCESSOR   │────▶ Git
│              │     │              │     │              │
│  Human or    │     │  Always on.  │     │  AI agent    │
│  automated   │     │  No logic.   │     │  or human    │
│  tool        │     │  Just holds  │     │  with sda    │
│              │     │  messages.   │     │  CLI / MCP   │
└──────────────┘     └──────────────┘     └──────────────┘
```

Three independent concerns. Each is replaceable without affecting the others.

| Layer | Responsibility | Examples |
|---|---|---|
| **Source** | Generate signal | Slack, SonarQube, QC team, incidents, meetings |
| **Queue** | Hold messages until processed | Slack channel, Teams channel, mailbox, SQS, Redis Stream, HTTP endpoint |
| **Processor** | Read queue, run `sda capture`, open PR | GitHub Copilot, Claude, Cursor, cron script, human |

---

## Queue options

The queue is not part of ArchSpec. It is external infrastructure that most organisations already have. Any of these work:

| Queue | Cost | Setup | Always on? | AI can read? |
|---|---|---|---|---|
| Slack channel `#arch-inbox` | Free | 2 min | Yes | Yes (API / MCP) |
| Teams channel | Free | 2 min | Yes | Yes (Graph API) |
| Shared mailbox | Free | 5 min | Yes | Yes (IMAP / API) |
| GitHub Discussions category | Free | 1 min | Yes | Yes (GitHub MCP) |
| HTTP endpoint (Lambda / Cloud Function) | ~Free | 30 min | Yes | Yes (poll) |
| Redis Stream / SQS | Cheap | 1 hr | Yes | Yes (SDK) |

**Recommendation:** Start with a dedicated Slack or Teams channel. It requires no infrastructure, people can post there naturally, bots can post via webhook, and AI agents can read it via API.

---

## Source-by-source examples

### Slack

An architect notices a design concern in a Slack discussion.

**Manual:** Post to `#arch-inbox`: *"billing service has circular dependency with auth — noticed in PR #482"*

**Automated:** A Slack workflow forwards messages that get a 🏛️ reaction to `#arch-inbox`.

**Processing:** AI agent reads `#arch-inbox`, runs:
```bash
sda capture "Circular dependency: billing → auth" --source slack --type design
```

### SonarQube

A nightly scan produces findings. Most are code-level. Some are architectural.

**Automated:** SonarQube quality gate webhook posts to `#arch-inbox` when architecture-level rules fail (complexity, coupling, circular dependencies).

**Processing:** AI agent reads the message, filters for architecture-relevant findings, runs:
```bash
sda capture "God class detected: OrderProcessor (2400 lines)" --source sonarqube --type design
```

### Security audit / QC report

The QC team or an external auditor produces a report with findings.

**Manual:** QC engineer posts a summary to `#arch-inbox`: *"Auth tokens stored client-side with no rotation — finding SEC-012"*

**Automated:** Security scanning tool (Snyk, Trivy, SAST/DAST) webhook posts critical findings to the channel.

**Processing:**
```bash
sda capture "Auth tokens stored without rotation policy" --source security-audit --type security
```

### Incidents and postmortems

An incident reveals a structural weakness.

**Manual:** On-call engineer or architect posts to `#arch-inbox` during the postmortem: *"No circuit breaker on billing→payment call — third outage from same cause"*

**Processing:**
```bash
sda capture "Missing circuit breaker: billing → payment" --source incident --type reliability
```

### CI / dependency scanning

Dependabot, Renovate, or a license audit surfaces a concern.

**Automated:** GitHub Action posts to `#arch-inbox` when a critical CVE affects a core service, or when a license violation is detected.

**Processing:**
```bash
sda capture "Critical CVE in auth library: CVE-2026-1234" --source dependency-scan --type security
```

### Meetings

A decision is made verbally in a meeting. Nobody writes it down.

**Manual:** Architect posts to `#arch-inbox` immediately: *"Decided to move session storage from Redis to Postgres — performance meeting 2026-04-08"*

**Processing:**
```bash
sda capture "Move session storage Redis → Postgres" --source meeting --type design
```

---

## AI agent processing loop

The processor — whether an AI agent or a human — follows the same pattern:

```
1. READ      Check the queue for new messages
2. INTERPRET Understand what the message is about
3. DEDUP     Check existing PROB files — is this already captured?
4. CAPTURE   Run sda capture with appropriate source and type
5. ENRICH    Optionally fill in services, symptoms, constraints
6. NOTIFY    Post back: "Created PROB-007. Ready for triage."
7. WAIT      Repeat on next message
```

The AI agent does not triage. It does not make decisions. It creates **draft** problem files. The architect triages — setting status to `active`, filling in services and symptoms, and opening a PR.

### With MCP (recommended for AI agents)

AI agents with MCP access can call ArchSpec tools natively:

```
archspec.capture({
  title: "Circular dependency billing → auth",
  source: "sonarqube",
  type: "design",
  services: ["billing", "auth"],
  symptoms: ["SonarQube rule: circular-dependency"]
})
```

### With CLI (works everywhere)

Any agent with shell access can run `sda capture` directly. This is the lowest-common-denominator integration — it works with any AI tool that can execute commands.

---

## What the architect does

The architect does not need to monitor the queue. The AI agent does that. The architect does two things:

1. **Triage** — Review draft PROB files (flagged by `sda check`), fill in details, set status to `active`.
2. **Decide** — Write ADRs that link to problems, open PRs, follow the governance review process.

```
sda check
  ⚠ PROB-007 is draft — triage within 48h (SLA: 48h)
  ⚠ PROB-008 is draft — triage within 48h (SLA: 48h)
```

The capture problem is solved. The discipline holds. Nothing was lost between the source and the inbox.

---

## Deduplication

The same issue may surface multiple times — SonarQube flags it weekly, an engineer mentions it in Slack, the QC team includes it in a report. The processor should check for existing problems before creating a new one.

For AI agents, this means reading `architecture/inbox/` and comparing titles, services, and symptoms before running `sda capture`. For CLI users, `sda check` will flag potential duplicates in a future release.

A recommended practice: include an `external_ref` in the PROB YAML when the source has its own identifier:

```yaml
id: PROB-007
title: Circular dependency billing → auth
source: sonarqube
external_ref: sonarqube:rule-circular-dep:billing-auth
```

This makes deduplication reliable across repeated scans.

---

## What ArchSpec does not do

ArchSpec is a toolkit, not a platform. It does not:

- Run a queue or message broker
- Host a webhook receiver
- Provide a Slack bot
- Operate a dashboard
- Filter findings from external tools

These are responsibilities of the queue layer and the processing layer — both of which are external to ArchSpec and replaceable independently.
