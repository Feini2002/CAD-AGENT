# System Asset Sedimentation Protocol

本文定义用户说“沉淀 XX 资产”时的默认动作。它面向通用 CAD Agent，不绑定某一个训练案例、某一个 DWG 或某一个工具。

## 一句话

通用资产沉淀不是保存一张截图，也不是只在当前 `CODEX_PREVIEW` 里画一次；它必须形成可检索、可应用、可验收的系统资产包。

## 四件套

每个系统资产包至少承担四类职责：

| 职责 | 典型文件 | 说明 |
| --- | --- | --- |
| 机器契约 | `assets.json` / `standard.json` | 记录资产 ID、类别、别名、用途、尺寸、证据、边界 |
| CAD 原生资产位置 | `*_assets.dwg` / `.dwt` | 保存或预留 AutoCAD 原生图层、样式、块、图元资产 |
| 应用 / 验收工具 | `scripts/sediment_system_asset.py`，后续可扩展 `ensure_*` / `verify_*` | 负责登记、导入、应用和回读验收 |
| 全局索引 | `libraries/system_library/registry.json` | 告诉 Agent 什么时候优先使用这个系统资产 |

注意：四件套是职责，不是固定文件数。简单资产可以共用脚本；复杂资产可以有多个 JSON、多个 DWG 或专门检查器。

## 资产库守门员

“沉淀 XX 资产”必须先经过 `pipeline_asset_governor`。守门员不是落图执行器，而是资产库入口的判断者：

- 判断请求是否真的是系统资产沉淀，而不是一次 quick trial、普通训练通过或临时预览。
- 判断来源边界是否足够精确：`selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox`、`named_block` 或 `style_definition`。
- 决定本轮能否写 clean reusable source，还是只能进入 `metadata_only` / `03_REVIEW_QUARANTINE`。
- 按需派发 `pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`。
- 收尾输出 `polishHardeningDecision`，说明当前范围是否完成，或还需要 native CAD relayout、reuse replay、source boundary review、Agent rule review。

守门员可以判断是否需要新增全局 Agent，但新增 Agent 必须进入 reviewed package / OpenSpec / 全局规则更新；不得在普通沉淀任务里临时发明未登记角色。主 Agent 的 `dispatchDecision` 也遵守同一边界：已登记 Agent 可以按语义动态加入 `effectiveRequiredAgents`，未登记 Agent 只能写入 `additionalAgentRequests`，状态为 `needs_reviewed_package` 或 `needs_openspec_change`，不得临场激活或用来放行完成声明。

| Agent | 职责 | 不能做 |
| --- | --- | --- |
| `pipeline_asset_librarian` | 分类、命名、去重、检索词、状态流、资产卡片、registry / assets.json 一致性 | 不执行 CAD，不静默覆盖冲突 asset id |
| `pipeline_asset_dwg_curator` | 系统资产 DWG 分区排版、训练污染清洗、槽位、防重叠、保存 / 回读证据边界 | 不复制整屏、训练面板、当前业务 DWG，不声明未跑的 native 写入 |
| `pipeline_asset_reuse_auditor` | 复用回放、sourceSpec、created handles、readback、`verified` 晋升门禁 | 不把 metadata_only 或弱匹配当成已复用 |

## 资产 DWG 排版

系统资产 DWG 不是训练画布，也不是把 `CODEX_PREVIEW` 原封不动搬家。分类 DWG 默认按五个区组织：

| 区域 | 用途 | 是否可作为复制源 |
| --- | --- | --- |
| `00_INDEX` | 目录、asset id、状态、槽位索引 | 否 |
| `01_CLEAN_ASSETS` | 干净几何、block、style、symbol 或可复制源 | 是 |
| `02_PREVIEW_CARDS` | 人工复审资产卡：样例、尺寸、用途、状态 | 否 |
| `03_REVIEW_QUARANTINE` | 来源不清、未清洗、未过门禁的候选 | 否 |
| `99_EVIDENCE_LINKS` | 报告、截图、训练来源等证据索引 | 否 |

训练标题、课程说明、临时备注、边框、尺寸线、审计文字和证据路径默认不得进入 `01_CLEAN_ASSETS`。它们可以进 JSON 证据、资产卡片或 `99_EVIDENCE_LINKS`，但不能污染未来复制 / 插入的源。

每条资产的 `native.layoutPlan` 必须使用 v2 结构：`schemaVersion`、`zones`、`slot`、`plannedBbox`、`cleanSource`、`previewCard`、`evidenceLinks`、`cleanupPolicy` 和兼容旧读取的 `grid`。

