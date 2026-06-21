## 1. Service dependency edges

- [x] 1.1 In `_build_graph()` (`index.py`), attach `depends_on` to each service node from the model (both referenced and model-only branches)
- [x] 1.2 Update `_merge_into()` to union `depends_on` across partitions
- [x] 1.3 Extract `assemble_graph(project_dir) -> (graph, partitions)` and `_build_partitioned_graphs()`; refactor `index()` to reuse them
- [x] 1.4 Tests: service nodes carry `depends_on`; referenced service also carries `depends_on`

## 2. Interactive graph (`sda graph`)

- [x] 2.1 Vendor Cytoscape.js + fcose stack (MIT) into `cli/src/sda/assets/`; package via `pyproject.toml`
- [x] 2.2 New `commands/graph.py`: convert graph → Cytoscape nodes/edges (4 edge kinds incl. `depends_on`), compute stats + hotspots
- [x] 2.3 Render a self-contained HTML template with inlined assets, responsive layout, fullscreen toggle, click-to-highlight, insight sidebar
- [x] 2.4 Options: `--output`, `--open`, `--project-dir`; default `architecture/graph.html`
- [x] 2.5 Register `graph` in `main.py`
- [x] 2.6 Tests: writes output, self-contained (no external `<script src>`), `depends_on` edge present, hotspots section, custom output, partitioned includes all services

## 3. Build orchestration (`sda build`)

- [x] 3.1 New `commands/build.py`: run index then graph in-process with a combined summary
- [x] 3.2 Register `build` in `main.py`
- [x] 3.3 Tests: produces both index.yaml and graph.html; index reflects `depends_on`

## 4. Service reference validation (`sda check`)

- [x] 4.1 `validators/services.py`: `load_service_names()`, `validate_depends_on()` (ERROR), `validate_problem_service_refs()` (WARNING, accepts precomputed registry)
- [x] 4.2 `validators/adr.py`: `validate_adr_service_existence()` (WARNING)
- [x] 4.3 Wire new checks into `_flat_checks()` and `_partitioned_checks()` (partitioned problem refs use the union registry)
- [x] 4.4 Tests: missing `depends_on` target → ERROR + `--strict` exit 1; valid → clean; unknown problem ref → WARNING; partitioned depends_on

## 5. Output hygiene, docs, packaging

- [x] 5.1 `scaffold.py`: `sda init` adds `.gitignore` rule for generated graph HTML (idempotent)
- [x] 5.2 Repo `.gitignore`: ignore `architecture/**/graph.html`
- [x] 5.3 Fix stale `aos` leftovers in `scaffold.py` (package name + workflow template path)
- [x] 5.4 Docs: `readme.md` CLI table, `docs/concepts/knowledge-graph.md` (depends_on + visualization + build)

## 6. Verification

- [x] 6.1 `pytest cli/tests` — all green (74 passed)
- [x] 6.2 `sda build --project-dir example` → index shows `depends_on`, graph.html written
- [x] 6.3 Render graph.html in a browser — full service map + `depends_on` edges + hotspots, offline
- [x] 6.4 Negative: broken `depends_on` → `sda check --strict` exits 1; clean → exits 0
- [x] 6.5 `openspec validate native-knowledge-graph` passes
