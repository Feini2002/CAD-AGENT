## Why

OpenSpec changes are structurally consistent, but most lifecycle and cross-change meaning still lives in Markdown prose or task checkbox inference. This makes completed changes, dependency relationships, unresolved design questions, and future archive readiness hard for machines to audit.

## What Changes

- Introduce `.openspec.yaml` metadata v2 as a lightweight machine-readable layer for change lifecycle, dependencies, supersedes links, impact declarations, open-question closure, and verification notes.
- Extend the existing document governance audit with read-only OpenSpec metadata checks.
- Backfill minimal metadata for active changes, prioritizing changes that currently lack `.openspec.yaml`.
- Keep archive migration, stable spec consolidation, and runtime Agent behavior changes out of scope.

## Capabilities

### New Capabilities

- `openspec-metadata-governance`: OpenSpec change metadata lifecycle and read-only machine audit.

### Modified Capabilities

无。

## Impact

- Code: `core/maintenance/doc_governance.py`
- Tests: `tests/core/test_doc_governance.py`
- OpenSpec metadata: `openspec/changes/*/.openspec.yaml`
- Docs: `openspec/README.md`, `openspec/config.yaml`; the temporary planning note was absorbed into this change and removed.
- Verification: OpenSpec strict validation and doc governance / unit checks.
- Evidence boundary: governance-only; no CAD execution, no Table C change, no training workbench refresh, no runtime Agent gate change.
