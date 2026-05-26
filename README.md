# CAD Agent Core Lab

## 系统简介

CAD Agent Core Lab 是一个可迁移的通用 CAD Agent 开发包，用结构化 `CAD_PLAN` 连接自然语言需求、设计模型、CAD 执行和可验证结果。它不绑定某一张 DWG、某一套家装图纸或某一台电脑，也不把工装、家装、办公等场景写成彼此割裂的独立系统。

核心方向是：

- `core/` 沉淀通用能力：读图、模型、对象、风格、布局、计划、执行、验证和安全边界。
- `agents/<scenario>/` 只保留轻量场景差异，复用 Core，不复制 Core 算法。
- `libraries/` 存放跨场景资源，例如对象默认值、块库、风格、材料、尺寸和图层标准。
- `projects/` 存放真实或样例项目资料。
- `docs/` 存放架构、计划、治理、交接、验证、决策和历史记录；Cursor 按包交付见 [`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`](docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md)。

仓库的绘图原则是先把白话需求转成 `CAD_PLAN` 或更高层结构化意图，再做校验、dry-run、执行和回读验证。真实 CAD 输出默认只落到 `CODEX_PREVIEW`，不默认保存 DWG，不覆盖原始文件，不删除已有实体，不修改正式图层。

## 开发状况

当前仓库已经完成 Phase O-V 非 CAD 主线、系统层安全补强，以及 blank-shell pipeline 的第一轮落地。主链路已经跑通：

```text
SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> placements
-> LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> dry-run
-> VERIFICATION_REPORT
```

最新稳定结论：

- 当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。
- `CORE_CONTEXT_BRIEF.md` 是日常恢复上下文的短入口。
- `docs/planning/phase-*.md` 是 Phase 执行剧本，不是第二套主计划；后置 Backlog 和未来小包只看 `CORE_RESTRUCTURE_PLAN.md`。
- 最新全量回归为 `456 tests OK`，repo audit 0 findings；blank-shell、office alpha、interior delivery、project sample、proposal confirmed、CAD beta rollup 和 scene beta benchmark 均已有可重复运行证据。
- `core.plan_engine`、benchmark runner、composition engine、CAD validation runner、本地 CAD regression runner 已进入可运行原型状态。
- `scripts/run_local_cad_regression.py --no-cad` 已能汇总 baseline CAD validation、project sample CAD check 和 interior composition CAD check，输出 deferred / strict gate 证据；当前 no-CAD 矩阵不等于真实 CAD 几何通过。
- 真实 CAD 验证已覆盖 baseline、基础图元能力探针、受控 block alpha 和 3 个简单 interior composition cases，并取得有限 `geometry_verified` 证据。
- 按用户要求，`CORE_RESTRUCTURE_PLAN.md` 已新增“本地真实 CAD 校验扩样主线”，拆为 `LCAD-01` 到 `LCAD-11` 小任务包。

仍需注意：这些验证不能扩大解释为真实项目图纸、公司块库、属性块、hatch 或任意 `CAD_PLAN` 都已经准确。当前系统是 Core Alpha 原型，不是完整自动设计大脑；真实 CAD 几何准确仍只看 created handles 定向回读、`geometry_verified` 和关键 checks。

## 交付进度规则

后续每次 CAD Agent 相关交付，最终回复都必须附带一组粗估开发进度，用于判断当前产品和工程节奏。固定三项为：

```text
总进度：约 xx%
Core 底座开发进度：约 xx%
Agent 多场景实现进度：约 xx%
```

默认权重口径沿用 `CAD_AGENT_RULES.md`：`总进度 = Core 底座开发进度 * 70% + Agent 多场景实现进度 * 30%`。百分比是 5-10 个百分点误差范围内的主观工程估算，不替代真实验证证据；涉及 CAD 几何准确时，仍必须以 created handles 回读、`geometry_verified` 和关键 checks 为准。

## 下一步计划

近期开发继续围绕 `CORE_RESTRUCTURE_PLAN.md` 推进。当前用户指定的默认优先级是补齐“大量本地真实 CAD 校验层”：

1. 先做 `LCAD-01-REGRESSION-MANIFEST`、`LCAD-02-STRICT-MATRIX-RUNNER`、`LCAD-03-ACTIVE-DOCUMENT-GUARD`，把本地真实 CAD regression manifest、strict runner 和 ActiveDocument / `CODEX_PREVIEW` 安全守卫搭稳。
2. 再做 `LCAD-04` 到 `LCAD-06`，扩大 baseline smoke、基础实体矩阵和 `CAD_PLAN` fixture suite。
3. 然后做 `LCAD-07` 到 `LCAD-09`，覆盖 block / attribute / hatch、project sample 真实 CAD smoke 和多场景 composition 真实 CAD smoke。
4. 最后做 `LCAD-10` 和 `LCAD-11`，补负向安全 suite、趋势 rollup 和证据审计。
5. 继续保持 README 只做入口说明；详细状态、计划、规则、交接和历史分别进入 `CORE_CONTEXT_BRIEF.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_RULES.md`、`docs/handoffs/` 和 `CAD_AGENT_CHANGELOG.md`。
