#!/usr/bin/env bash
# Build the web viewer bundle and stage it for packaging into the sda-cli wheel.
#
# Run before `python -m build cli/` so the wheel includes the prebuilt viewer
# (cli/src/sda/viewer/index.html). End users then get `sda graph view`/`serve`
# without needing Node.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

pnpm install --frozen-lockfile
pnpm --filter @archspec/web build

mkdir -p cli/src/sda/viewer
cp web/dist/index.html cli/src/sda/viewer/index.html

echo "✓ Staged web/dist/index.html -> cli/src/sda/viewer/index.html"
