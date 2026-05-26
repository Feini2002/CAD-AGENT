# Block Alpha 真实 CAD 证据（R-BLOCK-CAD-05）

最后更新：2026-05-26

## 运行命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_cad_validation.py --block-alpha-only --output-dir output\validation_runs\r-block-alpha-cad
```

## 证据目录

`output/validation_runs/r-block-alpha-cad/`

| 文件 | 说明 |
| --- | --- |
| `report.json` | 总控 `status=pass`，`block_alpha.geometry_verified=true` |
| `block_alpha_execution_summary.json` | 执行摘要，`created_handles` 非空 |
| `block_alpha_report.json` | `status=geometry_verified`，`evidence_state=readback_geometry_verified` |
| `block-alpha-window.png` | 窗口级视觉辅助，`screenshot_role=visual_aid_only` |

## 可声称 / 不可声称

- **可声称**：受控 `CODEX_TEST_BLOCK_001` 在 `CODEX_PREVIEW` 上完成一次真实插入，created handle 定向 readback 全部 pass。
- **不可声称**：任意块库、属性块、正式图层、真实项目图纸或全部 `insert_block_alpha` 计划均已几何 verified。

## 2026-05-26 Codex 追加验收

## 2026-05-26 Codex 第二轮追加验收

- `output/validation_runs/codex-second-gate-block-alpha-cad-final/report.json`：`status=pass`，created handle `99B`，`block_alpha.geometry_verified=true`，`block_alpha_readback` 为 `readback_geometry_verified`。
- `output/validation_runs/codex-second-gate-full-cad-final/report.json`：`status=pass`，baseline handles `99C..9E6` 与 block handle `ABC` 均完成 created-handle readback。
- 负向 COM 探针：非法 `block_id`、非法 `block_name`、attributes、非法 `base_point` 均被拒绝；当前测试 DWG ModelSpace 实体数 `131 -> 131`。
- 本轮新增门禁：runner 会把 readback 报告中的 created handles 与上一阶段 execution summary 交叉比对；block alpha 几何通过必须包含 `created_handles_scope=pass` 和完整 block_reference 几何字段。

- `output/validation_runs/codex-review-block-alpha-cad-after-gate/report.json`：`status=pass`，`block_alpha.geometry_verified=true`，created handle `879`。
- `output/validation_runs/codex-review-full-cad-after-gate/report.json`：`status=pass`，baseline handles `87A..8C4` 与 block handle `99A` 均完成 created-handle readback。
- 负向 COM 探针：任意 `block_id` / 任意 `block_name` 均被 driver 拒绝；`CODEX_PREVIEW` 实体数 `111 -> 111`，未新增实体。
- 新门禁要求：`geometry_verified` 必须绑定非空 `created_handles`、实体回读 payload 和 `created_handles_scope=pass`；block alpha 还必须满足 `entity.type=block_reference`。
