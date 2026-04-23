# Design: Release Automation Architecture

## Architecture Overview

The release automation system is built on GitHub Actions and uses a three-layer approach to integrate Conventional Commits, Release Management, and Package Distribution.

### 1. Version Scaling and Changelog Generation

We use `release-please-action` configured for a monorepo setup. The bot monitors the `main` branch for new commits.

-   **Trigger:** Push to `main`.
-   **Detection:** Filters commits since the last release tag.
-   **Action:** If version-impacting commits (feats, fixes, breaking changes) are found, it opens or updates a Pull Request titled `chore(main): release X.Y.Z`.
-   **Files Updated:**
    -   `cli/pyproject.toml` (version field)
    -   `CHANGELOG.md` (root directory)

### 2. The Release Trigger

The actual release is triggered by **user action**. When the "Release PR" is merged into `main`, `release-please` performs the following:
-   Creates a Git tag matching the version (e.g., `v0.1.0`).
-   Creates a GitHub Release containing the changelog notes.

### 3. Distribution Pipeline

The `publish.yml` workflow is configured to listen for the `release` event.

-   **Trigger:** `release: published`.
-   **Security:** Uses GitHub OIDC (Trusted Publishing) for authentication with PyPI.
-   **Steps:**
    1.  Checkout the tagged commit.
    2.  Build the distribution wheel (`python -m build cli/`).
    3.  Upload to PyPI using the official `pypa/gh-action-pypi-publish`.

## Configuration Files

### `release-please-config.json`
Specifies how the tool interprets the repository structure.

### `.release-please-manifest.json`
Tracks the current version state to ensure continuity between automation runs.
