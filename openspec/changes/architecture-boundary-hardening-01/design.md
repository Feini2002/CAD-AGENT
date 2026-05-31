## Context

The repository is now a portable CAD Agent Core Lab with Core platform work closed and active work focused on training loops, asset intelligence, and real-CAD proof gates. Several useful modules exist, but the boundary between stable Core, training experiments, and case-specific code is becoming harder to see. The highest-risk pressure points are `core/verification/`, the capability map page/data generator, asset promotion flow, and reusable code that still lives under `projects/.../runs/`.

## Goals / Non-Goals

**Goals:**

- Publish one current module-boundary snapshot that future agents can read before refactoring.
- Make the first split contracts explicit for verification, capability-map, object-family asset trials, and case-run migration.
- Keep the package scoped to architecture hardening and guardrails, not a broad system rewrite.
- Add machine-checked tests that ensure the boundary snapshot stays discoverable and covers the agreed pressure points.

**Non-Goals:**

- Do not change CAD execution behavior, registry semantics, `CAD_PLAN` schema, or Table C coverage.
- Do not migrate all large verification files in this package.
- Do not promote raw reference files to `libraries/system_library/` without executable checks and readback evidence.
- Do not create a second roadmap inside OpenSpec.

## Decisions

1. **Use a boundary snapshot before code movement.**
   - Rationale: the main risk is not just file size; it is unclear ownership. A snapshot lets later code splits be evaluated against stable categories instead of ad hoc folder moves.
   - Alternative considered: immediately split every file over 500 lines. Rejected because it would be mechanical and high-risk without proving the target ownership boundaries.

2. **Classify code into stable Core, training experiments, and case-only code.**
   - Rationale: these three buckets match the repository's current operating model and the user's requested boundary language.
   - Alternative considered: classify by directory only. Rejected because some paths such as `core/training/` are intentionally experimental despite living under `core/`.

3. **Define split maps as contracts, then migrate incrementally.**
   - Rationale: `core/verification/` and capability-map files are valuable but dense. Splitting by report contract, runner, registry writeback, visual audit, data builder, page shell, and display config creates a stable target without forcing risky churn.
   - Alternative considered: treat line count as the only split trigger. Rejected because a smaller file can still have unclear responsibilities.

4. **Use `residential_sofa_2seat` as the first object-family asset trial candidate.**
   - Rationale: it has recent training rounds and real-CAD/readback context, making it the best candidate for a controlled raw reference -> executable check -> system asset loop.
   - Alternative considered: start with a new object family. Rejected because this package should harvest existing proof instead of opening a new evidence surface.

5. **Promote project-run logic only after evidence gates.**
   - Rationale: renderer/audit code under `projects/.../runs/` may be useful, but moving it into Core before multiple validated rounds would turn case-specific assumptions into platform behavior.
   - Alternative considered: move all reusable-looking helpers now. Rejected because case assumptions are still entangled with sofa-specific geometry and training feedback.

## Risks / Trade-offs

- [Risk] The snapshot can become stale. -> Mitigation: link it from `docs/architecture/README.md` and add tests that require the key sections and split maps.
- [Risk] This package may feel lighter than a full refactor. -> Mitigation: make the non-goal explicit and leave the next migration gates concrete.
- [Risk] The first asset trial could be mistaken for a promoted capability. -> Mitigation: state that it remains a candidate until executable checks, system asset evidence, `CAD_PLAN`, and readback pass.
- [Risk] OpenSpec could become a second backlog. -> Mitigation: keep tasks scoped to this package and reference `CORE_RESTRUCTURE_PLAN.md` as the only mainline.

## Migration Plan

1. Add the boundary snapshot under `docs/architecture/`.
2. Link the snapshot from the architecture docs index.
3. Add tests that assert the snapshot includes the three buckets, split maps, asset trial route, and case migration gate.
4. Update status/changelog records.
5. Run targeted tests and repository/documentation verification.

Rollback is documentation-only for this package: remove the snapshot, its README link, the OpenSpec change, and the focused tests if the direction is rejected.

## Open Questions

- Which verification file should be split first in the next package: report contract validation or visual audit/readback helpers?
- Should the first capability-map implementation split create a static `capability-map-config.js`, or should display config stay embedded until the page shell is smaller?
