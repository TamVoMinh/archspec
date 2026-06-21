## ADDED Requirements

### Requirement: A plugin is a dock panel
The viewer's only contribution type SHALL be a panel. A panel plugin SHALL declare a manifest
of `id`, `title`, `icon`, the content types it `handles`, and a `capability` of `view` or
`serve`, plus the component that renders it. There SHALL be no other contribution types
(commands, menus, decorators) in this capability.

#### Scenario: Panel registered and mounted by id
- **WHEN** a panel plugin is registered with a unique `id`
- **THEN** the workbench SHALL be able to mount that panel by its `id`

#### Scenario: Panel declares the content types it handles
- **WHEN** a request to open content of a given content type occurs
- **THEN** a panel whose `handles` includes that content type SHALL be eligible to render it

### Requirement: Panels declare a view/serve capability
Each panel SHALL declare whether it works in `view` (pure-client) or requires `serve`
(backend-dependent). In `view` mode, a `serve`-only panel SHALL degrade gracefully rather than
error.

#### Scenario: Serve-only panel degrades in static export
- **WHEN** a `serve`-capability panel is opened in a static `view` export
- **THEN** the panel SHALL show a graceful message indicating it requires `serve` mode
- **THEN** the viewer SHALL NOT crash

### Requirement: First-party panels
The viewer SHALL ship first-party panels: a `graph-view` panel and a `markdown` panel in the
initial version, with a `mermaid` panel following. A PlantUML panel is explicitly out of scope
for the initial version and SHALL be added later as a `serve`-capability panel.

#### Scenario: Graph and markdown panels available
- **WHEN** the viewer loads
- **THEN** a `graph-view` panel and a `markdown` panel SHALL be available to open

### Requirement: Graph-view panel renders the knowledge-graph model
The `graph-view` panel SHALL render the knowledge-graph model — problems, ADRs, services, and
all edge types including service-to-service `depends_on` — superseding the standalone generated
HTML graph.

#### Scenario: depends_on edges shown in the panel
- **WHEN** the model contains a service `api` with `depends_on: [db]`
- **THEN** the `graph-view` panel SHALL render a dependency edge from `api` to `db`

#### Scenario: All node types rendered
- **WHEN** the model contains problems, ADRs, and services
- **THEN** the `graph-view` panel SHALL render a node for each

### Requirement: Each node type maps to openable content
Selecting a graph node SHALL resolve to content the viewer can open, per node type:
- an **ADR** node opens its Markdown file (`markdown` content),
- a **problem** node opens its problem record (its YAML / a rendered problem view),
- a **service** node opens a service detail derived from its `services.yaml` entry (it has no
  standalone file), and
- a **group** node focuses/filters the graph to its children rather than opening a document.
A node with openable content SHALL trigger `document.open` with the appropriate content type.

#### Scenario: Opening an ADR node
- **WHEN** the user activates an ADR node
- **THEN** `document.open` SHALL be emitted with that ADR id and `markdown` content type

#### Scenario: Opening a service node with no standalone file
- **WHEN** the user activates a service node
- **THEN** the viewer SHALL open a service detail derived from its `services.yaml` entry
- **THEN** the viewer SHALL NOT error due to the absence of a standalone service file

#### Scenario: Activating a group node
- **WHEN** the user activates a group node
- **THEN** the `graph-view` SHALL focus/filter to that group's child services

### Requirement: Graph-view renders partitions and groups
The `graph-view` panel SHALL visually distinguish partitions (nodes annotated with `system`)
and SHALL render hierarchical service groups (`group` nodes and their `children`), so a
multi-partition workspace is legible rather than an undifferentiated graph.

#### Scenario: Partition boundaries are visible
- **WHEN** the model annotates nodes with `system` values for multiple partitions
- **THEN** the `graph-view` SHALL visually distinguish nodes by partition

#### Scenario: Service groups are represented
- **WHEN** the model contains a `group` node with `children`
- **THEN** the `graph-view` SHALL represent the group and its membership

### Requirement: Selection does not relayout the graph
A `selection.changed` event SHALL update the `graph-view` highlight only; it SHALL NOT recompute
the graph layout. Node positions SHALL remain stable across panel rebuilds (for example, when a
document panel opens and splits the dock), so the graph never jumps or re-arranges on
interaction.

#### Scenario: Selecting a node highlights without re-arranging
- **WHEN** a node is selected from the search panel or by clicking it in the graph
- **THEN** that node SHALL be highlighted
- **THEN** every node SHALL remain in its prior position (no relayout)

#### Scenario: Layout is stable across a rebuild
- **WHEN** the graph panel is rebuilt (e.g. a document panel opens and splits the dock)
- **THEN** nodes SHALL return to the same positions rather than being laid out afresh

### Requirement: Fuzzy search across the model
The viewer SHALL provide fuzzy search across nodes and documents (problems, ADRs, services).
Selecting a result SHALL drive selection and/or open the corresponding content via the event
bus. Consistent with the panels-only model, search is provided as a panel.

#### Scenario: Search locates and navigates to a node
- **WHEN** the user searches for a term matching a problem, ADR, or service
- **THEN** matching results SHALL be listed
- **WHEN** the user selects a result
- **THEN** the viewer SHALL select and/or open the corresponding node via the bus

### Requirement: Rendered content is sanitized
Panels that render authored content (Markdown, diagrams) SHALL sanitize it so that embedded
scripts or active content cannot execute, since the `view` export is a shareable artifact.

#### Scenario: Script in authored content does not execute
- **WHEN** a document contains an embedded script or active-content payload
- **THEN** the rendering panel SHALL neutralize it
- **THEN** no injected script SHALL execute when the document is viewed

### Requirement: Document links and attachments resolve in both modes
The viewer SHALL resolve relative links and attachments referenced by a document (e.g. captured
via `--attach` or the inbox folder layout). In a static `view` export, referenced attachments
SHALL be available offline.

#### Scenario: Attachment available in a static export
- **WHEN** a document references an attachment and the project is exported with `sda graph view`
- **THEN** the attachment SHALL be reachable from the rendered document offline
