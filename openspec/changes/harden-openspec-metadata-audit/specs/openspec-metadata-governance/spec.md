## ADDED Requirements

### Requirement: OpenSpec change metadata v2 is machine-auditable

Each active OpenSpec change under `openspec/changes/<change>/` MUST expose enough `.openspec.yaml` metadata for a read-only checker to determine schema, metadata version, lifecycle status, archive readiness, dependencies, supersedes relationships, open question closure, and governance evidence boundary.

#### Scenario: Missing metadata is reported

- **WHEN** an active change has no `.openspec.yaml` or lacks `metadataVersion` / `lifecycle.status`
- **THEN** the document governance audit reports findings for that change

#### Scenario: Completed change is not archive-ready

- **WHEN** a change remains under `openspec/changes/` with `lifecycle.status=complete` and `archiveReady=false`
- **THEN** the metadata MUST include a human-readable archive reason

### Requirement: OpenSpec dependency metadata is checked without mutation

The audit MUST check declared `dependsOn`, `blockedBy`, and `supersedes` references for existence and dependency cycles without modifying files, changing lifecycle status, or archiving changes.

#### Scenario: Dependency cycle is blocked

- **WHEN** change metadata forms a cycle through `dependsOn` or `supersedes`
- **THEN** the document governance audit reports a blocked finding that names the affected change

#### Scenario: Missing relationship target is reported

- **WHEN** a dependency or supersedes target does not exist under active or archived OpenSpec changes
- **THEN** the document governance audit reports the missing target

### Requirement: Open questions cannot remain unresolved in complete changes

Changes with `lifecycle.status=complete` or `lifecycle.status=archive-ready` MUST NOT retain an `openQuestions` item with `status=open`.

#### Scenario: Complete change has unresolved question

- **WHEN** a complete change metadata file contains `openQuestions` with an item whose `status` is `open`
- **THEN** the document governance audit reports the unresolved question
