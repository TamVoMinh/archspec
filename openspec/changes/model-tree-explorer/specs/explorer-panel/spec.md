## ADDED Requirements

### Requirement: Explorer is a browsable model tree
The viewer SHALL provide an `explorer` panel that presents the architecture model as a tree:
folders are logical groupings and leaves are artifacts (problems, ADRs, services). It SHALL be
the viewer's primary navigation surface, replacing the flat search panel. The tree SHALL NOT be
a literal filesystem mirror (services that share a `services.yaml` SHALL each appear as their
own leaf).

#### Scenario: Services appear as individual leaves
- **WHEN** several services are defined in one `services.yaml`
- **THEN** the Explorer SHALL show each service as its own leaf, not a single file node

#### Scenario: Artifacts are reachable by browsing
- **WHEN** the model contains problems, ADRs, and services
- **THEN** each SHALL be reachable as a leaf under its grouping folders

### Requirement: Group-by toggle re-roots the tree
The Explorer SHALL provide a control to change the grouping of the tree, supporting at least
**system**, **type**, and **service group**. Changing the grouping SHALL re-root the tree
without losing the current model.

#### Scenario: Switch grouping
- **WHEN** the user changes Group-by from "type" to "system"
- **THEN** the tree SHALL re-root so partitions are the top-level folders containing their
  problems, ADRs, and services

#### Scenario: Service groups as folders
- **WHEN** grouping is "service group" and the model has a `group` node with children
- **THEN** that group SHALL appear as a folder containing its member services

### Requirement: Integrated fuzzy filter
The Explorer SHALL include a filter input. Typing SHALL narrow the tree to leaves matching the
query (fuzzy) plus their ancestor folders; clearing the input SHALL restore the full tree. The
filter SHALL match on an artifact's id/label, and on its title where the model provides one
(titles are not yet carried in the model — see the follow-up task to surface them).

#### Scenario: Filter narrows the tree
- **WHEN** the user types a query matching some artifacts
- **THEN** the tree SHALL show only matching leaves and the folders that contain them

#### Scenario: Clearing restores the tree
- **WHEN** the filter input is cleared
- **THEN** the full tree SHALL be shown again

### Requirement: Folders show counts
Each folder SHALL display the count of artifact leaves it contains, counted recursively across
any nested subfolders, so magnitude is visible without expanding.

#### Scenario: Count shown on a folder
- **WHEN** a grouping folder contains 210 services
- **THEN** the folder SHALL display its count (e.g. "Services (210)")

### Requirement: Selecting an artifact opens it
Selecting a leaf SHALL emit `selection.changed` and `document.open` for that artifact, as the
search panel did; selecting/expanding a folder SHALL NOT open a document.

#### Scenario: Leaf selection opens the document
- **WHEN** the user selects a service leaf
- **THEN** the viewer SHALL select that node and open its document via the event bus

#### Scenario: Folder toggle does not open a document
- **WHEN** the user expands or collapses a folder
- **THEN** no `document.open` SHALL be emitted

### Requirement: Tree is virtualized for scale
The Explorer SHALL render efficiently for large models (hundreds to thousands of nodes) by
rendering only visible rows, so scrolling and filtering stay responsive.

#### Scenario: Large model stays responsive
- **WHEN** the model contains many hundreds of artifacts
- **THEN** the Explorer SHALL remain responsive to scroll and filter (only visible rows rendered)

### Requirement: Artifacts outside a grouping are not lost
For any grouping, artifacts that do not have a value for that grouping dimension SHALL still
appear, collected under an explicit leftover folder (e.g. "Unscoped" / "Ungrouped") rather than
being dropped from the tree.

#### Scenario: Unscoped artifacts when grouping by system
- **WHEN** grouping is "system" and a problem has no `system` (or a root-level ADR exists)
- **THEN** that artifact SHALL appear under an "Unscoped" folder, not be omitted

#### Scenario: Non-service artifacts when grouping by service group
- **WHEN** grouping is "service group"
- **THEN** problems and ADRs (which have no service group) SHALL appear under a leftover folder
- **THEN** services with no group SHALL appear under a leftover folder

### Requirement: Empty model shows guidance
When the model contains no artifacts, the Explorer SHALL show getting-started guidance rather
than a blank rail, consistent with the rest of the viewer.

#### Scenario: Empty model
- **WHEN** the model has no problems, ADRs, or services
- **THEN** the Explorer SHALL display guidance instead of an empty tree

### Requirement: Explorer reflects the current selection
The Explorer SHALL indicate the currently selected artifact when its row is visible, including
when the selection originates elsewhere (e.g. clicking a node in the graph). Expanding/scrolling
to reveal an off-screen selection (reveal-in-Explorer) is out of scope for this requirement.

#### Scenario: Selection from the graph is reflected
- **WHEN** a node is selected in the graph and its row is visible in the Explorer
- **THEN** that row SHALL be shown as selected

### Requirement: Deterministic ordering
Within a folder, folders and leaves SHALL be ordered deterministically (e.g. folders first, then
leaves, each sorted by id/label), so the tree is stable across renders.

#### Scenario: Stable order
- **WHEN** the tree is rendered for the same model and grouping more than once
- **THEN** items within each folder SHALL appear in the same order each time
