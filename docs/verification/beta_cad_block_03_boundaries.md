# BETA-CAD-BLOCK-03 Hatch / Polyline / Layer Mapping 探针

最后更新：2026-05-26

> 后置主线：**真实 CAD 能力扩展** 第 3 小包。机器入口：`core/verification/entity_level_evidence.py`、`core/verification/cad_capability_probe.py`。

## 目标

在 CAD capability probe 报告中增加 **entity-level evidence**：

- **polyline**：写入点集 / closed / layer_role → readback 对比 + layer mapping；
- **layer mapping**：`layer_role=preview` 解析到 `CODEX_PREVIEW`；
- **hatch**：结构化 **deferred** 槽位（`hatch_unverified`），不实现真实 COM 写入。

## 已交付

| 项 | 说明 |
| --- | --- |
| Entity evidence | `assess_entity_level_evidence()`、`entity_level_evidence_allows_probe_pass()` |
| Probe 集成 | `run_cad_capability_probe()` 输出 `entity_evidence[]` + `entity_level_evidence` check |
| 契约 | `ENTITY_CONTRACTS` 增加 `hatch`（deferred）；`polyline` 标注 `beta_entity_level_probe` |
| 归一化 | `inspect_dwg` 识别 `AcDbHatch`（pattern + bbox） |
| 校验 | `validate_capability_probe_evidence` 在 `cad_capability_verified` 时要求 entity_evidence |

## 行为摘要

| 图元 | 写入 | Readback | 探针结论 |
| --- | --- | --- | --- |
| polyline | COM `draw_polyline` | handle 回读对比 | `pass` 计入 verified |
| hatch | 仅记录意图 | 无 COM 写入 | `deferred` / `hatch_unverified` |
| layer | `layer_role=preview` | 实体 layer | mapping check |

整体 probe 仍可为 `cad_capability_verified`（hatch deferred 不阻断）。

## 不能声称什么

- **不是** hatch 已在真实 CAD 验证。
- **不是** 任意图层 / 正式图层映射已全面覆盖（仅 preview 角色）。
- Fake driver 单测 **不等于** 用户 AutoCAD 会话实跑。

## 子校验

```powershell
& $py -m unittest tests.core.test_entity_level_probe tests.core.test_cad_capability_probe -v
```

## 下一小包

`BETA-CAD-BLOCK-05`：CAD beta suite 证据汇总。
