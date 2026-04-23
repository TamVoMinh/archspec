## ADDED Requirements

### Requirement: Recursive service file discovery
The `sda index` command SHALL recursively discover all `services.yaml` files under `architecture/model/` and merge them into a single index.

#### Scenario: Root-level services only (existing behavior)
- **WHEN** only `architecture/model/services.yaml` exists
- **THEN** `sda index` SHALL read it as before — all services are root-level with no group

#### Scenario: Services in subdirectory
- **WHEN** `architecture/model/payments/services.yaml` exists alongside `architecture/model/services.yaml`
- **THEN** `sda index` SHALL discover both files and merge their services into the index

#### Scenario: Subdirectory name becomes group
- **WHEN** `architecture/model/payments/services.yaml` defines services `svc-orders`, `svc-cache`, `svc-worker`
- **THEN** each service SHALL have `group: payments` in the index and a `payments` group node SHALL be created

### Requirement: Group nodes in index
The index SHALL include group nodes (`type: group`) for each service subdirectory, with a `children` list of service names.

#### Scenario: Group node structure
- **WHEN** `architecture/model/payments/services.yaml` contains services `svc-orders` and `svc-cache`
- **THEN** `index.yaml` SHALL contain a node `payments` with `type: group` and `children: [svc-orders, svc-cache]`

### Requirement: Service name global uniqueness
Service names SHALL be globally unique across all `services.yaml` files regardless of group.

#### Scenario: Duplicate service name across groups
- **WHEN** `architecture/model/services.yaml` defines `api` and `architecture/model/infra/services.yaml` also defines `api`
- **THEN** `sda check` SHALL report an error indicating duplicate service name `api`

### Requirement: Service validation across split files
The `sda check` service validators (ownership, staleness, domain coverage) SHALL apply to all discovered `services.yaml` files, not just the root one.

#### Scenario: Staleness check in subdirectory
- **WHEN** `architecture/model/payments/services.yaml` has a service with `last_reviewed` older than 180 days
- **THEN** `sda check` SHALL report a staleness warning for that service

### Requirement: Status shows group counts
The `sda status` command SHALL display service counts per group when hierarchical services exist.

#### Scenario: Status with groups
- **WHEN** the model has 2 root services and 3 services under `payments`
- **THEN** `sda status` SHALL show `Services 5 total (2 root, 3 in payments) none stale`