分类资产包还可以记录 `nativeLayout.visualRackPlan`，用于描述整张系统资产 DWG 的可视仓库架构。该字段不得只是“有 A/B/C 区”的标签：必须包含 `schemaVersion >= 2`、`layoutMode=classified_expandable_visual_warehouse_v2`、`warehouseArchitecture`、`acceptanceCriteria`、rack family、slot ownership、copy policy、扩展空位和 zone bbox。真实写入货架脚手架时，还必须记录保护资产内容 bbox、created shelf entity bbox、shelf/content clearance 审计和 `visualReadabilityAudit`；任何货架框线、标签、route 或 slot grid 与保护内容相交都不能验收，通道过窄、内容密度过高、proof content 仍在 `CODEX_PREVIEW`、`ASSET_SOURCE_BOUNDARY` 大框包住 proof panel，或源定义 / 证明面板 / 标签证据角色混淆，也不能验收。`scripts/run_asset_library_governance_check.py` 必须审计当前系统库中的 `visualRackPlan` 和最新 shelf CAD readback / clearance / readability 报告；审计不过时不能把资产 DWG 说成已完成仓库验收。

## 状态流

资产沉淀后的能力状态必须显式记录，不能把“已登记”直接说成“已稳定复用”。

| 状态 | 含义 | 能否优先复用 |
| --- | --- | --- |
| `candidate` | 已登记合同和索引，但还缺少稳定复用证据 | 只能作为候选 |
| `systemized` | 已有 Prompt / 规则 / 检查器或训练证据沉淀 | 可优先考虑，但仍看边界 |
| `verified` | 已通过复用验收，例如插入 / 应用 / 回读证明 | 可作为稳定系统资产 |
| `deprecated` | 保留历史但不推荐使用 | 不优先 |

默认新资产是 `candidate`。只有补齐复用证据、原生导出证据或明确机器 / 用户验收后，才能晋升到 `systemized` 或 `verified`。

## 加固字段

每个资产条目应包含：

- `lifecycle`：状态、允许状态、晋升门槛。
- `retrieval`：别名、使用场景、场景标签、限制、尺寸和 `matchText`。
- `native.layoutPlan`：在分类 DWG 中的 v2 分区排版槽位；这只是计划，除非另有 CAD 写入证据。
- `libraryGovernance`：资产库守门员决策、子 Agent 派发、source boundary 决策和 `polishHardeningDecision`。
- `versioning`：修订号、冲突策略、变体来源。
- `verification`：当前验证状态，默认 `metadata_only`。
- `nativeVisiblePanelEvidence` 或等价可见 native 证据：当资产声称原生样式 / 图元已写入系统资产 DWG 时，记录可见图元、readback、截图和保存状态。
- `reuseWorkflowProbe` 或 `reuseReplay`：当资产声称 `verified` 或可复用时，记录白话复用 workflow ready 计划，或真实 CAD 复用 created handles / readback。
- `feedbackLoop`：用户反馈、失败原因和 learning promotion 引用。
- `exportManifest`：资产类型、导出模式、来源边界、包含 / 排除 handles。
- `antiContamination`：禁止全屏 / 全模型空间等宽泛来源污染资产库的门禁。

## 源边界门禁

对象资产是否做 block export，不由“沉淀”二字自动决定，而由来源边界决定。

| 资产类型 | 典型导出 | 允许来源 |
| --- | --- | --- |
| `object_block` | `block_export` | `selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox`、`named_block` |
| `style_standard` | `style_export` | `style_definition` 或明确标准样式定义 |
| `rule_recipe` | `metadata_only` / recipe | 规则、Prompt、检查器或生成器证据 |
| `composite_template` | metadata / template | 明确组合边界和复用验收 |

禁止把这些宽泛来源默认导出成 block：

```text
whole_codex_preview
whole_modelspace
current_screen
all_visible
training_panel
global_preview_bbox
```

如果用户只说“沉淀沙发资产”，但当前没有选中实体、刚创建 handles、明确 bbox 或已有 named block，则资产只能先记录为 `metadata_only` / `candidate`。真正导出前必须记录 `includedHandles` 和 `excludedHandles`，并排除标签、边框、尺寸线、训练说明和其它无关对象。

## 默认目录

系统自产资产统一放在：

```text
libraries/system_library/
  registry.json
  drawing_standards/
    basic/
      assets.json
      standard_assets.dwg
  furniture/
    seating/
      sofas/
        assets.json
        sofa_assets.dwg
```

