# Core Context Brief

最后更新：2026-05-26

本文是后续 Codex 开发本仓库时的稳定短上下文入口。默认先读 `AGENTS.md`，再读本文；只有执行具体 phase、完整复盘、排查失败、修改规则或同步状态时，才展开详细文档。

## 当前结论

本仓库是通用 CAD Agent Core Lab，不绑定某张 DWG、某套家装图纸或某台电脑。

当前状态：

- Phase O-V 非 CAD 主线已完成，系统层安全补强和自检已完成。
- `docs/architecture/shell-layout-foundation-design.md` 的核心思路已合并进主计划，并落地到 blank-shell pipeline 的 Phase P-V。
- 最新基线记录为 227 tests OK，repo audit 0 findings，blank-shell 4 场景 benchmark pass，office alpha benchmark 4 cases pass，interior delivery benchmark 3 persona composition cases pass；此外，interior delivery 的 3 个 persona composition cases 已补跑真实 AutoCAD batch check，结果为 3/3 `geometry_verified`。此前记录中 `self_check.py` pass、`render_preview.py --check` ready、`run_cad_validation.py --no-cad` pass 仍为最近稳定基线。
- Phase W 已执行到 W-16；W-07 真实 CAD 总验证已在用户会话下通过。最新 CAD 底座加固报告为 `output\validation_runs\manual-cad-after-primitive-probe\report.json`，顶层 `status=pass`；`readback_report.json.status=geometry_verified`，`cad_capability_probe.json.status=cad_capability_verified`，关键 checks 全部通过。能力矩阵已从矩形/文字/标注扩展到独立直线、圆、弧和闭合多段线；缩放后的截图证据为 `output\validation_runs\manual-primitive-cad-probe\cad-primitive-screen.png`。此前无法调用的根因是默认沙箱身份 `desktop-r40v31q\codexsandboxoffline` 看不到用户桌面的 AutoCAD 进程、窗口和 ROT/COM 活动对象；用户会话身份 `desktop-r40v31q\user` 下 COM 可用。本轮额外修复了总控只看顶层 pass 的误判风险，并让真实 CAD 回读优先按本轮 created handles 定向读取，避免在大 DWG 中扫描全 ModelSpace。2026-05-26 的 `R-CAD-VIEW-CAPTURE` baseline 已把总控截图升级为 AutoCAD 客户区窗口级截图，并在截图前按本轮 created handles bbox 缩放视图；最新证据为 `output\validation_runs\r-cad-view-cad\report.json` 和 `output\validation_runs\r-cad-view-cad\cad-validation-window.png`。
- 当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`；根目录没有独立 `plan.md`。用户提到 `PlanMD`、`plan.md` 或“主 plan”时，默认指这份文件。
- 主平台 Markdown 精细化拆分已执行：`CORE_RESTRUCTURE_PLAN.md` 已收缩为总控索引，Phase W/X/Y/Z 执行剧本已迁入 `docs/planning/`。
- 本轮二次收束已新增 `docs/README.md` 作为文档区总地图，并把 `docs/ROADMAP.md` 降级为兼容跳转；后续又补强 PlanMD 主线协议，明确 `docs/planning/phase-*.md` 是辅助执行剧本，避免旧阶段路线或多个带 plan 的文件和当前主线并存造成误读。
- Phase R 新鲜视角评审已启动并细化：多名只读专家 agent 从 CAD 执行、图块库、办公业务、平台架构和 benchmark 验证角度提出建议；记录在 `docs/reviews/fresh-eyes-review-2026-05-25.md`。执行入口已扩展为 `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`、`phase-r-rebirth-implementation-plan.md`、`phase-r-cad-capability-contract.md`、`phase-r-block-library-roadmap.md`、`phase-r-office-benchmark-cases.md`，并新增 `docs/governance/multi-agent-contribution.md` 与 `docs/onboarding/first-handoff.md`。当前已把 Phase R 代码切口落到 benchmark runner、composition engine 和真实 CAD batch runner：支持 `evidence_state`、`geometry_accuracy`、`screenshot_role`、`minimums`、`contains_object_types`、`contains_component_roles`、`contains_object_roles`、`object_spec` / `composition_spec` benchmark pipeline、suite/case 配置校验，以及 blank-shell / composition 每个 CAD_PLAN 的 dry-run / verification 汇总证据；新增 `examples/benchmarks/office_alpha_benchmark.json` 与 `examples/benchmarks/interior_delivery_benchmark.json`。后者模拟室内设计师 / 家庭设计者 / 办公布局者，覆盖卧室床+地毯、餐桌组合、办公桌组合，并输出 SVG 与浏览器 PNG 视觉辅助证据；最新真实 CAD 组合证据为 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition_cad_check_report.json` 和 `output\validation_runs\interior-composition-cad-label-clean-y8000\composition-cad-screen-clean-y8000.png`。
- 2026-05-26 已把下一轮开发建议写回主计划：`CORE_RESTRUCTURE_PLAN.md` 新增九个开发包和固定子校验顺序；其中 `R-CAD-VIEW-CAPTURE` baseline 已完成实现与真实 CAD 验证，避免全屏截图被 Codex 窗口遮挡；`R-CAD-CONTRACT` baseline 已把 capability probe / readback 报告固化为机器可读证据契约（`core/verification/evidence_contract.py`），并由 CAD validation runner 硬门禁校验 `evidence_state` / `geometry_accuracy` / `screenshot_role`；`R-BLOCK-METADATA` baseline 已把 `libraries/blocks/block_library.example.json` 升级为 `BLOCK_LIBRARY v0.2`，含受控 `controlled-test-block-001` 与 `object_spec_to_block_reference()`；`R-BLOCK-PLAN` baseline 已让 `insert_block_alpha` CAD_PLAN 通过 validate / dry-run / fake execute（`examples/plans/insert_block_alpha_test.json`）；`docs/planning/phase-r-rebirth-implementation-plan.md` 已记录文件级步骤、子校验命令、通过标准和执行证据。该变更不代表真实 CAD block insertion、office micro-scene、blank-shell 多候选或 Scene Alpha 已完成；截图仍不能替代 created handles 回读。

