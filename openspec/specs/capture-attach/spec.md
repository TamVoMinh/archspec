## ADDED Requirements

### Requirement: Attach files when capturing a problem
The `sda capture` command SHALL accept an `--attach` option that takes one or more file paths to co-locate with the captured problem.

#### Scenario: Capture with single attachment
- **WHEN** user runs `sda capture "title" --attach ~/report.pdf`
- **THEN** the CLI SHALL create `architecture/inbox/PROB-XXX/PROB-XXX.yaml` and copy `report.pdf` into the same folder

#### Scenario: Capture with multiple attachments
- **WHEN** user runs `sda capture "title" --attach email.msg --attach screenshot.png`
- **THEN** the CLI SHALL create `architecture/inbox/PROB-XXX/PROB-XXX.yaml` and copy both files into the same folder

#### Scenario: Capture without attachments (backward compatible)
- **WHEN** user runs `sda capture "title"` without `--attach`
- **THEN** the CLI SHALL create `architecture/inbox/PROB-XXX.yaml` as a flat file (existing behavior)

### Requirement: Attachment file validation
The CLI SHALL validate that each `--attach` path points to an existing file before creating the problem.

#### Scenario: Non-existent attachment path
- **WHEN** user runs `sda capture "title" --attach /does/not/exist.pdf`
- **THEN** the CLI SHALL exit with an error message indicating the file does not exist and SHALL NOT create any problem file

### Requirement: Attachment file naming
Attached files SHALL retain their original filename when copied into the problem folder.

#### Scenario: Original filename preserved
- **WHEN** user attaches `~/Downloads/Microsoft Notification (April 2026).msg`
- **THEN** the file SHALL be copied as `architecture/inbox/PROB-XXX/Microsoft Notification (April 2026).msg`
