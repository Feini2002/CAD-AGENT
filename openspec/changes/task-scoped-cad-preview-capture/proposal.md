## Why

当前截图能力底层已支持 AutoCAD 客户区截图和按 `execution_summary.created_handles` 聚焦，但多个训练 / 验证入口没有统一调用该协议，导致 CAD 在后台或 DWG 含大量图块时，用户看到的仍可能是当前大视图、整窗或空的视觉证据。

本变更把截图默认口径收紧为“低打扰、强聚焦、弱证据”：默认不抢前台，优先按本轮任务对象取景，只截 AutoCAD 客户区；截图继续只作 `visual_aid_only`，真实 CAD 几何仍以 created handles / readback / audit 为准。

## What Changes

- 增强 `render_preview` 聚焦协议：支持从 `execution_summary` 提取 handles / bbox，返回 focus source、handle count、target bbox、capture mode 和 occlusion-safe 字段。
- 支持局部修复 / 单项复验的精准目标：当调用方提供 `target_handles`、`repair_plan.target_handles` 或 `repair_plan.target_bbox` 时，截图只围绕该局部目标，而不是整批 execution summary。
- 精准截图时禁止在 handles / bbox 不可用时静默 `ZoomExtents` 到全图，改为显式报告 focus target unavailable，避免海量图块重新进入视野。
- 让 `--layer` 真正进入 execution summary 聚焦链路。
- 第一批 runner 统一接入任务级截图：当前基础训练主入口、视觉 CAD review、跨机器复验入口。
- 训练 / 验证报告写入结构化 `visualPreview`，包括 `role=visual_aid_only` 和聚焦 / 截图失败原因。
- 不改变 CAD 保存、正式图层写入、几何验收门槛或表 C 口径。

## Capabilities

### New Capabilities

- `task-scoped-cad-preview`: 任务级 CAD 视觉辅助截图协议，覆盖 AutoCAD 客户区截图、按本轮 handles / bbox 聚焦、失败分类和证据边界。

### Modified Capabilities

- None.

## Impact

- Affected code: `core/verification/render_preview.py`, `core/verification/visual_cad_review.py`, `core/verification/cross_machine_reverify.py`, `core/training/foundation_batch_training.py`, `scripts/run_cad_foundation_remaining_training.py`.
- Affected tests: `tests/core/test_render_preview.py`, `tests/core/test_cad_foundation_remaining_training.py`, and targeted visual review / cross-machine tests if needed.
- Affected systems: training evidence reports, CAD validation visual checkpoints, user-facing preview screenshots.
- Scope behavior: local repair and single-item retest captures prefer explicit target handles / repair bbox over whole-batch handles.
- Evidence boundary: screenshots remain visual aids only; geometry completion claims still require CAD readback of created handles.