当前非 CAD blank-shell 链路：

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
-> VERIFICATION_REPORT(unverified)
```

## 不能声称的事

- 不能把 Phase W baseline、基础图元探针和 3 个室内组合案例的真实 CAD 几何通过扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN。
- 不能把截图或 `render_preview.py --check` 当作几何准确证据。
- 不能把 interior delivery 的 SVG/PNG 视觉辅助预览当作真实 CAD created-handle 几何回读证据；真实 CAD 结论必须看 `run_composition_cad_check.py` 的 created handles 回读报告。
- 不能默认保存、覆盖、删除或修改正式图层。
- 不能把场景 Agent 写成独立算法系统。
- 不能把 blank-shell pipeline 说成完整自动设计大脑。

## PlanMD 主从规则

- `PlanMD` 只是文档治理和开发排序入口，不改变通用 Core Lab、Core 优先、`CAD_PLAN` 中间层、真实 CAD 验证和场景轻量化方向。
- `CORE_RESTRUCTURE_PLAN.md` 决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。
- `docs/planning/phase-*.md` 只是执行剧本；可以写步骤和命令，但不能成为第二套主计划。
- `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 只写能力、证据、风险和当前状态，不写独立下一步。
- `CORE_ROADMAP.md`、`docs/README.md`、架构、治理、交接、验证、历史和 review 文档都服务 PlanMD。
- 如果辅助 MD 想新增待办或调整优先级，先同步到 `CORE_RESTRUCTURE_PLAN.md`。

## 交付进度格式

每次 CAD Agent 相关交付的最终回复都要附带粗估进度，固定写三项：

```text
总进度：约 xx%
Core 底座开发进度：约 xx%
Agent 多场景实现进度：约 xx%
```

