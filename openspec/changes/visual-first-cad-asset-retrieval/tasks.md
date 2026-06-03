## 1. Core Retrieval

- [x] 1.1 Create the `core.visual_retrieval` module and data models for query profiles, block candidates, scoring signals, and reports.
- [x] 1.2 Implement semantic/visual profile parsing for sofa screenshot requests.
- [x] 1.3 Implement visual-first candidate ranking with bbox ratio, furniture scale, source-layer, semantic, and optional block-definition signals.

## 2. CLI And Reports

- [x] 2.1 Add a read-only CLI that connects to the active AutoCAD session and runs current-DWG block retrieval.
- [x] 2.2 Emit JSON reports with elapsed time, Top-K candidates, best-match CAD readback evidence, evidence boundaries, and safety fields.

## 3. Verification

- [x] 3.1 Add unit tests for sofa profile parsing and candidate ranking.
- [x] 3.2 Run the simulated find-sofa-from-screenshot command against the current CAD session and record elapsed time.
- [x] 3.3 Update repository status/changelog with the visual-first retrieval V0 evidence and limits.
