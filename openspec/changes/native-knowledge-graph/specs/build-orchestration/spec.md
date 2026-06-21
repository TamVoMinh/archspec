## ADDED Requirements

### Requirement: One-command regeneration of derived artifacts
`sda build` SHALL regenerate all derived artifacts from source in a single invocation: the
knowledge-graph index (`architecture/index.yaml`) and the interactive graph
(`architecture/graph.html`).

#### Scenario: Build produces index and graph together
- **WHEN** `sda build` runs on a project
- **THEN** `architecture/index.yaml` SHALL be (re)generated
- **THEN** `architecture/graph.html` SHALL be (re)generated
- **THEN** the command SHALL exit 0 on success

#### Scenario: Built index reflects current sources
- **WHEN** `services.yaml` defines `api` with `depends_on: [db]`
- **WHEN** `sda build` runs
- **THEN** `architecture/index.yaml` SHALL contain `graph.api.depends_on == [db]`

### Requirement: Build supports opening the result
`sda build` SHALL accept an `--open` flag that opens the generated graph in the default browser
after building.

#### Scenario: Open flag opens the built graph
- **WHEN** `sda build --open` runs and completes successfully
- **THEN** the generated `architecture/graph.html` SHALL be opened in the default browser
