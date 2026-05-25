# CAD Agent 自主 CAD 验证执行手册

最后更新：2026-05-25

本文用于约束 Codex 在真实 CAD 环境中做验证时的行为。目标是减少“跑一步、卡一步、问一次”的低效循环，让 Codex 能自己完成可修问题的诊断、修复和复验。

## 给 Codex 的启动语

你可以直接复制下面这句给 Codex：

```text
读取 CAD_AGENT_AUTONOMOUS_VALIDATION.md，运行 scripts/run_cad_validation.py 做 CAD 层面验证；不要遇到第一个失败就停。若 report.status 不是 pass，按报告和本文分类继续处理：仓库内问题自己最小修复并复验，直到完整通过，或报告只剩 external_blocker 并列出需要我手动处理的事项。
```

## 一键命令

在仓库根目录执行。`$py` 必须指向 CAD-MCP 的虚拟环境 Python。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"

& $py scripts\run_cad_validation.py
```

只跑非 CAD 探针时：

```powershell
& $py scripts\run_cad_validation.py --no-cad
```

指定输出目录时：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
```

## 输出位置

脚本会写入：

```text
output/validation_runs/<timestamp>/
  report.json
  report.md
  *.stdout.txt
  *.stderr.txt
  execution_summary.json
  readback_report.json
  cad_capability_probe.json
  cad-validation-screen.png
```

`report.json.status` 只有三类顶层结论：

| status | 含义 | Codex 下一步 |
| --- | --- | --- |
| `pass` | 当前验证闭环通过 | 可以继续执行计划下一阶段 |
| `external_blocker` | 剩余失败依赖用户环境、CAD 窗口、授权、截图权限或缺依赖 | 停下来列出用户要处理的事项 |
| `fail` | 仓库代码、计划、dry-run、执行器或回读逻辑仍有可修问题 | Codex 必须最小复现、最小修复、重新运行脚本 |

## Codex 不得停在第一处失败

除非触发“必须问用户”的条件，Codex 必须继续做下面动作：

1. 读取 `report.json` 和失败步骤的 `stderr/stdout`。
2. 按 `failure_category` 分类。
3. 对仓库内可修问题新增或补充最小测试。
4. 做最小代码修复。
5. 重新运行相关测试。
6. 重新运行 `scripts/run_cad_validation.py`。
7. 更新 `CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`；如果是失败教训，还要更新 `CAD_AGENT_ISSUES.md`。

## 失败分类

| failure_category | 含义 | 默认处理 |
| --- | --- | --- |
| `missing_dependency` | CAD-MCP Python 缺 Pillow、pywin32 或 win32gui | 停下来要求用户补依赖，或在用户授权后安装 |
| `cad_connection_failed` | AutoCAD 未打开、无活动 DWG、授权弹窗或 COM 不通 | 停下来要求用户处理 CAD 环境 |
| `repo_regression` | 单测、自检或 benchmark 失败 | Codex 自己修仓库代码并复验 |
| `cad_plan_invalid` | baseline CAD_PLAN 校验失败 | Codex 自己修 schema / plan 生成 / 示例 |
| `dry_run_failed` | dry-run 失败或与计划不一致 | Codex 自己定位 plan_engine 或 CAD_PLAN |
| `execution_failed` | `execute_plan.py` 无法落图 | Codex 自己检查执行器、driver、安全策略；环境阻塞才问用户 |
| `screenshot_failed` | 截图能力或落盘失败 | 先判断是环境权限还是脚本问题；脚本问题自己修 |
| `readback_failed` | 实体回读或验证报告失败 | Codex 自己检查 `inspect_dwg.py`、created handles、readback scope |
| `cad_capability_failed` | CAD COM 能力探针失败 | Codex 自己检查 driver primitive write、handle readback、实体标准化和安全层约束 |

## 必须问用户的情况

只有下面情况才停下来问用户：

- 需要安装或修复 AutoCAD、CAD-MCP、Python 包、IDE/MCP 配置。
- AutoCAD 授权、弹窗、当前活动 DWG、窗口可见性需要用户处理。
- 需要保存 DWG、覆盖原图、删除实体或修改正式图层。
- 需要选择真实项目图纸、真实公司块库或业务语义。
- 已经完成最小复现，但缺少用户侧项目信息。

## 不需要问用户的情况

下面情况默认由 Codex 自己处理：

- 单元测试失败。
- schema/example 不一致。
- `scripts/*.py` 包装器导入路径错误。
- `CAD_PLAN` 示例或 plan_engine 生成错误。
- dry-run 报告结构错误。
- verification report 状态升级逻辑错误。
- readback JSON 解析、created handles、截图路径判断等仓库逻辑错误。

## 安全边界

自主验证不等于允许高风险 CAD 操作：

- 默认只允许 `CODEX_PREVIEW`。
- 不保存 DWG。
- 不覆盖原始 DWG。
- 不删除实体。
- 不修改正式图层。
- 未确认方案不得执行。

如果需要突破以上任何一条，必须明确向用户请求批准。

## 推荐工作方式

```text
run_cad_validation.py
-> 读 report.json
-> 分类 failure_category
-> 仓库内问题：写最小测试 -> 修复 -> 跑相关测试 -> 重跑总验证
-> 外部环境问题：停止并给用户清单
```

最终回复必须包含：

- `report.json` 路径。
- 顶层 `status`。
- `readback_report.json.status` 与关键 checks。
- `cad_capability_probe.json.status` 与能力矩阵 checks。
- 失败步骤和分类。
- 已自动修复的内容。
- 仍需用户处理的外部事项。

