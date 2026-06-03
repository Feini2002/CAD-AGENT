## 1. Tests First

- [x] 1.1 Add failing tests for default style-token schema/profile validation and token resolution.
- [x] 1.2 Add failing tests for `CAD_PLAN` style fields and dry-run style evidence.
- [x] 1.3 Add failing tests for preview execution summaries carrying expected style metadata.
- [x] 1.4 Add failing tests for glyph primitive style overrides.

## 2. Core Contract

- [x] 2.1 Extend drawing standard and CAD plan schemas with additive style semantics fields.
- [x] 2.2 Add default `codex_preview_beta` style tokens and layer roles for style semantics.
- [x] 2.3 Implement style-token resolution and apply it through `apply_drawing_standard_to_plan`.

## 3. Evidence Flow

- [x] 3.1 Include style evidence in dry-run reports without claiming plot verification.
- [x] 3.2 Propagate expected style metadata into preview execution summaries.
- [x] 3.3 Apply primitive-level style overrides for glyph primitives.

## 4. Governance And Verification

- [x] 4.1 Update training / status notes with evidence boundaries for style semantics.
- [x] 4.2 Run targeted tests, schema validation, OpenSpec strict validation, and required repository checks.
- [x] 4.3 Run a separate review Agent to evaluate completion and optimization opportunities, then harden once.
