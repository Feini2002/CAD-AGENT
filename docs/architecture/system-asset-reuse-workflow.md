# System Asset Reuse Workflow

本文定义系统资产跨 DWG 复用的主系统底座能力。目标不是让 Agent 只会复制一个 DWG，而是让它能理解用户语义、拆分任务、检索系统资产、校验 native source，并把可复用资产精准写入当前图。

## 目标

- 用户显式说“从 XX 资产调用 XX 放到当前 DWG”时，必须优先走系统资产库。
- 用户没有点名资产，但语义强匹配已有资产时，也要先查资产库，例如“放一个线型表到当前图”。
- 一句话可以拆成多个资产复用任务，例如“放一个线型表，再放一个沙发”。
- 每个子任务独立判定 ready / blocked，避免一个资产来源不清导致全部临场重画。
- 写入当前 DWG 默认只写 `CODEX_PREVIEW`，回读 created handles，默认不保存当前业务 DWG。

## 能力分层

| 层 | 入口 | 职责 |
| --- | --- | --- |
| 语义触发 | `analyze_system_asset_search_need` | 判断显式复用、隐式强匹配或非资产请求 |
| 任务拆解 | `infer_system_asset_reuse_tasks` | 把复合白话拆成 `asset_reuse_1..n` |
| 候选检索 | `find_system_asset_matches` | 从 `libraries/system_library/registry.json` 排序候选 |
| 计划生成 | `build_system_asset_reuse_workflow` | 生成 source spec、target layer、base point、阻断原因 |
| CAD 写入 | `apply_system_asset_reuse_workflow` | 调用 driver 跨 DWG 复制 / 插入，并做 handles 回读 |
| CLI | `scripts/reuse_system_asset.py --workflow` | 供主系统、训练脚本或人工调试复用 |

## 主系统决策

主系统收到绘图请求后，按以下顺序判断：

1. 先由 `core.assets.semantic_rules` 匹配语义规则，识别资产复用、资产沉淀、线型表、局部修复等路由提示。
2. 对系统资产 registry 做 `encodingPreflight`；若返回 `asset_registry_encoding_failed`，不得继续匹配或写 CAD。
3. 再做轻量语义触发；若是 `not_asset_reuse_request`，继续普通 `CAD_PLAN`。
4. 若触发资产库，构建 workflow。
5. 对 `ready` 子任务直接执行跨 DWG 复用。
6. 对 `partial` 子任务，保留 ready 计划，同时把 blocked 任务反馈给调度器。
7. 对 `needs_asset_match`，可转为普通绘图、询问用户、或创建候选沉淀任务。
8. 对 `needs_precise_native_source`，不得全模型空间拷贝；需要补 `includedHandles` / `blockName` / verified style source。

## 状态与证据

复用完成报告必须包含：

- `assetId`、`assetName`、`category`
- `match.score` 与 `matchedTerms`
- `nativeDwg`
- `sourceSpec`
- target layer 与 base point
- `created_handles` 与 `readbackEntityCount`
- `readbackStatus`，必须为 `ok` 才能把单个复用计划判为 `asset_reused`
- `savedCurrentDwg=false`
- blocked task 的 `reason`
- `encodingPreflight`
- `semanticRules`

这些字段是资产晋升为 `verified` 的证据来源之一；没有 handles 回读时，不能把资产说成已通过 CAD-native 复用。若 copy 返回了 handles 但当前 DWG 读不回实体，状态必须停在 `asset_reuse_readback_empty` / `asset_reuse_readback_unavailable` / `asset_reuse_readback_failed`，不得算完成。

CLI 输出必须是严格 JSON。`scripts/reuse_system_asset.py` 使用 `allow_nan=false` 语义，报告中不得出现 `NaN`、`Infinity` 或其它非标准 JSON 值。

## 当前边界

当前工作流已覆盖语义规则摘要、registry 编码预检、语义触发、多资产拆分、单句多资产识别、候选排序、精确来源门禁、workflow CLI、严格 JSON 输出、fake-driver 写入回读和负向探针。真实 CAD 复制能力已由 `AutoCADComDriver.copy_entities_from_dwg()` 证明可从系统资产 DWG 写入当前未保存 DWG；更复杂的 block 属性保持、CTB/STB / plot、跨图层样式依赖和自动布局避让仍需要后续专项扩展。
