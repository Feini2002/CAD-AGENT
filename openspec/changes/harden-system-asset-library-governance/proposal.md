## Why

系统资产 DWG 当前容易退化成训练画布的搬运结果：训练标题、临时说明、边框或复审文字可能跟可复用资产混在一起，长期会削弱检索、复用和人工复审的意义。

本变更把“沉淀资产”升级为有守门员的系统资产库治理流程：先判断能否进库，再清洗、分区、排版、审计和登记证据，避免把未清洗训练内容当作通用底座资产。

## What Changes

- 新增资产库守门员 `pipeline_asset_governor`，作为“沉淀 / 通用资产 / 收进资产库”的默认全局入口。
- 新增三个资产治理子角色：`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`。
- 升级系统资产沉淀协议，明确系统资产 DWG 不是训练画布，应按目录区、干净资产区、资产卡片区、待复审区和证据索引区组织。
- 升级 `native.layoutPlan` 为可审计的分区 / 槽位 / bbox / 清洗策略 / 资产卡 / 复用源计划，而不是只记录简单行列。
- 增加机器可读的资产库治理决策：是否需要继续润色加固、是否需要派生子 Agent、是否允许写入 clean source、是否只能停在 quarantine / metadata_only。
- 保持现有证据边界：元数据、排版计划和 fake-driver 复用不等于真实 CAD 原生导出；真实 native DWG 写入、保存、截图和 created-handle 回读仍需单独证据。

## Capabilities

### New Capabilities

- `system-asset-library-governance`: 资产库守门员、DWG 排版治理、清洗门禁、复用审计和继续加固判断。

### Modified Capabilities

无。当前仓库没有稳定 `openspec/specs/`，系统资产沉淀协议升级作为新能力 `system-asset-library-governance` 的要求落地，并同步更新仓库文档与实现。

## Impact

- Agent 注册：`agents/pipeline/pipeline_manifest.json` 与新增 `agents/pipeline/asset_*` 角色定义。
- Core：`core/assets/system_asset_sedimentation.py`、`core/assets/__init__.py`，并新增资产库排版 / 治理辅助模块。
- CLI：`scripts/sediment_system_asset.py` 增加资产库治理报告输出；可新增独立自检脚本。
- 文档：系统资产沉淀协议、资产智能架构、训练 / Agent 流水线、状态与 handoff。
- 测试：新增资产库治理、layoutPlan v2、污染清洗、守门员决策和 CLI 验证测试。
- 非目标：本包不声明真实 CAD 原生 DWG 已重新排版完成；若没有执行真实 CAD 写入和回读，只能说治理规则与元数据 / fake-driver 自校验通过。
