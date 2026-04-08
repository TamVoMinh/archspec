# The Architecture Problem

*Why ArchSpec exists — and why the status quo is costing you more than you think.*

---

You are not short on architecture documentation.

You have a wiki. You have diagrams. You probably have a folder somewhere called `adr/` with fifteen Markdown files nobody has opened in four months. You have a Confluence page titled "System Architecture — v3 — FINAL" last edited by someone who left the company in November.

And yet, every time a new engineer joins, you spend two weeks explaining why things are the way they are. Every time an incident happens, the postmortem surfaces the same structural weakness you identified eighteen months ago but never formally addressed. Every time someone proposes a refactor, the team argues about constraints that were already reasoned through — because that reasoning lives in the memory of three people who were in a room together in 2024.

**The documentation is not the problem. The discipline is.**

---

## Decisions are not first-class citizens

In your codebase, every line has a commit. Every function has a test (or should). Every dependency is declared explicitly. The code is a rigorous, machine-verifiable artifact.

Your architectural decisions are not.

They live in meeting notes, in Slack threads, in the heads of principal engineers, in PDFs that were attached to Jira tickets that were closed. They are not versioned alongside the code they motivated. They are not validated in CI. They cannot be queried. They cannot be read by the AI assistant generating code in your codebase right now.

Code is a first-class citizen. Decisions are folklore.

**Folklore does not scale. Folklore does not survive team turnover. And in 2026, folklore does not feed into your AI agents.**

---

## The architect is the bottleneck

You review PRs because you are the only one who holds the full picture. You get tagged in every conversation about service boundaries because that knowledge lives in your head and nowhere else. You are the single point of failure for architectural context in your organisation.

This is not your fault. It is a systems problem. The architecture practice was not designed to be queryable, delegatable, or automatable — so it centralised around the person who cared most about it.

Every time you are the bottleneck, an engineer is waiting. Every time an engineer is waiting, value is not being delivered. The architect who is always in the critical path is not doing architecture — they are doing support.

**The goal is not to make you work harder. It is to make your judgment enforceable without your presence.**

---

## The signal you are losing

The bottleneck is not just about decisions. It starts earlier — at capture.

Architecture-relevant signal arrives from every direction. Slack threads. Meeting side-comments. SonarQube scans flagging structural debt. Security audits from the QC team. Incident postmortems that surface the same root cause for the third time. A dependency scanner that found 12 new CVEs overnight.

Most of it is never captured.

Not because you do not care. Because there is no place to put it. The signal appears in one tool, you are working in another, and by the time you have context to write it down properly, the moment has passed. Three architecture-relevant observations surface on a Tuesday. By Friday, you remember one of them — vaguely.

The problem is not that you lack a documentation habit. The problem is that there is no **fast, low-friction intake point** between "I noticed something" and "I wrote a formal decision record." The gap between those two is where architectural insight goes to die.

What you need is not a platform. Not a service. Not another dashboard. You need a **dumb pipe** — a queue that holds messages until something processes them. A Slack channel. A shared mailbox. A webhook endpoint. Anything that is always on and accepts input from any source.

On the other side of that pipe, an AI agent — or a human with a CLI — picks up the message, runs `sda capture`, and creates a structured problem file in Git. The architect triages later. The signal is not lost. The discipline holds.

```
  Sources                  Queue                   ArchSpec
  (messy, async)           (dumb pipe, always on)  (CLI toolkit)

  Slack msg ─────┐
  SonarQube ─────┤         ┌──────────┐            ┌──────────┐
  QC report ─────┼────────▶│ channel  │──── AI ───▶│ sda CLI  │──▶ Git
  Incident ──────┤         │ mailbox  │   agent    │ captures │
  Meeting ───────┤         │ webhook  │   picks up │ links    │
  PR review ─────┘         └──────────┘            └──────────┘

  You don't build          You already             You already
  this. It exists.         have this.              have this.
```

The queue does not understand architecture. It does not filter, normalize, or deduplicate. It just holds messages until something processes them. That is all it needs to do.

The AI agent is disposable and replaceable. Today it is GitHub Copilot with MCP access. Tomorrow it is Claude. Next month it is something that does not exist yet. The queue and the CLI stay the same.

**The cheapest way to stop losing signal is not a better memory. It is a dumber pipe.**

---

## Your AI agents are flying blind

Right now, an AI assistant in your codebase knows nothing about the decisions your team has made. It does not know that ADR-005 prohibits direct database access from the API layer. It does not know that PROB-032 is an open, unresolved problem with the billing service boundary. It does not know that the integration pattern it just generated was explicitly rejected eight months ago.

It generates code that is syntactically correct, logically sound, and architecturally wrong.

The fix is not prompting harder. The fix is giving your AI agents a machine-readable, always-current map of your architectural decisions before they start. Not a PDF. Not a wiki page. A structured, versioned, queryable graph — the kind that fits in a context window and updates automatically when your architecture evolves.

**In a world where code is generated by machines, the only thing that matters is the decision behind it. ArchSpec makes those decisions legible to both humans and machines.**

---

## The TDD analogy — and where it breaks

Spec-Driven Architecture borrows the core discipline from TDD: the specification must exist before the implementation. You write the decision record before you write the code, the same way you write the failing test before you write the function.

But the analogy has a gap. In TDD, the test fails if the code is wrong. In SDA without verification, you can write a rigorous ADR, accept it through a careful review process, and have every subsequent engineer ignore it — and nothing will catch it.

ADR-012 says the caching layer must not be accessed directly by the API gateway. Is that still true after 60 commits and two team changes? Nobody knows, because nobody checked.

**A decision that cannot be verified is aspirational documentation. ArchSpec closes the loop — decisions define constraints, and those constraints are validated automatically.**

---

## What this requires

Not a new tool category. Not a migration to another platform. Not a new meeting.

A discipline. A small, enforced set of practices:

- Every problem gets captured before anyone starts discussing solutions
- Every decision traces back to a problem
- Every commit that implements a decision references it
- Every constraint in a decision is validated in CI
- Every service has a named owner and a review date

These are not new ideas. Architects have known this for years. What has been missing is tooling lightweight enough to make the discipline stick — that runs in your existing CI, stores everything in Git, and takes less than ten minutes to set up.

That is what ArchSpec is.

---

*ArchSpec does not replace your judgment. It makes your judgment enforceable, traceable, and permanent — for the engineers working with you today, the AI agents working alongside them, and the architect who inherits this system in 2028.*