分类使用点分路径，例如：

| 类别 | 目录 | 原生库 |
| --- | --- | --- |
| `drawing_standards.basic` | `libraries/system_library/drawing_standards/basic/` | `standard_assets.dwg` |
| `furniture.seating.sofas` | `libraries/system_library/furniture/seating/sofas/` | `sofa_assets.dwg` |
| `furniture.tables.tea_tables` | `libraries/system_library/furniture/tables/tea_tables/` | `tea_table_assets.dwg` |

## 默认流程

当用户明确说“沉淀 XX 资产”时：

1. 固定 UTF-8 运行环境并执行 `encodingPreflight`。项目路径、资产名、别名、用途、来源文档、中文标注或 visible text 若已经出现 `??`、`�` 或典型 mojibake，必须在写合同 / 打开 CAD 前阻断。
2. 进入 `pipeline_asset_governor`，生成 `libraryGovernance`、source boundary 决策、子 Agent 派发和 `polishHardeningDecision`。
3. 判断资产类别，例如绘图标准、沙发、茶几、门窗、灯具、符号或组合片段。
4. 解析稳定分类目录；没有目录时创建。
5. 找到或预留该分类的原生 CAD 资产库 DWG。
6. 将资产登记到分类 `assets.json`。
7. 更新 `libraries/system_library/registry.json`。
8. 写入生命周期、检索字段、`native.layoutPlan` v2、版本 / 冲突策略和反馈回流字段。
9. 写入 `assetKind`、`sourceBoundary`、`exportManifest` 和 `antiContamination`；对象类 block export 必须有精确来源。
10. “沉淀 XX 资产”本身视为对对应系统资产 DWG 的创建、打开 / 激活、写入和保存授权；如果本轮能确定原生来源并需要添加 CAD 内容，则执行原生 DWG 写入。
11. 只要本轮向对应系统资产 DWG 添加、替换或修复了原生 CAD 内容，必须保存该 DWG，并回读活动文档路径、`Saved=true` 和关键实体 / 样式证据。
12. 样式资产若记录 `native_style_definition_written` 或 `nativeWrite=written_to_standard_assets_dwg`，必须同时写入 `nativeVisiblePanelEvidence` 或等价可见 native 证据；不可见 DimStyle / Linetype / TextStyle 定义不能单独冒充可人工复审资产。
13. 资产若晋升 `verified`，必须写入 `reuseWorkflowProbe` 或 `reuseReplay`：前者证明 registry 编码预检、语义匹配、workflow 和 `sourceSpec` 已联通；后者证明真实 CAD created handles / readback 已通过。
14. 沉淀收尾时默认打开 / 激活对应系统资产 DWG，供用户人工复审；如果来源不足或没有生成 DWG，只登记合同，并在报告中标注 `nativeDwgExists=false` 和未打开原因。
15. 运行或保留验证入口：元数据验证可以 pass，但 `native visible asset evidence`、`executable reuse workflow probe`、`native DWG geometry` / `CAD insertion replay` 必须按实际证据留在 `checked` 或 `notChecked`。
16. 保存证据边界：checked / not_checked，禁止把“已登记合同”或 `layoutPlan` v2 说成“已导出原生 DWG”，也禁止把 `style_definition` ready plan 说成已经 `asset_reused`。
17. 如果本轮写入系统资产 DWG 货架脚手架，必须在报告中记录 `rackPlanAudit`、`protectedContentReadback`、created-handle 实体回读、`visualClearanceAudit` 和 `visualReadabilityAudit`：resolved handle count、per-layer counts、全量 entity bbox、unresolved handles、unmanaged layers、bbox union、保护内容簇、overlapCount、通道宽度、内容宽度占比、source/proof 分离、proof content 图层语义和 `savedCurrentBusinessDwg=false`。截图只作为人工复审入口，不替代 handles / bbox / readback / clearance / readability audit。

## 复用流程

当用户说“从 XX 资产调用 XX / 复用 XX / 插入 XX / 套用 XX / 放到当前 DWG”，或请求语义明显匹配已有系统资产时：

