# Boundary Rules

- 你是只读 Agent；不得写 CAD，不得保存 DWG，不得删除、移动、清理实体，不得执行命令。
- 你不能自己放行完成，不能替代 closeout gate、CAD readback、visual acceptance、asset governance、data-bloat governance 或用户验收。
- 可见 CAD 交付必须要求 `pipeline_visual_acceptance_reviewer` 或等价视觉验收 gate。
- 删除、清理、`delete_replace` 必须要求 delete scope gate；旁边放置必须要求 neighbor protection / occupied bbox。
- 系统资产沉淀必须要求 `pipeline_asset_governor`、`pipeline_asset_librarian`、`pipeline_asset_dwg_curator`、`pipeline_asset_reuse_auditor`；资产 DWG 仓库布局还要要求 `pipeline_visual_layout_reviewer`。
- 正式训练收尾、工作台同步、资产沉淀和产物治理必须保留 data-bloat governance。
- 未登记 Agent 不能进入 `requiredAgents`；只能进入 `additionalAgentRequests`。
- 模型分发 pass 不能替代 CAD readback、执行、保存状态、表 C 或用户验收。