当前估算口径见 `CAD_AGENT_RULES.md` 与 `CAD_AGENT_STATUS.md`；百分比只表示开发节奏，不替代真实 CAD 验证证据。

## 目标入口

| 目标 | 入口 | 先读 |
| --- | --- | --- |
| 真实 CAD 验证 / 换机验收 | Phase W、`scripts/run_cad_validation.py` | `docs/planning/phase-w-cad-validation-plan.md`、`CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md` |
| 场景 Agent Alpha 验收 | Phase X、`agents/*/preferences.json` | `docs/planning/phase-x-scene-agent-alpha-plan.md`、`agents/SCENE_AGENT_RULES.md` |
| blank-shell pipeline 硬化 | Phase Y、`core/workflows/blank_shell_pipeline.py` | `docs/planning/phase-y-blank-shell-hardening-plan.md`、`docs/architecture/shell-layout-foundation-design.md` |
| 文档和维护治理 | Phase Z、根目录 Markdown | `docs/planning/phase-z-doc-governance-plan.md` |
| 新鲜视角评审 / 重生式开发校准 | Phase R、多 agent 只读评审和执行拆单 | `docs/planning/phase-r-fresh-perspective-rebirth-plan.md`、`docs/planning/phase-r-rebirth-implementation-plan.md`、`docs/reviews/fresh-eyes-review-2026-05-25.md` |
| 卡壳、画不准、验证不了 | 自查闭环 | `CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_ISSUES.md` 相关条目 |

## 按需展开

| 文件 | 什么时候读 | 说明 |
| --- | --- | --- |
| `README.md` | clone、换机、首次接手、需要入口说明时 | 用户向入口，不作为每轮默认全文上下文 |
| `docs/README.md` | 需要理解文档区分层时 | `docs/` 导航和目录职责 |
| `CORE_STATUS.md` | 判断能力成熟度、找模块状态时 | 能力矩阵 |
| `CORE_ROADMAP.md` | 对齐长期路线时 | 高层路线图 |
| `CORE_RESTRUCTURE_PLAN.md` | 执行或修改 PlanMD 时 | 唯一开发主线和当前主 plan |
| `CAD_AGENT_STATUS.md` | 汇报当前进展时 | 当前状态页 |
| `CAD_AGENT_RULES.md` | 改规则或做 CAD 行为判断时 | 长期规则 |
| `CAD_AGENT_BLOCKER_PLAYBOOK.md` | 卡壳、画不准、环境不通时 | 排障流程 |
| `CAD_AGENT_AUTONOMOUS_VALIDATION.md` | 真实 CAD 验证、换机验收、Phase W | CAD 总验证手册 |
| `CAD_AGENT_CHANGELOG.md` | 追溯最近变更原因时 | 历史流水 |
| `CAD_AGENT_ISSUES.md` | 遇到失败、回归或奇怪现象时 | 问题与教训库 |
| `docs/architecture/shell-layout-foundation-design.md` | 空壳布局设计边界或 Phase Y | 架构设计与落地映射 |
| `docs/history/core-platform-md-split-plan-2026-05-25.md` | 追溯根目录主平台 Markdown 拆分时 | 已执行的主平台 MD 精细化拆分记录 |
| `docs/history/shell-layout-time-estimate.md` | 追溯早期时间预期时 | 历史估算，不作为当前计划 |
| `docs/planning/phase-r-fresh-perspective-rebirth-plan.md` | 执行 Phase R 时 | 新鲜视角评审与重生式开发计划 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 执行 Phase R 拆单时 | Phase R R0-R5 执行总表和证据状态 |
| `docs/planning/phase-r-cad-capability-contract.md` | 执行 CAD 能力契约或 block insertion alpha 前 | 基础实体 write-read-verify 和 block alpha 门禁 |
| `docs/planning/phase-r-block-library-roadmap.md` | 执行图块库、OBJECT_SPEC 或制图标准前 | 图块库字段、制图标准和受控测试块路线 |
| `docs/planning/phase-r-office-benchmark-cases.md` | 执行办公基础闭环 Alpha 前 | 办公对象、微场景、场景和失败 benchmark |
| `docs/governance/multi-agent-contribution.md` | 多 agent 并行协作或分工前 | 可写边界、审查门禁和冲突处理 |
| `docs/onboarding/first-handoff.md` | 新 agent / 新开发者首次接手时 | 最短阅读路径和不可声称边界 |
| `docs/planning/phase-w-cad-validation-plan.md` | 执行 Phase W 时 | 真实 CAD 回读闭环剧本 |
| `docs/planning/phase-x-scene-agent-alpha-plan.md` | 执行 Phase X 时 | 场景 Agent Alpha 验收剧本 |
| `docs/planning/phase-y-blank-shell-hardening-plan.md` | 执行 Phase Y 时 | blank-shell pipeline 硬化剧本 |
| `docs/planning/phase-z-doc-governance-plan.md` | 执行 Phase Z 时 | 文档治理与回归基线剧本 |
| `docs/reviews/fresh-eyes-review-2026-05-25.md` | 追溯本轮多 agent 新鲜视角建议时 | 只读专家评审纪要 |

