# 训练反馈记录

案例 id：`residential_training_template`（复制后改成你的 id）

## §理解（白话是否听懂）

| 轮次 | 日期 | 你的原话摘要 | Agent 理解 | 问题 | 已改 rules? |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |

## §计划（CAD_PLAN 是否对上）

| 轮次 | validate | dry-run | 和你的预期差在哪 | 处理 |
| --- | --- | --- | --- | --- |
| 1 | | | | |

## §几何（预览图是否对上）

| 轮次 | 你判定 | 不准点（房间/对象/尺寸） | handles/证据路径 |
| --- | --- | --- | --- |
| 1 | pending / pass / fail | | `runs/` |

## §用户指出的错因（你的原话，Agent 只整理不篡改）

| 轮次 | 日期 | 你的原话 / 不准点 | 附件 |
| --- | --- | --- | --- |
| 1 | | | `runs/roundN_preview.png` |

## §Agent 根因与修复（fail 后 Agent 填写）

| 轮次 | 根因（含证据路径） | 修复步骤 | 判因类型 |
| --- | --- | --- | --- |
| 1 | | | `链路` / `几何` / `环境` / `需求` |

- **链路** 类：同步 `docs/training/pipeline-changelog.md`
- **几何** 类：同步根目录 `TRAINING_ERRORS.md` + 视情况改 `agents/<scenario>/rules.md`

## 案例结论

- [ ] 三步均 pass，可标 **done**
- [ ] 仍需下一轮（写 next 动作一行）

**next：**
