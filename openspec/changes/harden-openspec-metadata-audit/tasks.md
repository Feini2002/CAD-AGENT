## 1. OpenSpec Contract

- [x] 1.1 Create proposal, design, specs, and tasks for `harden-openspec-metadata-audit`.
- [x] 1.2 Absorb the temporary planning note into OpenSpec system docs and delete the sidecar file.

## 2. Metadata Audit

- [x] 2.1 Add failing tests for missing metadata, lifecycle/archive consistency, unresolved open questions, dependency existence, and dependency cycles.
- [x] 2.2 Implement read-only OpenSpec metadata checks inside `core/maintenance/doc_governance.py`.
- [x] 2.3 Keep `scripts/run_doc_governance_audit.py` as the first-round audit entry.

## 3. Metadata Backfill

- [x] 3.1 Add minimal `.openspec.yaml` metadata for the three completed changes that lack it.
- [x] 3.2 Add minimal `metadataVersion` and `lifecycle` metadata to current active changes.

## 4. Verification

- [x] 4.1 Run targeted doc governance unit tests.
- [x] 4.2 Run OpenSpec strict validation.
- [x] 4.3 Run the document governance audit and report any remaining findings honestly.