1. 先检索 `libraries/system_library/registry.json`，不直接从白话跳到临时重画。
2. 按 `assetId`、名称、别名、用途、标签、场景标签和 `retrieval.matchText` 做语义匹配。
3. 优先选择 `verified` / `systemized` 且有可用 `nativeDwg` 的资产；来源必须是 `includedHandles`、`blockName`、verified `style_standard` 或其它合同允许的精确边界。若资产只登记 metadata 或缺 `reuseWorkflowProbe`，只能作为候选或阻断项。
4. 写入当前 DWG 时默认只写 `CODEX_PREVIEW`，不保存当前业务 DWG。
5. 输出复用报告：matched asset、source spec、target layer、created handles、readback count、copy method、`savedCurrentDwg=false`。
6. 若匹配到资产但来源不足，返回 `needs_precise_native_source`；不得把 `whole_modelspace`、`current_screen`、`all_visible`、训练面板或全局预览 bbox 当成资产源。
7. 真实 CAD 验证通过后，资产合同可把 `CAD insertion replay` 从 `notChecked` 移入 `checked`，并登记复用报告和截图。

## 复用工作流

跨 DWG 复用必须支持复合语义，而不是只支持一个 query 对一个 asset。

默认工作流入口：

```text
用户白话
  → analyze_system_asset_search_need
  → infer_system_asset_reuse_tasks
  → build_system_asset_reuse_workflow
  → apply_system_asset_reuse_workflow
  → created handles / readback / savedCurrentDwg=false
```

工作流至少承担六类判断：

| 阶段 | 产物 | 失败 / 分流 |
| --- | --- | --- |
| 语义触发 | `explicit_reuse_language` / `implicit_asset_match` / `no_asset_signal` | `no_asset_signal` 且无强匹配时返回 `not_asset_reuse_request`，交回普通绘图链路 |
| 任务拆分 | `asset_reuse_1..n` | 无法拆分时保留整句作为一个任务 |
| 候选检索 | `candidateMatches`、best match、score、matched terms | 无候选返回 `needs_asset_match` |
| 精确来源门禁 | `sourceSpec`：handles / block / layer / style | 来源不足返回 `needs_precise_native_source` |
| 目标分配 | target layer、base point、`saveCurrentDwg=false` | 多资产可用槽位策略防重叠；精确位置应由上游 CAD_PLAN / placement 传入 |
| CAD 写入与回读 | created handles、readback count、copy method | 写入失败或读不回不得晋升为 verified |

工作流状态：

| 状态 | 含义 |
| --- | --- |
| `ready` | 所有子任务都有可执行复用计划 |
| `partial` | 至少一个子任务 ready，至少一个子任务被阻断 |
| `needs_asset_match` | 触发了资产检索，但没有匹配到资产 |
| `needs_precise_native_source` | 匹配到了资产，但缺精确 native source |
| `not_asset_reuse_request` | 没有资产信号，普通绘图系统继续处理 |
| `asset_reuse_workflow_completed` | 所有 ready 子任务真实写入并读回 |
| `asset_reuse_workflow_partial` | 部分写入或仍有 blocked task |

多资产请求不得因一个资产不完整而退回临场重画全部内容。正确行为是保留 ready 资产的复用计划，同时把缺失资产的阻断原因返回给主系统，让主系统决定是补沉淀、让用户确认、还是临时绘制并标注为未沉淀。

## 沙发例子

用户说“沉淀沙发 A 资产”时，默认进入：

```text
libraries/system_library/furniture/seating/sofas/
  assets.json
  sofa_assets.dwg
```

用户以后说“沉淀沙发 B 资产”，仍进入同一个包，更新同一个 `assets.json` 和 `sofa_assets.dwg`，并按资产 ID、尺寸、用途和证据 refs 建索引。只有用户要求另建库或类型确实不同，才创建新分类。

如果沙发 B 复用了沙发 A 的 asset id，但尺寸或 blockName 明显不同，必须按冲突策略处理：

- `update_existing`：作为同一资产修订，记录历史。
- `reject`：拒绝覆盖，要求用户明确。
- `new_variant`：生成 `_v2` 等变体 ID，并记录 `derivedFromAssetId`。

## 当前边界

当前实现 `scripts/sediment_system_asset.py` 的登记入口只写仓库契约和索引，不连接 AutoCAD，不保存 DWG，不修改正式图层，也不删除实体。`--verify` 会检查合同、索引、状态、检索、排版计划、版本、反馈、来源边界、防污染字段，以及更强声明所需的可见 native 证据和复用 workflow / replay 证据；缺证据时应 fail 或保留 `notChecked`。真实 CAD 原生导出、block 定义写入、DWG 排版、保存、打开和截图验收由 CAD-native 步骤接入同一协议。“沉淀 XX 资产”已经授权这些步骤作用于对应系统资产 DWG，但不授权保存用户当前业务 DWG 或覆盖非系统资产文件。
