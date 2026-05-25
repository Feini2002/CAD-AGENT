# First Handoff

状态：新人接手入口已建立  
最后同步：2026-05-26

> 给第一次接手本仓库的 Codex / agent / 开发者。目标是 5-10 分钟内知道当前系统到哪了、从哪开始、不能说什么。

## 最短阅读路径

1. `AGENTS.md`：强制行为规则、安全边界、默认中文输出。
2. `CORE_CONTEXT_BRIEF.md`：稳定短上下文入口。
3. `README.md` 的“Clone 后先看这里”。
4. `CORE_RESTRUCTURE_PLAN.md`：唯一 `PlanMD`，先确认当前活跃工作队列、优先级和退出标准。
5. 当前任务对应 Phase 的辅助执行剧本：
   - Phase R：先读 `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`，再按任务读 `docs/planning/phase-r-rebirth-implementation-plan.md`、`phase-r-cad-capability-contract.md`、`phase-r-block-library-roadmap.md` 或 `phase-r-office-benchmark-cases.md`
   - Phase W：`docs/planning/phase-w-cad-validation-plan.md`
   - Phase X：`docs/planning/phase-x-scene-agent-alpha-plan.md`
   - Phase Y：`docs/planning/phase-y-blank-shell-hardening-plan.md`
   - Phase Z：`docs/planning/phase-z-doc-governance-plan.md`
6. 需要判断能力成熟度时，再读 `CORE_STATUS.md` 和 `CAD_AGENT_STATUS.md`。

## 当前一句话

当前仓库是通用 CAD Agent Core Lab：非 CAD blank-shell pipeline 已跑通，Phase W baseline 真实 CAD readback 已通过，但不能扩大到真实项目图纸、真实块库、块插入或任意 CAD_PLAN 全量准确。

## 不能声称

- 不能说任意 CAD_PLAN、真实项目图纸、块库或块插入都已准确。
- 不能说截图、dry-run 或 no-CAD benchmark 证明几何准确。
- 不能说 blank-shell pipeline 是完整自动设计大脑。
- 不能说场景 Agent 已完成 Alpha。
- 不能默认保存、覆盖、删除 DWG 或修改正式图层。
- 不能把场景 Agent 写成独立算法系统。

## 第一天可以做的 3 件事

| 任务 | 做法 | 验证 |
| --- | --- | --- |
| 梳理一个 Phase | 读短入口和目标 Phase，列“入口、证据、不能声称、主计划归属” | 不改代码，只更新主计划或 review 文档 |
| 补一个小 benchmark 规格 | 例如 office desk / chair / computer desk 的 object 或 micro-scene case | 写 expected assertions 和 evidence_state |
| 做文档自查 | 扫描 Phase R、主计划、状态文档口径是否一致 | `rg` 引用扫描、占位词扫描、边界扫描 |

## 如果要开始代码开发

先确认：

- 是否需要真实 CAD；如果需要，默认只写 `CODEX_PREVIEW`。
- 是否涉及正式图层、保存、覆盖、删除；如果涉及，必须有用户明确批准。
- 是否属于 Core、libraries、agents、examples、projects 或 docs 的正确边界。
- 是否已有测试或 benchmark 可先写失败用例。
- 完成后是否能同步状态和 changelog。

## 主计划入口

后续优先级只以根目录 `CORE_RESTRUCTURE_PLAN.md` 这个唯一 PlanMD 为准。当前 Phase R 的执行参考入口：

- `docs/planning/phase-r-rebirth-implementation-plan.md`
- `docs/planning/phase-r-cad-capability-contract.md`
- `docs/planning/phase-r-block-library-roadmap.md`
- `docs/planning/phase-r-office-benchmark-cases.md`
- `docs/governance/multi-agent-contribution.md`
