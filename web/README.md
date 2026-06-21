# @archspec/web — dockview viewer

The front end for `sda graph view` / `sda graph serve`: a React + Tailwind + dockview
workbench. Plugins are dock panels (graph-view, document, search); panels coordinate via an
FE-only event bus and never reference each other.

## Develop

```bash
pnpm install
pnpm --filter @archspec/web dev        # dev server with bundled sample data
pnpm --filter @archspec/web test       # vitest (bus, store, router, elements)
pnpm --filter @archspec/web typecheck
pnpm --filter @archspec/web build       # single self-contained dist/index.html
```

## How it ships

`scripts/build-viewer.sh` builds this app and copies `web/dist/index.html` to
`cli/src/sda/viewer/index.html`, which is packaged into the `sda-cli` wheel. End users get
`sda graph view`/`serve` with no Node. The Python side embeds the model + documents
(`view`) or serves them read-only (`serve`); the app picks its data source by context
(embedded → `view`, dev → sample, served → http).

The model contract lives in `packages/model`.
