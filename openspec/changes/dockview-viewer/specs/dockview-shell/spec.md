## ADDED Requirements

### Requirement: Viewer renders as a dockview workbench
The viewer SHALL present its content in a dockview-based workbench that supports multiple
panels arranged as tabs and split/resizable groups, so a user can view the graph and one or
more documents side by side.

#### Scenario: Multiple panels arranged side by side
- **WHEN** the viewer opens with a graph panel and a document panel
- **THEN** both SHALL be visible in the workbench
- **WHEN** the user drags one panel to a screen edge
- **THEN** the workbench SHALL split into resizable groups containing the panels

#### Scenario: Panels can be tabbed and closed
- **WHEN** two document panels occupy the same group
- **THEN** they SHALL appear as tabs in that group
- **WHEN** the user closes a tab
- **THEN** that panel SHALL be removed from the workbench

### Requirement: Two delivery modes share one viewer
The viewer SHALL be delivered by the CLI in two modes that run the same application and differ
only in data source: `sda graph view` SHALL produce a static export with the model embedded
that opens offline, and `sda graph serve` SHALL run a local server feeding the same application
from live data.

#### Scenario: Static export opens offline
- **WHEN** a user runs `sda graph view`
- **THEN** a static viewer artifact SHALL be written with the model embedded
- **THEN** opening it SHALL require no network access

#### Scenario: Serve reflects live data
- **WHEN** a user runs `sda graph serve`
- **THEN** the same viewer application SHALL be served against live project data

### Requirement: The backend is read-only
The `serve` backend SHALL expose only read operations (such as fetching the model and document
content) and SHALL NOT accept writes from the viewer. Edits to architecture occur through files
and the CLI, not the viewer.

#### Scenario: Serve exposes reads only
- **WHEN** the viewer requests the model or a document in `serve` mode
- **THEN** the backend SHALL return the requested data
- **WHEN** any write/mutation of architecture data is attempted from the viewer
- **THEN** the backend SHALL NOT provide such an operation

### Requirement: Static export is self-contained and offline
The `sda graph view` artifact SHALL be self-contained and SHALL render with no network access.
It MAY be a single HTML file or a self-contained directory, but SHALL NOT depend on any external
script, stylesheet, font, or remote service, and SHALL embed the model and the document content
it needs.

#### Scenario: Export renders with networking disabled
- **WHEN** a `sda graph view` artifact is opened with networking disabled
- **THEN** the workbench, graph, and any embedded documents SHALL render
- **THEN** no request to an external host SHALL be required

### Requirement: Empty, loading, and error states are handled
The viewer SHALL present meaningful states rather than a blank screen for the degenerate cases:
an empty model, a model that fails to load, and a document that is missing or malformed. A
failure to render one panel's content SHALL NOT crash the workbench.

#### Scenario: Empty model on first run
- **WHEN** the model contains no problems, ADRs, or services (e.g. fresh `sda init`)
- **THEN** the viewer SHALL show guidance for getting started rather than an empty canvas

#### Scenario: Model fails to load
- **WHEN** the model cannot be loaded or parsed
- **THEN** the viewer SHALL show an error state explaining the failure, not a blank screen

#### Scenario: A document is missing or malformed
- **WHEN** a panel is asked to render content that is missing or malformed
- **THEN** that panel SHALL show an inline error
- **THEN** the rest of the workbench SHALL remain usable

### Requirement: Model carries a schema version
The model SHALL include a schema version, and the viewer SHALL handle a version it does not
recognize gracefully (a clear message) rather than mis-rendering. This protects frozen `view`
exports against later schema changes.

#### Scenario: Unrecognized model version
- **WHEN** the viewer loads a model whose schema version it does not support
- **THEN** the viewer SHALL show a version-mismatch message
- **THEN** the viewer SHALL NOT silently mis-render the model

### Requirement: Sensible default layout on launch
The viewer SHALL open with a sensible default layout (at minimum the `graph-view` panel
visible) so the user is never presented with an empty workbench on launch.

#### Scenario: Default layout shows the graph
- **WHEN** the viewer launches with no saved layout
- **THEN** the `graph-view` panel SHALL be visible
