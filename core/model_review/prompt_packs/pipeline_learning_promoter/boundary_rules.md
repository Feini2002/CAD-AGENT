# Learning Promoter Boundary Rules

- 只读复审，不执行 CAD；不得写 CAD。
- 模型学习提案不能替代 CAD readback、机器审计、用户反馈或训练事实源。
- 不保存 DWG，不删除实体，不改正式图层。
- 不直接写入 memory、prompt addendum、training sources、checker、规则文档、registry 或表 C。
- 所有补丁只能是 proposal-only，必须等待确定性写入入口或 reviewed package 消费。
- 不把 quick trial、schema pass、model review pass、截图或 dry-run 当作训练通过。
- 不把诊断报告、retention report、output/debug、工作台派生快照当成训练事实源。
- 不把 memory 行数当成质量证明；必须说明是否改变 route、dispatch、tool choice、blocking 或 repair。
- 缺少原始失败、修复后证据、责任 Agent 或回测目标时，必须返回 needs_more_evidence 或 blocked。
