## ADDED Requirements

### Requirement: ADR PRs carry a lifecycle label
Every PR that adds or modifies a file under `architecture/adr/` SHALL carry one of the following labels: `adr/proposed`, `adr/accepted`, `adr/rejected`, or `adr/contested`. A PR without such a label SHALL be considered `adr/proposed` by default.

#### Scenario: New ADR PR is labelled proposed
- **WHEN** a PR is opened adding a new ADR file with `status: proposed`
- **THEN** the PR SHALL carry the `adr/proposed` label

#### Scenario: Label transitions to accepted after approvals
- **WHEN** a PR has 2 approvals including the architecture lead and no blocking reviews
- **THEN** the label SHALL be updated to `adr/accepted` and the ADR file's `status` field SHALL be updated to `accepted` before merge

### Requirement: Contested ADRs are escalated to the architecture lead
If two contributors open PRs with ADRs that modify the same service within 7 calendar days and their decisions conflict, the architecture lead SHALL schedule a joint resolution session within 3 business days.

#### Scenario: Conflicting ADRs are flagged
- **WHEN** two open ADR PRs both reference the same service and propose mutually exclusive decisions
- **THEN** both PRs SHALL be labelled `adr/contested` and a comment SHALL notify the architecture lead

#### Scenario: Resolution supersedes both conflicting ADRs
- **WHEN** the joint session produces a resolution
- **THEN** a new ADR SHALL be created with `status: accepted` and both original ADRs SHALL be updated to `status: superseded` with `superseded_by` pointing to the resolution ADR

### Requirement: PR review requirements match the change type
The following minimum approval rules SHALL be enforced via branch protection and `CODEOWNERS`:
- New inbox problem: 1 approver (any contributor)
- New ADR (`adr/proposed`): 1 approver (domain owner)
- ADR acceptance (`adr/accepted`): 2 approvers (domain owner + architecture lead)
- `services.yaml` change: architecture lead required
- `schemas/` change: architecture lead required

#### Scenario: ADR acceptance without arch lead approval is blocked
- **WHEN** a PR proposes `adr/accepted` but the architecture lead has not approved
- **THEN** GitHub branch protection SHALL block the merge

#### Scenario: Inbox problem PR requires only one contributor approval
- **WHEN** a PR adds only a new problem YAML file and has 1 approval
- **THEN** the PR SHALL be mergeable without further reviewer requirements
