## Change Type

<!-- Select the type that applies to this PR. Add the corresponding label. -->

- [ ] New inbox problem (`PROB-*.yaml`) → label: _(no ADR label needed)_
- [ ] New ADR (`status: proposed`) → label: **`adr/proposed`**
- [ ] ADR acceptance (`status: accepted`) → label: **`adr/accepted`**
- [ ] Service model change (`services.yaml`) → label: _(no ADR label needed)_
- [ ] Schema change (`schemas/`) → label: _(no ADR label needed)_
- [ ] Other / docs / tooling

---

## Checklist

### For ADR PRs
- [ ] `## Metadata` block is present with `status`, `date`, `superseded_by`, and `links` fields
- [ ] All links reference existing `PROB-*.yaml` files
- [ ] All affected services exist in `architecture/model/services.yaml`
- [ ] If `status: superseded`, `superseded_by` is set to a valid ADR identifier
- [ ] PR label matches the ADR status

### For Inbox Problem PRs
- [ ] `id` follows `PROB-XXX` format
- [ ] `source` is one of: `slack`, `jira`, `github`, `meeting`, `email`, `adhoc`
- [ ] If `status: active`, `services` and `symptoms` are non-empty

### For Service Model PRs
- [ ] `last_reviewed` is set to today's date for any new or modified services
- [ ] `owner` email is set for any new services
- [ ] New service is added to `domain_ownership` in `OWNERS.yaml`

### Required Reviewers

<!-- GitHub CODEOWNERS will auto-request reviewers. Verify below: -->

| This PR touches | Required approvers |
|---|---|
| `architecture/model/` | Architecture lead |
| `schemas/` | Architecture lead |
| `architecture/adr/` | Domain owner + Architecture lead |
| `OWNERS.yaml` | Architecture lead |
| Inbox only | Any contributor |

---

## Summary

<!-- Brief description of what this PR adds or changes, and why -->

---

## ADR Label Reference

> Create these labels in GitHub repository Settings → Labels if they don't exist:
> - `adr/proposed` — colour `#0075ca`
> - `adr/accepted` — colour `#0e8a16`
> - `adr/rejected` — colour `#e4e669`
> - `adr/contested` — colour `#d93f0b`
