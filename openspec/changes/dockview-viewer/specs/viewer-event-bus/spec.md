## ADDED Requirements

### Requirement: Panels communicate only through an FE event bus
Panels SHALL coordinate exclusively through a front-end publish/subscribe event bus and SHALL
NOT hold direct references to one another. Events SHALL be fire-and-forget notifications; the
bus SHALL NOT require correlation ids, reply events, or a command/query split.

#### Scenario: Selection propagates without direct coupling
- **WHEN** the `graph-view` panel emits a `selection.changed` event for a node
- **THEN** any subscribing panel SHALL receive it
- **THEN** the emitting panel SHALL NOT reference the subscribing panels directly

#### Scenario: Opening a document is requested via an event
- **WHEN** a panel emits a `document.open` event for an artifact id and content type
- **THEN** an eligible panel SHALL render that document
- **THEN** the requester SHALL NOT call the rendering panel directly

### Requirement: Defined v1 event vocabulary
The bus SHALL support at least the following events: `model.loaded`, `selection.changed`,
`document.open`, `graph.highlight`, `panel.mounted`, and `panel.disposed`. The event vocabulary
together with the panel manifest SHALL constitute the plugin contract.

#### Scenario: Documented events are available
- **WHEN** a panel subscribes to `selection.changed`, `document.open`, or `graph.highlight`
- **THEN** the bus SHALL deliver those events to the subscriber when emitted

### Requirement: Current state is queryable for late-mounting panels
A shared store SHALL hold current state — at least the current selection and the loaded model —
so a panel that mounts after an event already fired can read current state on mount. Events
announce changes; the store holds the current value.

#### Scenario: Late-mounted panel reads current selection
- **WHEN** a `selection.changed` event has set the current selection
- **WHEN** a new panel is mounted afterward
- **THEN** that panel SHALL be able to read the current selection from the store on mount

### Requirement: Reading data is separate from the event bus
Fetching content (the model, a document's text) SHALL be a pull operation against the store or
data source (embedded data in `view`, a read fetch in `serve`) and SHALL NOT be modeled as a
bus event.

#### Scenario: Document content is pulled, not evented
- **WHEN** a panel needs a document's content
- **THEN** it SHALL read it from the store or data source
- **THEN** it SHALL NOT obtain the content by emitting and awaiting a bus event

### Requirement: document.open is routed to a capable panel
A `document.open` event SHALL be dispatched to a panel that handles the requested content type
and is available in the current mode (`view`/`serve`). If more than one panel is eligible, the
viewer SHALL pick one deterministically. If none is eligible, the viewer SHALL surface a clear
message rather than failing silently. (Whether opening reuses the active panel or opens a new
tab is an open design question — see design.md.)

#### Scenario: Routed to a handling panel
- **WHEN** a `document.open` event names a content type a registered panel handles
- **THEN** that panel SHALL render the requested content

#### Scenario: No eligible panel
- **WHEN** a `document.open` event names a content type no available panel handles
- **THEN** the viewer SHALL surface a clear message
- **THEN** the viewer SHALL NOT fail silently or crash
