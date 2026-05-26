# BETA-CAD-BLOCK-02 属性块 / Tag Readback 探针

最后更新：2026-05-26

> 后置主线：**真实 CAD 能力扩展** 第 2 小包。机器入口：`core/verification/block_attribute_probe.py`、`examples/plans/insert_block_alpha_attribute_probe.json`。

## 目标

为受控 `insert_block_alpha` 增加 **attribute / tag readback 探针**：

- 带 `object.attribute_readback_probe` + `object.attributes` 的计划可声明期望 tag；
- readback 实体缺 tag 时输出 **结构化 deferred**（`attribute_unverified`），**不得**误报 `geometry_verified`；
- 无 probe 标记的计划 **不运行** attribute 检查（避免对普通块误报）。

## 已交付

| 项 | 说明 |
| --- | --- |
| Probe | `check_block_attribute_readback()`、`merge_block_readback_checks()` |
| CAD 归一化 | `inspect_dwg.normalize_com_entity()` 读取 `GetAttributes()` |
| 计划校验 | `validate_insert_block_alpha` 仅允许 probe 计划携带 `object.attributes` |
| 报告 | `build_block_alpha_readback_report` 合并 attribute 判定 |
| 示例 | `insert_block_alpha_attribute_probe.json` |

## 行为摘要

| 计划 | 实体 attributes | 结果 |
| --- | --- | --- |
| 无 probe | 任意 | attribute `not_run`；几何按原规则 |
| 有 probe | 缺失 | `deferred` + `blocks_geometry_verified` → 顶层 **非** geometry_verified |
| 有 probe | tag 匹配 | attribute pass；几何 pass 时可 geometry_verified |
| 有 probe | tag 不匹配 | `fail` / deferred |

COM `insert_block_alpha` **仍拒绝** 带 attributes 的写入（`attribute_unverified`）；本包先固化 readback 探针与 no-CAD/模拟实体测试。

## 不能声称什么

- **不是**真实 CAD 属性块已全面验证（受控样本 + 探针计划 only）。
- **不是**任意 DWG 动态块 / 公司块库属性准确。
- 模拟 COM 实体测试 **不等于** 用户会话下 AutoCAD 实跑（真实 CAD 留给后续包）。

## 子校验

```powershell
& $py -m unittest tests.core.test_block_attribute_probe tests.core.test_block_alpha_validation -v
```

## 下一小包

`BETA-CAD-BLOCK-04`：`drawing_standard_profile` 与受控图层/样式映射。
