## 1. Governance Tests

- [x] 1.1 Add doc-governance tests for OpenSpec contract misuse and valid configuration.
- [x] 1.2 Run the focused test file and confirm the new tests fail before implementation.

## 2. Governance Implementation

- [x] 2.1 Implement `check_openspec_contracts()` in `core/maintenance/doc_governance.py`.
- [x] 2.2 Include the OpenSpec contract section in `build_doc_governance_report()`.

## 3. Documentation Routing

- [x] 3.1 Update `AGENTS.md` with lightweight OpenSpec routing rules.
- [x] 3.2 Update `CORE_RESTRUCTURE_PLAN.md` so OpenSpec is documented as a contract layer below the single PlanMD.
- [x] 3.3 Update status, changelog, and handoff records for this package.

## 4. Verification

- [x] 4.1 Run focused doc-governance tests.
- [x] 4.2 Run `scripts/run_doc_governance_audit.py`.
- [x] 4.3 Validate the OpenSpec change artifacts.