## 固定边界

- 通用能力进入 `core/`。
- 场景差异进入 `agents/<scenario>/`。
- 跨场景资源进入 `libraries/`。
- 真实或样例项目资料进入 `projects/`。
- 旧命令兼容包装器保留在 `scripts/` 和 `drivers/`。
- 生成证据进入 `output/` 或 `docs/verification/`，不要默认提交。

## 安全门

真实 CAD 相关任务默认只允许：

- 绘制到 `CODEX_PREVIEW`。
- 不保存当前 DWG。
- 不覆盖原始 DWG。
- 不删除实体。
- 不修改正式图层，除非用户明确批准。

自然语言需求必须先变成 `CAD_PLAN` 或明确结构化绘图意图，再执行 validate、dry-run 和绘制。

声称“画准了”之前必须有证据：

- 预期对象、尺寸、基点、图层、文字、标注和允许误差。
- `scripts/validate_plan.py` 结果。
- `scripts/dry_run_plan.py` 结果。
- `CODEX_PREVIEW` 实际输出。
- 截图只能作为视觉辅助；几何准确必须有 created handles 范围内的实体回读和 `geometry_verified` 证据。
- 实际输出与 `CAD_PLAN` 或结构化意图的对比。

## 常用验证

优先使用 CAD-MCP 虚拟环境 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

非 CAD 基线：

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\blank_shell_manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_manual
& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\interior_delivery_manual
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad
```

真实 CAD 验证：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
& $py scripts\run_composition_cad_check.py --benchmark-output-root output\test_artifacts\benchmarks\interior_delivery_manual --output-dir output\validation_runs\interior-composition-cad-check --start-x 26000 --start-y 8000 --spacing-x 4200
```

文档自查：

```powershell
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|随[便]|先占[位]" README.md CORE_CONTEXT_BRIEF.md CORE_STATUS.md CORE_ROADMAP.md CORE_RESTRUCTURE_PLAN.md CAD_AGENT_STATUS.md docs
rg -n "CORE_CONTEXT_BRIEF|按需展开|run_cad_validation|run_blank_shell_pipeline|phase-r-rebirth|multi-agent-contribution|first-handoff|docs/README" README.md CORE_CONTEXT_BRIEF.md CORE_RESTRUCTURE_PLAN.md CAD_AGENT_RULES.md CAD_AGENT_STATUS.md docs
```

## 缓存友好约定

- 本文只写短摘要，不写长历史。
- 大段历史进入 `CAD_AGENT_CHANGELOG.md`。
- 失败教训进入 `CAD_AGENT_ISSUES.md`。
- 单一 PlanMD / 主计划进入 `CORE_RESTRUCTURE_PLAN.md`。
- 能力成熟度进入 `CORE_STATUS.md`。
