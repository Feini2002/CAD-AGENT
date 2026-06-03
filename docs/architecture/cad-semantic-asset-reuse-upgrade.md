# CAD Semantic Asset Reuse Upgrade

本文记录 `cad-semantic-asset-reuse-upgrade` 系统级升级。目标是把语义规则库、系统资产沉淀、跨 DWG 复用、线型表布局验收和中文编码门禁串成主系统底座，而不是继续依赖单次 prompt 记忆。

## 升级范围

- **语义规则库**：`core.assets.semantic_rules` 记录资产复用、资产沉淀、线型表和局部修复的触发词、路由、必跑门禁、禁止行为、验收 hooks 和证据边界。
- **复用前编码门禁**：`core.assets.system_asset_reuse` 在 registry 文本参与匹配前运行 `asset_registry_encoding_preflight`；坏中文、`??`、`�` 或典型 mojibake 会返回 `asset_registry_encoding_failed`，不生成 ready 计划。
- **候选排序**：系统资产匹配按 score、生命周期、native DWG、精确来源可用性和 asset id 做稳定排序，避免 candidate / metadata-only 资产压过 verified 资产。
- **跨 DWG 复用**：仍以 `build_system_asset_reuse_workflow` / `apply_system_asset_reuse_workflow` 为入口；单个复用计划只有 created handles 且 `readbackStatus=ok` 才能成为 `asset_reused`。
- **线型表独立审计**：`core.training.linetype_table_audit` 从 report + snapshot 审计中文文本、无填充、样线格 containment、自适应行高、样式差异和证据边界。
- **可变行数**：`draw_linetype_table(..., rows=...)` 支持 focused 表、全量表或未来扩展表，不再把 24 行 / 42 行当成硬限制。

## 主系统路由

```text
用户白话
  -> semantic_rules.match_semantic_rules
  -> orchestrator.semantic_asset_route
  -> system_asset_reuse.analyze_system_asset_search_need
  -> registry encoding preflight
  -> asset match / task split / source gate
  -> CAD_PLAN or system_asset_reuse_workflow
  -> created handles readback / layout audit / evidence boundary
```

语义规则库不是最终执行器。它只负责告诉主系统“应该优先尝试哪条路、哪些行为绝对禁止、需要哪些验收”。`core.orchestrator.semantic_asset_route` 会在普通 workflow dispatch 报告中写出资产复用路由；实际 CAD 写入仍由 reuse workflow、CAD_PLAN、training drawer 或 repair_plan 执行。

## 线型表门禁

线型表规则必须同时满足：

- 可见文本通过 UTF-8 / mojibake preflight。
- 报告中有 canonical 中文词，例如“线型”“样线”“用途与测试点”。
- 不创建 hatch / solid / wipeout / fill 类实体。
- 分组行不被竖向列线切割；样线不越出 `sampleCellBbox`。
- 开启范围线的圆弧和两条控制线都在样线单元格内。
- 行高按样线需求自适应，允许分栏、压缩和扩展，但不得使用固定 24 行限制。
- 线型、颜色、线宽和 BYLAYER 差异必须来自实体属性 readback。
- 截图只作视觉辅助，不证明 CTB/STB 或打印输出。

## 资产复用门禁

资产复用必须满足：

- registry 文本编码预检通过。
- 弱匹配只返回候选，不自动复用。
- `candidate` / `metadata_only` 可以被看见，但不能冒充 `verified`。
- `object_block` 必须有 `includedHandles`、`blockName` 或其它合同允许的精确来源。
- `style_standard` 只走 verified style source，不误做 block export。
- 当前业务 DWG 默认只写 `CODEX_PREVIEW`，并保持 `savedCurrentDwg=false`。

## 验证证据

本升级的首批证据：

- `tests.core.test_semantic_asset_rules`
- `tests.core.test_system_asset_reuse`
- `tests.core.test_system_asset_sedimentation`
- `tests.core.test_linetype_table_demo`
- `tests.core.test_script_bootstrap`
- `output/validation_runs/system-assets/semantic-upgrade/reuse_workflow_plan.json`
- `output/validation_runs/linetype-table/semantic-upgrade/linetype_table_report.json`

当前证据主要是 Core / fake CAD / plan-only；真实 CAD 跨 DWG 复用能力已由上一轮 `system-asset-reuse-linetype-table-20260602` 证明。后续新增对象资产时，应继续补真实 CAD readback 和人工复审。
