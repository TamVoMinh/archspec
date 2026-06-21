## ADDED Requirements

### Requirement: Self-contained offline graph rendering
`sda graph` SHALL render the knowledge graph as a single HTML file that opens with no network
access. The graph engine and its layout dependencies SHALL be inlined into the output; the file
SHALL NOT reference any external script, stylesheet, or CDN.

#### Scenario: Output is self-contained
- **WHEN** `sda graph` runs on a project
- **THEN** an HTML file SHALL be written (default `architecture/graph.html`)
- **THEN** the file SHALL contain no external `<script src=…>` or `<link href="http…">`
- **THEN** the file SHALL render the graph without any network request

### Requirement: Full service map with all edge types
The visualization SHALL include every registered service as a node (not only services referenced
by a problem or ADR) and SHALL draw service-to-service `depends_on` edges in addition to
problem→ADR, problem→service, and ADR→service edges.

#### Scenario: Unreferenced services and depends_on edges are shown
- **WHEN** `services.yaml` defines `api` (`depends_on: [db]`), `db`, and `auth`, and only `api` is referenced by a problem
- **THEN** the rendered graph SHALL include nodes for `api`, `db`, and `auth`
- **THEN** the rendered graph SHALL include a `depends_on` edge from `api` to `db`

### Requirement: Insight sidebar and fullscreen
The visualization SHALL present overview counts (problems, ADRs, services, edges) and a service
hotspots list (services ranked by the number of problems and ADRs touching them), and SHALL
provide a control to view the graph fullscreen.

#### Scenario: Sidebar shows counts and hotspots
- **WHEN** `sda graph` runs
- **THEN** the HTML SHALL display the problem/ADR/service/edge counts
- **THEN** the HTML SHALL display a "Service hotspots" section

### Requirement: Output path and browser open options
`sda graph` SHALL accept an `--output` path (relative paths resolved against the project dir) and
an `--open` flag that opens the generated file in the default browser.

#### Scenario: Custom output path is honored
- **WHEN** `sda graph --output custom/g.html` runs
- **THEN** the file SHALL be written at `custom/g.html`
