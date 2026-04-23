## ADDED Requirements

### Requirement: Folder-based problem discovery
The SDA CLI SHALL discover problem files in both flat (`PROB-XXX.yaml`) and folder (`PROB-XXX/PROB-XXX.yaml`) layouts within `architecture/inbox/`.

#### Scenario: Flat file discovery (existing behavior)
- **WHEN** `architecture/inbox/PROB-001.yaml` exists as a bare file
- **THEN** `sda index`, `sda check`, and `sda status` SHALL include PROB-001 in their results

#### Scenario: Folder-based discovery
- **WHEN** `architecture/inbox/PROB-003/PROB-003.yaml` exists inside a folder
- **THEN** `sda index`, `sda check`, and `sda status` SHALL include PROB-003 in their results

#### Scenario: Mixed layouts
- **WHEN** the inbox contains both `PROB-001.yaml` (flat) and `PROB-003/PROB-003.yaml` (folder)
- **THEN** both problems SHALL be discovered and included in the index

#### Scenario: Duplicate detection
- **WHEN** both `PROB-001.yaml` and `PROB-001/PROB-001.yaml` exist
- **THEN** `sda check` SHALL report an error indicating a duplicate problem ID

### Requirement: Non-YAML files in problem folders are ignored
The scanner SHALL only parse `PROB-XXX.yaml` files inside problem folders. All other files (attachments, markdown, images) SHALL be ignored by the scanner.

#### Scenario: Attachments alongside problem YAML
- **WHEN** `PROB-003/` contains `PROB-003.yaml`, `source-email.msg`, and `screenshot.png`
- **THEN** only `PROB-003.yaml` SHALL be parsed; other files SHALL not affect scanning

### Requirement: Problem ID extraction from folder layout
The problem ID SHALL be derived from the YAML `id` field, falling back to the filename stem — regardless of whether the file is flat or in a folder.

#### Scenario: ID from YAML field in folder layout
- **WHEN** `PROB-003/PROB-003.yaml` contains `id: PROB-003`
- **THEN** the problem SHALL be indexed as `PROB-003`
