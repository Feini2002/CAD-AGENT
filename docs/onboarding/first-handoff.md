# First Handoff

状态：新人接手入口已同步到 DOC-ARCH-REBASE
最后同步：2026-05-28

> 给第一次接手本仓库的 Codex / agent / 开发者。目标是 5-10 分钟内知道当前系统到哪了、从哪开始、不能说什么。

## 最短阅读路径

1. `AGENTS.md`：强制行为规则、安全边界、默认中文输出。
2. `CORE_CONTEXT_BRIEF.md`：稳定短上下文入口。
3. `README.md`：项目定位和入口说明。
4. `CORE_RESTRUCTURE_PLAN.md`：唯一 `PlanMD`。
5. `docs/planning/任务清单.md` §0：三指令执行台账和当前 `next`。
6. `CORE_STATUS.md`：能力状态和表 C 解释；机器值以 coverage JSON 为准。
7. `docs/status/current.md`：当前状态快照。
8. `docs/handoffs/current.md` + `docs/handoffs/package-index.md`：最近包交接和全量索引。

## 当前一句话

当前仓库是通用 CAD Agent Core Lab：Core、benchmark、能力登记表、真实 CAD 验证入口和文档治理都已建立。表 C 数值不要从本文硬读，必须以 `CORE_CONTEXT_BRIEF.md` 和 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。

## 不能声称

- 不能说任意 `CAD_PLAN`、真实项目图纸、真实块库或块插入都已准确。
- 不能说截图、dry-run 或 no-CAD benchmark 证明几何准确。
- 不能把表 A 工程进度、表 B 台账完成度或 RCAD 烟囱完成度当成表 C 真实 CAD 实力。
- 不能默认保存、覆盖、删除 DWG 或修改正式图层。
- 不能把场景 Agent 写成独立算法系统；场景差异必须复用 Core。
- `Scene Alpha` 只证明轻量偏好层、`benchmark_pass_non_cad` 和解释模板边界；`docs/verification/scene_alpha_explanation_template.md` 不代表 `geometry_verified`。

## 当前文档架构

| 需要 | 入口 |
| --- | --- |
| 当前状态 | `docs/status/current.md` |
| 历史流水 | `docs/status/changelog.md` |
| 风险教训 | `docs/status/issues.md` |
| 交接窗口 | `docs/handoffs/current.md` |
| 交接归档 | `docs/handoffs/archive/` |
| CAD 验证 runbook | `docs/runbooks/cad-validation.md` |
| 卡壳流程 | `docs/runbooks/blocker-playbook.md` |
| 文档治理检查 | `scripts/run_doc_governance_audit.py` |

## 第一天可以做的 3 件事

| 任务 | 做法 | 验证 |
| --- | --- | --- |
| 恢复上下文 | 读 `AGENTS.md` + `CORE_CONTEXT_BRIEF.md` + 当前任务入口 | 不改代码 |
| 审一个包 | 从 `docs/handoffs/package-index.md` 找包，再核对机器证据 | 不用摘要替代 JSON |
| 做文档自查 | 跑 doc governance audit | `& $py scripts\run_doc_governance_audit.py` |

## 开始开发前

- 是否需要真实 CAD；需要时默认只写 `CODEX_PREVIEW`。
- 是否涉及保存、覆盖、删除或正式图层；涉及则必须有用户明确批准。
- 是否有测试 / benchmark / doc governance 检查可先跑。
- 完成后是否需要同步 `docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md` 和 `docs/handoffs/current.md`。
