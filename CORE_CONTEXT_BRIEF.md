# Core Context Brief

最后更新：2026-05-25

本文是后续 Codex 开发本仓库时的稳定短上下文入口。目标是提高开发时的上下文缓存命中率：先读这份短入口，再按任务读取详细文档，不要每次把计划、变更流水和历史问题全文塞进上下文。

## 使用规则

默认读取顺序：

1. 先读 `AGENTS.md`。
2. 再读本文 `CORE_CONTEXT_BRIEF.md`。
3. 根据本文件的“按需展开”表，只读取当前任务需要的详细文件。

维护原则：

- 本文件保持短、稳定、可扫读，不写长篇历史。
- 只在当前阶段、入口命令、阻塞状态或上下文读取规则变化时更新。
- 详细计划仍写在 `CORE_RESTRUCTURE_PLAN.md`。
- 历史变更仍写在 `CAD_AGENT_CHANGELOG.md`。
- 失败教训仍写在 `CAD_AGENT_ISSUES.md`。
- 生成输出、日志、截图、benchmark artifact 和 CAD 验证报告默认不读全文，只读 summary 或指定 report。

## 当前结论

本仓库是通用 CAD Agent Core Lab，不绑定某张 DWG、某套家装图纸或某台电脑。

当前状态：

- Phase O 到 Phase V 的非 CAD 主线已完成到原型闭环。
- 当前单元测试基线记录为 `196 tests OK`。
- 最近复验时间为 2026-05-25 17:19：`self_check.py` pass，`render_preview.py --check` ready，repo audit 0 findings，blank-shell pipeline ok，4 场景 blank-shell benchmark pass，`run_cad_validation.py --no-cad` pass。真实 CAD 验证本轮未运行。
- `workflow.blank_shell_pipeline` 已登记到 capability registry。
- 非 CAD blank-shell pipeline 已能串联：

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

当前不能声称的事：

- 不能声称真实 CAD 几何已经准确验证。
- 不能把截图当作几何准确证据。
- 不能默认保存、覆盖、删除或修改正式图层。
- 不能把场景 Agent 写成独立算法系统。

当前主要瓶颈：

- `execute_plan`、截图和实体回读都有入口，但真实 AutoCAD readback 闭环仍需 Phase W 补验。
- 设计推理仍是 prototype，能跑通候选和解释，不等同完整自动设计大脑。
- 场景 Agent 已有 preferences，但 Phase X 的多场景 Alpha 验收仍未完成。

## 下一步路线

优先路线按任务选择：

| 目标 | 入口 | 先读 |
| --- | --- | --- |
| 真实 CAD 验证 / 换机验收 | Phase W、`scripts/run_cad_validation.py` | `CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md` |
| 场景 Agent Alpha 验收 | Phase X、`agents/*/preferences.json` | `CORE_RESTRUCTURE_PLAN.md` 的 Phase X、`agents/SCENE_AGENT_RULES.md` |
| 非 CAD pipeline 继续深化 | `core/workflows/blank_shell_pipeline.py` | `CORE_STATUS.md`、Phase V 相关测试 |
| schema / 模型合约 | `core/schemas/`、`core/model_loop/` | `CORE_STATUS.md`、相关 schema 和测试 |
| 对象 / 布局 / 方案算法 | `core/object_engine/`、`core/layout_engine/`、`core/proposal_engine/` | `CORE_STATUS.md`、对应测试文件 |
| 卡壳、画不准、验证不了 | 自查闭环 | `CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_ISSUES.md` 相关条目 |

## 按需展开

| 文件 | 什么时候读 | 说明 |
| --- | --- | --- |
| `README.md` | clone、换机、首次接手、需要完整入口说明时 | 用户向入口，不作为每轮开发默认全文上下文 |
| `CORE_STATUS.md` | 判断能力成熟度、找模块状态时 | 能力矩阵，优先读相关模块行 |
| `CORE_ROADMAP.md` | 对齐长期阶段时 | 路线图，低频读取 |
| `CORE_RESTRUCTURE_PLAN.md` | 执行某个 Phase 或改计划时 | 大计划，默认只读目标 Phase |
| `CAD_AGENT_STATUS.md` | 汇报当前进展或同步状态时 | 当前状态与已验证命令 |
| `CAD_AGENT_RULES.md` | 改规则、做 CAD 行为判断时 | 长期规则 |
| `CAD_AGENT_BLOCKER_PLAYBOOK.md` | 卡壳、画不准、环境不通时 | 排障流程 |
| `CAD_AGENT_CHANGELOG.md` | 需要追溯最近变更原因时 | 历史流水，默认读最近小节 |
| `CAD_AGENT_ISSUES.md` | 遇到失败、回归或奇怪现象时 | 历史坑点，按关键词读 |

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
- 截图或实体回读。
- 实际输出与 `CAD_PLAN` 或结构化意图的对比。

## 常用验证

优先使用 CAD-MCP 虚拟环境 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

文档或规则改动后的轻量自检：

```powershell
rg -n "CORE_CONTEXT_BRIEF|先读|按需" AGENTS.md README.md CAD_AGENT_RULES.md CAD_AGENT_STATUS.md
rg -n "TB[D]|TO[D]O|以后再[说]|随[便]|先占[位]" CORE_CONTEXT_BRIEF.md AGENTS.md README.md CAD_AGENT_RULES.md CAD_AGENT_STATUS.md
```

非 CAD 基线：

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\hardening-polish
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\hardening-polish
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad
```

真实 CAD 验证：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
```

## 缓存友好约定

- `CORE_CONTEXT_BRIEF.md` 的章节顺序尽量稳定。
- 大段历史不要搬进本文。
- 新增阶段进展时优先改“当前结论”和“下一步路线”，不要重写全文。
- 大文件前半部分尽量少改；新增细节追加到对应小节或详细文档。
- Codex 状态汇报默认引用本文摘要，再按需引用详细文件。
