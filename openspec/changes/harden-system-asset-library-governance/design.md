## Context

系统资产沉淀协议已经要求机器契约、原生 DWG 位置、工具和全局索引四件套，也已有 `native.layoutPlan`、来源边界和防污染字段。但当前 layout plan 只是简单 grid 行列，真实资产 DWG 仍可能像训练画布一样堆放内容，导致训练标题、临时说明和复审文字混入未来可复制源。

用户明确要求资产库具备“守门员”能力：主 Agent 能判断是否新增 / 派生子 Agent，并把这类治理规则写入全局架构。这个能力影响 Agent 注册、系统资产协议、Core 数据结构、CLI 验证和后续 CAD-native 写入门禁，因此需要 OpenSpec 契约。

## Goals / Non-Goals

**Goals:**

- 为系统资产沉淀新增 `pipeline_asset_governor` 守门入口。
- 允许守门员按规则派发 `pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor` 三类子角色。
- 将 `native.layoutPlan` 升级到 v2，包含 DWG 分区、槽位、bbox、清洗策略、资产卡片、可复制源和复用审计计划。
- 为“是否继续润色加固”提供机器可读判断，避免一次沉淀后直接声称资产库完全成熟。
- 保留现有 CAD 安全边界：系统资产 DWG 授权不扩展到当前业务 DWG；无真实 CAD 写入 / readback 时不声称 native 验证。

**Non-Goals:**

- 本包不重排所有历史系统资产 DWG。
- 本包不要求连接 AutoCAD 完成真实原生写入。
- 本包不提升表 C，不声明完整施工图能力。
- 本包不把 raw/reference 库直接晋升为 system_library。

## Decisions

1. **守门员作为全局 Agent，不作为 Core 类**

   `pipeline_asset_governor` 写在 `agents/pipeline/` 中，表达职责、输入、输出、门禁和可派生子 Agent。Core 只提供可测试的数据结构和函数。这样保持 `agents/` 不写 Python 的既有边界。

2. **layoutPlan v2 由 Core 生成**

   新增资产库 layout helper，生成稳定的五区模型：

   ```text
   00_INDEX
   01_CLEAN_ASSETS
   02_PREVIEW_CARDS
   03_REVIEW_QUARANTINE
   99_EVIDENCE_LINKS
   ```

   v2 plan 同时保留旧 `grid` 字段，降低 registry / 旧测试迁移风险。

3. **清洗策略默认保守**

   训练标题、说明、边框、尺寸线和证据文字默认进入 `excludedContentTypes`；只有精确来源、明确 included handles 或 style definition 才允许进入 clean source。来源不足时进入 quarantine 或 metadata_only。

4. **“继续润色加固”是决策，不是主观话术**

   守门报告输出 `polishHardeningDecision`：`complete_for_current_scope`、`needs_native_cad_relayout`、`needs_reuse_replay`、`needs_source_boundary_review`、`needs_agent_rule_review`。收尾时据此说明是否继续，不用“感觉差不多”。

5. **真实 CAD 和 fake-driver 分开**

   单元测试可验证 layout / registry / CLI / fake-driver 复用计划；真实 CAD 写入、保存、截图和回读仍是单独证据。若本轮不运行真实 CAD，最终必须说明 native CAD relayout 未执行。

6. **视觉仓库验收不能只看分区名，也不能只看 handles 数量**

   `visualRackPlan` 必须独立通过机器审计：`schemaVersion >= 2`、`layoutMode=classified_expandable_visual_warehouse_v2`、`warehouseArchitecture`、`acceptanceCriteria`、rack family ownership、copy policy、扩展空位和 zone bbox 比例都要成立。`scripts/run_asset_library_governance_check.py` 读取当前系统库 `nativeLayout.visualRackPlan` 后复用该审计；`scripts/layout_system_asset_shelves.py` 在写入系统资产 DWG 前先审 plan，写入后再回读本轮 created handles 的图层和 bbox。二次纠偏后，脚本还必须先回读非货架层上的保护资产内容 bbox，按内容簇布置 A1/A2，并在写入后运行 shelf/content clearance 审计；任何货架框线、标签、route 或 slot grid 与保护内容相交都不能 pass。这样完成态不再等同于“脚本能写 metadata / 创建了 handles”。

7. **几何不重叠不等于视觉可交付**

   `visualReadabilityAudit` 是 clearance 之外的硬门禁：A1/A2 和 A2/B 必须有可读通道，A1/A2 内容宽度占比不能过密，系统资产 proof content 不能继续留在 `CODEX_PREVIEW`，`ASSET_SOURCE_BOUNDARY` 只能作为小 source token，不能用大框包住 proof panel。A-to-A `pipeline_visual_layout_reviewer` 也必须输出同一组可读性字段；否则主 Agent 不能进入完成口吻。

## Risks / Trade-offs

- [Risk] 历史 `assets.json` 仍有旧 layout 字段 → 保留旧字段并追加 v2 字段，验证器接受兼容格式。
- [Risk] Agent 数量增加导致链路膨胀 → 守门员默认只派需要的子角色，且新增 Agent 必须受 reviewed package / OpenSpec 约束。
- [Risk] 误把训练说明删掉导致证据不可追溯 → 清洗只作用于可复制源区，证据引用进入 JSON 和 `99_EVIDENCE_LINKS`。
- [Risk] 用户以为本包已完成真实 DWG 重排 → 文档、验证报告和最终回复必须区分 `layoutPlan v2 checked` 与 `native CAD relayout not_run`。

## Migration Plan

1. 注册资产库守门员和三个子角色。
2. 新增 Core layout / governance helper，并接入沉淀合同生成。
3. 扩展 CLI 输出守门报告和 layoutPlan v2。
4. 更新系统资产协议、流水线文档、状态 / changelog / handoff。
5. 新增测试并运行 OpenSpec strict validate、资产沉淀单测、语义规则单测和脚本自检。
6. 对已写出的 `standard_assets.dwg` 追加真实 CAD 货架重排、protected content readback、created handles 回读、shelf/content clearance audit、截图和 governance check，保留“截图仅视觉辅助”的证据边界。

Rollback：保留旧 `grid` 字段，若 v2 逻辑出现问题，可暂时只忽略 `layoutPlanV2` 与 `libraryGovernance`，旧资产 registry 仍可读。

## Open Questions

- 是否后续对历史 `standard_assets.dwg` 做真实 CAD 原生重排，需在 AutoCAD 可用时开单独 CAD-native 包执行。
- 是否把守门员升级为真正多 Agent 调度器，取决于后续自动化框架，而非本包立即实现。
