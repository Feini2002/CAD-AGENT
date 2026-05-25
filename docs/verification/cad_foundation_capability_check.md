# CAD Foundation Capability Check

最后更新：2026-05-25 22:08

## 最新结论

本轮在 Phase W baseline `geometry_verified` 之外，新增并验证了 CAD 调用底座能力矩阵。该矩阵已经纳入 `scripts/run_cad_validation.py` 的真实 CAD 总控，作为 `cad_capability_probe` 硬门禁。2026-05-25 22:08 进一步扩展到基础图元：独立直线、圆、弧、闭合多段线、文字、标注和矩形边框。

```text
status: pass
readback_report.status: geometry_verified
cad_capability_probe.status: cad_capability_verified
output_dir: output\validation_runs\cad-foundation-full-cad-20260525
latest_output_dir: output\validation_runs\manual-cad-after-primitive-probe
```

## 证据路径

| 证据 | 路径 / 值 | 结论 |
| --- | --- | --- |
| 单元测试 | `unittest discover -s tests` | 207 tests OK |
| repo audit | `scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings` | 0 findings |
| no-cad 总控 | `output\validation_runs\cad-foundation-no-cad-final-20260525\report.json` | `status=pass` |
| 单独能力探针 | `output\validation_runs\manual-primitive-cad-probe\cad_capability_probe.json` | `status=cad_capability_verified`，11 entities |
| 单独能力探针截图 | `output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png` | 已生成，538584 bytes |
| 整合真实 CAD 总控 | `output\validation_runs\manual-cad-after-primitive-probe\report.json` | `status=pass` |
| baseline 实体回读 | `output\validation_runs\manual-cad-after-primitive-probe\readback_report.json` | `status=geometry_verified` |
| 能力矩阵报告 | `output\validation_runs\manual-cad-after-primitive-probe\cad_capability_probe.json` | `status=cad_capability_verified`，11 entities |
| 总控截图 | `output\validation_runs\manual-cad-after-primitive-probe\cad-validation-screen.png` | 已生成，501581 bytes |

## 能力矩阵 checks

| check | status | 摘要 |
| --- | --- | --- |
| `active_document_read` | `pass` | 活动 DWG 为 `A1_page2_vector_full.dwg` |
| `layer_policy` | `pass` | 探针只使用 `CODEX_PREVIEW` |
| `layer_ensure` | `pass` | `CODEX_PREVIEW` 可确保存在 |
| `rectangle_handles` | `pass` | 矩形 4 条线返回 handles |
| `line_handle` | `pass` | 独立直线返回 handle |
| `circle_handle` | `pass` | 圆返回 handle |
| `arc_handle` | `pass` | 弧返回 handle |
| `polyline_handle` | `pass` | 闭合多段线返回 handle |
| `text_handle` | `pass` | 文字返回 handle |
| `dimension_handles` | `pass` | 2 个对齐标注返回 handles |
| `handle_readback_count` | `pass` | 回读覆盖本轮 created handles |
| `readback_layer_scope` | `pass` | 11 个探针实体全部在 `CODEX_PREVIEW` |
| `readback_type_counts` | `pass` | 回读类型为 5 line / 1 circle / 1 arc / 1 polyline / 1 text / 2 dimension |
| `readback_bbox` | `pass` | bbox 为 900.0 x 450.0，符合探针预期 |
| `safety_preview_only` | `pass` | 未保存、未删除、未覆盖、未写正式图层 |

## 本轮加固

- 新增 `core/verification/cad_capability_probe.py`，以真实 AutoCAD COM 创建最小探针对象并按 handles 回读。
- 新增 `scripts/run_cad_capability_probe.py`，可单独运行底层 CAD 调用能力验证。
- `scripts/run_cad_validation.py` 的真实 CAD 总控新增 `cad_capability_probe` step，并对 `cad_capability_probe.json.status=cad_capability_verified` 和 checks 全 pass 做硬门禁。
- 新增 `tests/core/test_cad_capability_probe.py`，并扩展 `tests/core/test_cad_validation_runner.py`，锁住能力探针和总控门禁。
- 扩展 `AutoCADComDriver`，支持 `draw_line`、`draw_circle`、`draw_arc`、`draw_polyline`；扩展 `inspect_dwg.py`，支持圆、弧、多段线回读标准化。
- 扩展能力矩阵测试，真实 CAD 复验后确认 11 个探针实体的 handle 回读、类型统计和 bbox 全部通过。

## 安全边界

本轮只写入 `CODEX_PREVIEW`，没有保存 DWG，没有覆盖原图，没有删除实体，没有修改正式图层。能力探针会新增测试实体作为证据，不做清理，因为当前规则禁止未经批准删除实体。

该结论证明当前用户会话中的 AutoCAD COM 基础调用、preview 写入、handle 回读和实体标准化底座可用；不扩大为真实项目图纸、块库、任意 CAD_PLAN 或复杂业务几何全部准确。
