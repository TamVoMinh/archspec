## ADDED Requirements

### Requirement: Service nodes record declared dependencies
`sda index` SHALL record each service's `depends_on` list (from `services.yaml`) on its service
node in the generated graph. Services with no declared dependencies SHALL carry an empty list.

#### Scenario: Declared dependencies appear on the service node
- **WHEN** `services.yaml` defines `api` with `depends_on: [db, cache]`
- **THEN** `architecture/index.yaml` SHALL contain `graph.api.depends_on == [db, cache]`

#### Scenario: Service without dependencies carries an empty list
- **WHEN** `services.yaml` defines `db` with no `depends_on`
- **THEN** `graph.db.depends_on` SHALL be `[]`

#### Scenario: Referenced services still record dependencies
- **WHEN** PROB-001 references service `api` and `api` declares `depends_on: [db]`
- **THEN** `graph.api.problems` SHALL include `PROB-001`
- **THEN** `graph.api.depends_on` SHALL be `[db]`

### Requirement: Dependencies are merged across partitions
When partitions exist, the master index SHALL preserve each service's `depends_on`, unioning the
lists if the same service name appears in more than one partition.

#### Scenario: depends_on preserved in partitioned master index
- **WHEN** partition `payments` defines `svc-orders` with `depends_on: [svc-ledger]`
- **THEN** the master `architecture/index.yaml` service node `svc-orders` SHALL include `svc-ledger` in its `depends_on`
