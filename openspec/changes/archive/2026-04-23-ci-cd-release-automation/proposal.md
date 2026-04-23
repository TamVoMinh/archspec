# Proposal: CI/CD Release Automation with Release Please

## Problem Statement

Currently, releasing the `sda-cli` package requires manual steps:
1.  Manually bumping the version in `pyproject.toml`.
2.  Creating a git tag and pushing it.
3.  Drafting and publishing a GitHub Release.
4.  Writing a manual changelog.

This process is error-prone, inconsistent, and often results in missing or low-quality release notes. Furthermore, there is no enforcement of versioning conventions across different releases.

## Proposed Solution

We propose integrating Google's `release-please` tool to automate the entire release lifecycle. By following **Conventional Commits** (e.g., `feat:`, `fix:`, `feat!:`), the framework will automatically:
-   Determine the next version number (Semantic Versioning).
-   Maintain a single, consolidated `CHANGELOG.md` file.
-   Open and update a persistent "Release PR" on every merge to `main`.
-   Create a GitHub Release and tag when the Release PR is merged.
-   Trigger the PyPI publishing pipeline once the release is created.

## Expected Outcomes

-   **Consistency:** All releases follow Semantic Versioning based on commit history.
-   **Traceability:** Automated changelogs link every code change to a specific version.
-   **Control:** Releases are only finalized when a human merges the Release PR, providing a built-in safety gate.
-   **Efficiency:** Developers spend zero time on manual versioning and release management.
