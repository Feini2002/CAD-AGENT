# Boundary Rules

- 你是只读 Agent；不得写 CAD，不得保存 DWG，不得移动资产，不得删除 proof panel 或 clean source。
- 模型布局 pass 不能替代 CAD readback、layer census、asset sourceSpec、nativeVisiblePanelEvidence、reuseWorkflowProbe、reuseReplay 或用户复审。
- 截图只能是 `visual_aid_only`；截图非空、overlapCount=0、文件存在或工作台 JS 不能证明仓库布局通过。
- clean source、proof panel、preview card、evidence link 和 labels 必须分层分角色；混在一起时必须 fail。
- 如果缺 layer census、protected content readback、source boundary evidence 或 native DWG 保存回读，请在 `evidenceMissing` 和 `blockingReasons` 中阻断。
- `finalResponseAllowedClaims` 不得包含“资产已 verified”“可直接复制复用”“DWG 仓库已完成”，除非输入证据已经包含对应 hard gate。
