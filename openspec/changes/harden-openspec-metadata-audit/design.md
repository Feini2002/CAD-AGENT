## Context

The repository already uses OpenSpec for scoped complex changes and has a local README plus config boundary that keeps OpenSpec below `CORE_RESTRUCTURE_PLAN.md`. The missing layer is machine-readable change metadata: current CLI status can infer completion from `tasks.md`, but cannot express archive readiness, dependency graphs, supersedes relationships, unresolved design questions, or schema / Agent impact intent.

The existing `core/maintenance/doc_governance.py` audit already checks that OpenSpec does not become a second master plan or global backlog. This change extends that same audit surface before considering a dedicated OpenSpec audit script.

## Goals / Non-Goals

**Goals:**

- Define minimal metadata v2 fields for `.openspec.yaml`.
- Check metadata presence, lifecycle status, completed-task consistency, archive-reason consistency, dependency existence, supersedes existence, dependency cycles, and unresolved open questions.
- Backfill active changes with minimal lifecycle metadata.
- Keep the audit read-only and deterministic.

**Non-Goals:**

- Do not archive completed changes.
- Do not migrate stable specs.
- Do not make OpenSpec the global backlog or PlanMD.
- Do not let runtime CAD / Agent gates read OpenSpec markdown.
- Do not change CAD capability claims, Table C, training facts, or workbench snapshots.

## Decisions

1. **Reuse document governance first**

   Add metadata checks under `check_openspec_contracts()` instead of creating a new top-level script immediately. This keeps the first implementation small and lets existing governance output carry the findings.

2. **Use a small, permissive metadata parser**

   `.openspec.yaml` currently uses a constrained subset of YAML. The audit only needs simple keys and relationship lists, so it uses a local parser instead of adding a new dependency. If future metadata grows more complex, the audit can switch to a real YAML parser under a later change.

3. **Treat dependency problems as findings, not auto-fixes**

   Missing dependencies, dependency cycles, and unresolved open questions should appear as audit findings. The checker must not rewrite metadata or archive changes.

4. **Require lifecycle metadata for active changes**

   Active changes under `openspec/changes/` should have `.openspec.yaml`, `metadataVersion`, and `lifecycle.status`. Completed changes left outside archive should also state `archiveReady` and an archive reason when not ready.

## Risks / Trade-offs

- [Risk] The simple YAML parser may miss future complex YAML shapes. -> Mitigation: keep supported fields simple and document dedicated parser migration as a later option.
- [Risk] Backfilling metadata across many changes creates noisy churn. -> Mitigation: add minimal fields only; do not fill full impact maps for every historical change.
- [Risk] OpenSpec governance expands into a second planning system. -> Mitigation: checks enforce metadata and boundaries only; next/backlog remains in the existing PlanMD and task ledger.

## Migration Plan

1. Add tests for missing metadata, lifecycle / archive consistency, unresolved open questions, dependency existence, and dependency cycles.
2. Implement the read-only audit inside `core/maintenance/doc_governance.py`.
3. Backfill minimal `.openspec.yaml` metadata for current active changes.
4. Validate OpenSpec and run targeted unit / governance checks.
5. Leave archive migration for a future explicit change.

## Sidecar Absorption

The temporary planning note was used only to collect the pre-implementation discussion. Its durable content now lives in this change contract and the OpenSpec local entry:

- Current facts: there are 20 active changes in this working tree, and the originally noted missing metadata set expanded to include `prove-main-agent-cognition-loop`.
- Implemented scope: metadata presence, metadata version, lifecycle status, completed-task consistency, archive reason, unresolved open questions, missing dependency / supersedes targets, and dependency-cycle detection.
- Deferred scope: structured impact conflict detection, `impact.breaking` propagation, schema target validation, and Agent target validation.
- Evidence boundary: governance-only; no archive migration, CAD execution, Table C movement, training fact write, or workbench refresh.

The sidecar file is deleted after absorption so `docs/planning/` does not keep a second planning surface.

## Open Questions

无。
