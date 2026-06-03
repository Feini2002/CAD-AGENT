## 1. Cache Foundation

- [x] 1.1 Add tests for building and reusing a current-DWG block cache manifest.
- [x] 1.2 Implement `core.visual_retrieval.current_dwg_cache` with manifest serialization and document identity validation.

## 2. Generic Quick Composite Task

- [x] 2.1 Add tests for object-agnostic `find_and_annotate_bbox_dimensions` planning and reporting.
- [x] 2.2 Implement `core.quick_tasks.find_and_annotate` using cached candidates when valid and live snapshot fallback when needed.
- [x] 2.3 Add generic CLI `scripts/run_quick_composite_task.py`.

## 3. Verification

- [x] 3.1 Run targeted unit tests for visual retrieval, dimension annotation, cache, and quick task modules.
- [x] 3.2 Run the generic quick composite CLI against the active sofa DWG and record elapsed time/source.
- [x] 3.3 Update status/changelog with concise evidence and boundaries.
