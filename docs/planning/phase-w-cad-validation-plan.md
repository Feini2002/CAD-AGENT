# Phase W CAD Validation Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-26

> 本文是 Phase W 辅助执行剧本，不是独立 PlanMD。执行顺序、优先级和退出标准以根目录 `CORE_RESTRUCTURE_PLAN.md` 为准；执行前仍需先读 `AGENTS.md` 与 `CORE_CONTEXT_BRIEF.md`，并遵守 `CODEX_PREVIEW`、不保存、不覆盖、不删除、不改正式图层的 CAD 安全边界。

## Phase W：真实 CAD 回读闭环补验

目标：把 `CODEX_PREVIEW` 落图、截图、实体回读和 `VERIFICATION_REPORT.geometry_verified` 证据链真正闭合。

### W.0 已完成内容聚合与证据边界

Phase W 不是从零开发 CAD 验证工具，而是把已有入口组织成一次真实 CAD 验收剧本。

| 能力 / 组件 | 当前状态 | 已有证据入口 | 仍缺证据 | Phase W 要补什么 |
| --- | --- | --- | --- | --- |
| `scripts/run_cad_validation.py` | 已有 CAD 验证总控 | `--no-cad` 已通过；会写 `report.json` / `report.md` | 真实 CAD 全链路报告 | 生成并审查 `output\validation_runs\cad-readback-alpha\report.json` |
| `execute_plan.py` | 可执行 baseline plan 到 `CODEX_PREVIEW` | 单测、dry-run、无 CAD 总控 | 真实 AutoCAD 执行结果 | 审查 `execution_summary.json` 和 `created_handles` |
| `inspect_dwg.py` | 有 `--connect-cad`、`--execution-summary`、截图路径和 JSON report 入口 | fake readback 与无 CAD 报告壳 | 真实 ModelSpace 实体回读 | 生成并审查 `readback_report.json` |
| `render_preview.py` | `--check` ready，`--capture-autocad-window` 已存在 | 截图能力检查 | 真实 CAD 窗口截图 | 生成 `cad-validation-window.png` |
| `VERIFICATION_REPORT` | 已有 `unverified` / `executed_only` / `screenshot_captured` / `geometry_verified` 等状态 | 单测和 fake readback | 真实 readback 升级证据 | 只有证据满足门槛时才允许 `status=geometry_verified` |
| `scripts/run_cad_capability_probe.py` | CAD COM 能力矩阵探针 | 单测和真实 CAD 探针已通过 | 更复杂实体、块和选择集能力 | 验证活动文档、preview 图层、primitive write、handles、readback、bbox 和安全边界 |

硬边界：非 CAD 基线已经完成；Phase W baseline 真实 CAD 几何准确性已补验证据链；后续真实项目、块库和更多 CAD_PLAN 仍需单独补验。

### W.1 本阶段验证范围

本阶段只验证：

| 范围 | 说明 |
| --- | --- |
| baseline `CAD_PLAN` | 先以 `examples\plans\draw_test_cabinet.json` 做最小真实 CAD 验收，不扩大到真实业务图纸 |
| `CODEX_PREVIEW` | 所有落图只允许进入预览图层 |
| 执行摘要 | 必须检查 `target layer`、对象类型、尺寸、基点和 `created_handles` |
| 截图 | 只作为视觉辅助证据 |
| 实体回读 | 作为几何验证主证据 |
| 验证报告 | 必须解析 `readback_report.json.status` 和 `checks`，不能只看命令退出码 |

本阶段不验证：

| 不做 | 原因 |
| --- | --- |
| 不保存 DWG | 保护用户原图 |
| 不覆盖、删除实体或修改正式图层 | Phase W 是验证，不是正式改图 |
| 不验证真实项目方案优劣 | 真实业务验收属于后续项目或场景阶段 |
| 不把截图当几何证明 | 截图只能辅助肉眼检查 |
| 不验证真实块库完整插入 | 真实块库和 block readback 可作为 Phase W 之后的专项 |

### W.2 执行前条件与停止点

| 条件 | 检查方式 | 不满足时动作 |
| --- | --- | --- |
| CAD-MCP Python 依赖齐全 | `run_cad_validation.py` 的 `python_import_*` 步骤 | `missing_dependency` 时停止并列缺失依赖，除非用户授权安装 |
| AutoCAD 已打开 | `autocad_com_connect` | `cad_connection_failed` 时停止，请用户打开 AutoCAD |
| 有活动测试 DWG | `AutoCADComDriver(connect_existing_only=True)` 输出文档名 | 无活动文档时停止，请用户打开测试 DWG |
| 允许写入 `CODEX_PREVIEW` | 执行器安全策略 | 不允许则停止问用户 |
| 不需要保存、覆盖、删除、正式图层 | 执行请求审查 | 一旦需要突破，必须先问用户 |
| 当前窗口可截图 | `render_preview.py --check` 和 `capture_autocad_window` | 窗口/权限问题可登记 `external_blocker` |

### W.3 输出目录与证据清单

统一输出目录：

```text
output/validation_runs/cad-readback-alpha/
  report.json
  report.md
  execution_summary.json
  readback_report.json
  cad-validation-window.png
  *.stdout.txt
  *.stderr.txt
```

| 证据文件 | 必须存在条件 | 用途 | 缺失时处理 |
| --- | --- | --- | --- |
| `report.json` | 每次总验证后 | 顶层 `status`、steps、failure_category、next_actions | 没生成则按总控脚本失败处理 |
| `report.md` | 每次总验证后 | 人读摘要 | JSON 存在但 MD 缺失时修报告生成 |
| `execution_summary.json` | `execute_sample_plan` 有 stdout 时 | created handles、目标图层、对象摘要 | 缺失则查执行阶段 |
| `readback_report.json` | `inspect_readback` 有 stdout 时 | 几何验证主证据 | 缺失则查回读阶段 |
| `cad-validation-window.png` | 截图成功后 | 视觉辅助证据 | 环境权限问题登记外部阻塞 |
| `*.stdout.txt` / `*.stderr.txt` | 每个 step 都应写入 | 失败复盘和分类 | 缺失则修 runner 证据落盘 |

### W.4 执行顺序总表

| 顺序 | 步骤 | 命令 / 动作 | 预期证据 | 失败后去向 |
| --- | --- | --- | --- | --- |
| 1 | 恢复上下文 | 读 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、本文 Phase W、`CAD_AGENT_AUTONOMOUS_VALIDATION.md` | 明确边界 | 缺文档或引用漂移先修文档 |
| 2 | 无 CAD 预检 | `run_cad_validation.py --no-cad` | no-cad `report.json status=pass` | 仓库内问题自动修 |
| 3 | 依赖和截图能力 | 总控中的 import / `render_preview_check` | import OK、截图能力 ready | 依赖缺失问用户；脚本坏自动修 |
| 4 | CAD 连接 | `autocad_com_connect` | `COM OK: <DWG name>` | AutoCAD / DWG / 授权问题问用户 |
| 5 | validate baseline plan | 总控内置 | `validate_sample_plan` pass | 修 schema / plan |
| 6 | dry-run baseline plan | 总控内置 | `dry_run_sample_plan` pass | 修 dry-run / plan_engine |
| 7 | 安全落图 | `execute_sample_plan` | `execution_summary.json`、created handles | 仓库执行问题自动修，COM 权限问题问用户 |
| 8 | 截图取证 | `capture_screen` | `cad-validation-window.png` | 脚本问题自动修，窗口/权限问用户 |
| 9 | 实体回读 | `inspect_readback` | `readback_report.json` | 仓库 readback 自动修 |
| 10 | 几何门禁 | 解析 `readback_report.json` | `status=geometry_verified` 且关键 checks 全 pass | 修 verification / readback；不得只看总控 pass |
| 11 | 归档与同步 | 写 `docs/verification/cad_readback_alpha_check.md`，更新状态文档 | 验证记录和状态同步 | 缺记录不算交接完成 |

### W.5 CAD 待检查矩阵

| ID | 检查项 | 触发条件 | 命令 / 证据 | 通过标准 | 失败分类与下一步 |
| --- | --- | --- | --- | --- | --- |
| W-CAD-01 | 无 CAD 预检基线 | Phase W 前、换机前、真实 CAD 不稳定时 | `& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-w-preflight-no-cad` | `report.json.status=pass` | `repo_regression` / `cad_plan_invalid` / `dry_run_failed`：先自动修仓库 |
| W-CAD-02 | 依赖与截图能力 | 换机、截图失败、总控依赖步骤失败 | import `PIL` / `win32com.client` / `win32gui`；`render_preview.py --check` | 依赖可导入，截图能力 ready | `missing_dependency`：问用户授权修环境 |
| W-CAD-03 | AutoCAD COM 连接 | 准备落图或回读 | `autocad_com_connect` step 或 `AutoCADComDriver(connect_existing_only=True)` | 能打印活动 DWG 名称 | `cad_connection_failed`：问用户处理 CAD 环境 |
| W-CAD-04 | baseline CAD_PLAN 校验 | 任何真实落图前 | `validate_sample_plan` 或 `validate_plan.py <plan_path>` | `VALID CAD_PLAN` | `cad_plan_invalid`：修 schema / 示例 / 生成器 |
| W-CAD-05 | dry-run 一致性 | 任何真实落图前 | `dry_run_sample_plan` 或 `dry_run_plan.py <plan_path>` | 对象、尺寸、基点、图层、文字、标注符合预期 | `dry_run_failed`：修 plan_engine / CAD_PLAN |
| W-CAD-06 | 安全落图 | AutoCAD 已打开且预检通过 | `execute_sample_plan`；`execution_summary.json` | 只写 `CODEX_PREVIEW`，created handles 非空，不保存/覆盖/删除 | `execution_failed`：先查执行器、driver、安全策略 |
| W-CAD-07 | 截图落盘 | 已落图，需要视觉辅助 | `capture_screen`；`cad-validation-window.png` | PNG 文件存在且可作为视觉辅助 | `screenshot_failed`：路径/脚本自动修，窗口/权限问用户 |
| W-CAD-08 | 实体回读 | 已落图，需要证明画准 | `inspect_readback`；`readback_report.json` | 回读到本次实体，字段覆盖 layer / bbox / base point / text / dimension | `readback_failed`：查 handles、scope、snapshot、实体标准化 |
| W-CAD-09 | `geometry_verified` 升级门 | 生成 verification report 后 | 解析 `readback_report.json.status` 和 `checks` | 只有 readback scope 明确且关键 checks 全 pass，才允许 `geometry_verified` | 误升级/误降级：修 `verification_report.py` 和测试 |
| W-CAD-10 | 新 CAD_PLAN 延后补验 | pipeline 或新功能生成新 CAD_PLAN，但当轮无 CAD | `docs/verification/cad_deferred_verification_template.md` | 登记 plan_path、expected_layer、expected_objects、tolerance、待补命令 | 不得把 dry-run / no-cad / 截图能力写成几何准确 |
| W-CAD-11 | blank-shell CAD 输出尺寸一致性 | blank-shell pipeline 输出 CAD_PLAN 后 | pipeline artifact + validate + dry-run + 后续 CAD 补验 | placement bbox、OBJECT_SPEC、CAD_PLAN 尺寸一致 | 不一致时查 pipeline、block metadata、fallback object spec |
| W-CAD-12 | 换机真实 CAD 验收 | 新电脑 clone 后 | README 全量验收 + `run_cad_validation.py --output-dir output\validation_runs\migration-check` | 脚本链和 CAD-MCP 对话画图链都通过 | 任一步失败先读 blocker playbook，不用“先写代码以后再配环境”替代验收 |
| W-CAD-13 | CAD COM 调用底座能力 | 真实 CAD 总控、driver 变更、换机验收 | `scripts/run_cad_capability_probe.py` 或总控 `cad_capability_probe` step | `cad_capability_probe.json.status=cad_capability_verified` 且 checks 全 pass | `cad_capability_failed`：查 primitive write、handle readback、实体标准化和安全层 |

### W.6 分步执行清单

执行记录（2026-05-25 21:42）：W-01 到 W-16 已执行并完成 CAD 底座加固复验。默认沙箱身份无法看到用户桌面的 AutoCAD COM 活动对象，沙箱外用户会话诊断确认 `AutoCAD.Application`、`AutoCAD.Application.25.1`、`AutoCAD.Application.25` 均可 `GetActiveObject`。本轮先在 `output\validation_runs\full-repair-cad-20260525-212001\readback_report.json` 暴露“顶层 pass 但 readback 未 geometry_verified”的仓库门禁问题，随后按 W.10 修复 runner 和 handle 定向回读；又新增 `cad_capability_probe`，验证活动文档、preview 图层、矩形/文字/标注写入、handle 回读、类型统计、bbox 和安全边界。最终 W-07 输出 `output\validation_runs\cad-foundation-full-cad-20260525\report.json`，顶层状态为 `pass`；`execution_summary.json` 记录 7 个 baseline created handles；当时的 `cad-validation-screen.png` 已生成；`readback_report.json.status=geometry_verified`，关键 checks 全部 pass；`cad_capability_probe.json.status=cad_capability_verified`，能力矩阵 checks 全部 pass。2026-05-26 的 `R-CAD-VIEW-CAPTURE` 已把后续总控截图产物升级为 `cad-validation-window.png`。全程只写入 `CODEX_PREVIEW`，未保存 DWG、未覆盖原图、未删除实体、未修改正式图层。

- [x] W-01 读取上下文。
  - 动作：读取 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`、本文 Phase W、`CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`CAD_AGENT_BLOCKER_PLAYBOOK.md`。
  - 通过：能明确复述 Phase W 目标、禁止项和“baseline 已通过但不能扩大到任意 CAD_PLAN”的口径。
- [x] W-02 设置命令前置。
  - 动作：
    ```powershell
    $env:PYTHONIOENCODING='utf-8'
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
    ```
  - 通过：后续所有命令都使用 CAD-MCP `.venv` 的 `$py`。
- [x] W-03 建立输出目录命名。
  - 动作：本轮真实 CAD 验证使用 `output\validation_runs\cad-readback-alpha`。
  - 通过：不覆盖历史证据；如果目录已存在，先新建带时间后缀目录。
- [x] W-04 运行无 CAD 预检。
  - 命令：`& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\phase-w-preflight-no-cad`
  - 证据：`output\validation_runs\phase-w-preflight-no-cad\report.json`
  - 通过：`status=pass`。
- [x] W-05 若无 CAD 预检失败，读取失败步骤。
  - 动作：读取 `report.json`、失败 step 的 stdout/stderr。
  - 通过：能归类为 `repo_regression`、`cad_plan_invalid`、`dry_run_failed`、`screenshot_failed` 或 `missing_dependency`。
  - 下一步：仓库内问题自动最小修复并复跑；依赖缺失按外部阻塞处理。
- [x] W-06 确认用户侧 CAD 前置条件。
  - 动作：确认 AutoCAD 已打开、存在活动测试 DWG、窗口可见、允许写入 `CODEX_PREVIEW`。
  - 通过：可以进入真实 CAD 总验证。
  - 不通过：停止并列出用户需处理事项。
- [x] W-07 运行真实 CAD 总验证。
  - 命令：`& $py scripts\run_cad_validation.py --output-dir output\validation_runs\cad-readback-alpha`
  - 证据：`report.json`、`report.md`、各 step stdout/stderr。
  - 通过：进入 W-08 到 W-12 的证据审查；不能只凭顶层 status 完成。
- [x] W-08 审查 `report.json` 顶层状态。
  - 通过：若 `status=pass`，继续查具体证据；若 `status=external_blocker`，列用户事项；若 `status=fail`，按 failure_category 自动修。
- [x] W-09 审查落图执行证据。
  - 证据：`execution_summary.json`。
  - 通过：`layer` 为 `CODEX_PREVIEW`，`created_handles` 非空，未出现保存、覆盖、删除或正式图层操作。
- [x] W-10 审查截图证据。
  - 证据：`cad-validation-window.png`。
  - 通过：文件存在；截图只作为视觉辅助，不作为几何准确结论。
- [x] W-11 审查实体回读报告。
  - 证据：`readback_report.json`。
  - 通过：包含 expected / actual / checks / evidence / limitations；readback scope 由 created handles 或可信 snapshot 证明。
- [x] W-12 审查几何与内容 checks。
  - 通过：`readback_scope`、`created_handles_scope`、`layer_entities`、`bbox_size`、`base_point`、`label_text`、`dimension_count` 中适用项均为 pass；没有 fail、warning 或关键 not_run。
- [x] W-13 审查 `geometry_verified` 升级。
  - 通过：只有 W-09 到 W-12 全部满足时，`readback_report.json.status` 才能是 `geometry_verified`。
  - 注意：`screenshot_captured`、`executed_only`、`unverified`、`failed` 都不能作为“画准了”的完成证据。
- [x] W-14 如果 readback report 未升级，定位缺口。
  - 动作：按缺口区分 created handles、scope、bbox、base point、label、dimension、截图路径或实体标准化问题。
  - 通过：仓库内问题转入最小测试和最小修复；外部 CAD 环境问题登记 `external_blocker`。
- [x] W-15 形成长期验证记录。
  - 动作：创建或更新 `docs/verification/cad_readback_alpha_check.md`。
  - 通过：记录 output dir、顶层 status、失败分类、截图路径、readback report、最终结论和 residual risk。
- [x] W-16 同步状态文档。
  - 动作：更新 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`；出现新失败教训时更新 `CAD_AGENT_ISSUES.md`。
  - 通过：状态不夸大；仍然区分 no-cad pass、截图证据和真实几何验证。

### W.7 失败分类与自动处理策略

| failure_category / 缺口 | 归属 | 是否问用户 | Codex 下一步 |
| --- | --- | --- | --- |
| `missing_dependency` | 多数是环境 | 是，除非用户授权安装 | 列出缺失包或组件；不要绕过依赖继续声明完成 |
| `cad_connection_failed` | 用户 / CAD 环境 | 是 | 要求打开 AutoCAD、处理授权弹窗、打开活动测试 DWG |
| `repo_regression` | 仓库 | 否 | 最小复现、最小修复、重跑相关测试和总验证 |
| `cad_plan_invalid` | 仓库 | 否 | 修 schema、example 或 plan 生成 |
| `dry_run_failed` | 仓库 | 否 | 修 dry-run、CAD_PLAN 或 plan_engine |
| `execution_failed` | 仓库优先 | 视情况 | 查安全策略、driver、target layer、created handles；COM/权限才问用户 |
| `screenshot_failed` | 二分 | 视情况 | 路径/脚本自动修；窗口不可见或截图权限问用户 |
| `readback_failed` | 仓库优先 | 视情况 | 查 `inspect_dwg.py`、created handles、scope、snapshot、实体标准化 |
| `readback_report.status != geometry_verified` | 仓库或证据不足 | 视具体缺口 | 不得声明完成；先修证据链或登记外部阻塞 |
| `geometry_verified` 误升级 / 误降级 | 仓库 | 否 | 修 `verification_report.py` 和测试 |

### W.8 `geometry_verified` 升级门槛

只有同时满足下面条件，才允许把真实 CAD 几何验证写成通过：

| 门槛 | 证据 |
| --- | --- |
| baseline plan validate pass | `report.json` 中 `validate_sample_plan` pass |
| dry-run pass | `report.json` 中 `dry_run_sample_plan` pass |
| 实际落图到 `CODEX_PREVIEW` | `execution_summary.json` |
| created handles 非空且可追踪 | `execution_summary.json.created_handles` 与 readback 实体匹配 |
| readback scope 明确 | `readback_report.json` 中 scope 相关 check pass |
| 对象数量、类型和图层匹配 | `checks` 与 `actual.layer_counts` |
| bbox、尺寸和基点在误差内 | `bbox_size`、`base_point` check pass |
| 文字和标注匹配或明确不适用 | `label_text`、`dimension_count` check pass 或不适用 |
| 截图文件存在 | `cad-validation-window.png`，仅作辅助证据 |
| 未保存、覆盖、删除、修改正式图层 | 执行摘要和安全策略无违规 |

即使 `run_cad_validation.py` 顶层 `status=pass`，也必须继续审查 `readback_report.json.status`。只有 `readback_report.json.status=geometry_verified` 且关键 checks 全部通过，才允许说 baseline 真实 CAD 几何已通过。

### W.9 停止问用户的条件

| 场景 | 问用户什么 |
| --- | --- |
| AutoCAD 未打开、COM 不通或无活动文档 | 请打开 AutoCAD，并打开本次验证用测试 DWG |
| CAD 授权弹窗、插件弹窗、窗口不可见 | 请处理 CAD 窗口状态 |
| 缺 CAD-MCP、pywin32、Pillow、win32gui 或截图权限 | 是否允许安装或修复依赖 |
| 需要保存 DWG | 是否明确允许保存 |
| 需要覆盖原图、删除实体、修改正式图层 | 是否明确批准高风险操作 |
| 需要真实项目图纸或真实公司块库 | 请用户选择具体图纸或块库 |
| 用户意图或业务语义存在多种合理解释 | 请用户确认语义后再继续 |

### W.10 继续自动修的条件

| 场景 | 自动动作 |
| --- | --- |
| 单测、自检、repo audit、benchmark 失败 | 最小复现、最小修复、重跑 |
| schema / example 不一致 | 修示例或 schema |
| wrapper 导入路径错误 | 修脚本入口 |
| baseline CAD_PLAN 不合法 | 修 fixture、schema 或生成器 |
| dry-run 输出结构错误 | 修 dry-run report 或 plan_engine |
| created handles 没有传递到 readback | 修 execute / inspect 接口 |
| readback JSON 字段缺失或实体标准化不稳 | 修 `inspect_dwg.py` 或 CAD IO 标准化 |
| `geometry_verified` 状态升级逻辑错误 | 修 `verification_report.py` 并补测试 |
| 输出目录、report 或 artifact 缺失 | 修 `cad_validation_runner.py` 的证据落盘 |

### W.11 退出标准

`pass` 退出必须同时满足：

- `output\validation_runs\cad-readback-alpha\report.json` 存在。
- `execution_summary.json` 存在，且 created handles 非空。
- `cad-validation-window.png` 存在。
- `readback_report.json` 存在。
- `readback_report.json.status=geometry_verified`。
- `cad_capability_probe.json` 存在，且 `status=cad_capability_verified`。
- 关键 checks 没有 fail、warning 或关键 not_run。
- 全程只写 `CODEX_PREVIEW`，不保存、不覆盖、不删除、不改正式图层。
- `docs/verification/cad_readback_alpha_check.md` 已记录证据路径和结论。

`external_blocker` 退出必须同时满足：

- 无 CAD 预检已通过，或仓库内问题已排除。
- 剩余失败明确属于环境、授权、窗口、依赖、活动 DWG、用户图纸或块库选择。
- 已列出用户需要处理的具体事项。
- 状态文档没有声称真实 CAD 几何已验证。

`fail` 不能作为完成退出：

- 失败属于仓库内可修问题时，不得声明完成。
- 失败分类不清时，先补日志、报告分类或最小复现。
- 证据缺失时，先修证据链，不跳到结论。

### W.12 完成后同步文档

| 文档 | 何时更新 | 写什么 |
| --- | --- | --- |
| `docs/verification/cad_readback_alpha_check.md` | Phase W 跑过真实 CAD 后 | report 路径、顶层 status、截图、readback report、结论和 residual risk |
| `CORE_STATUS.md` | CAD 验证成熟度变化后 | CAD execution、entity readback、verification 的状态变化 |
| `CAD_AGENT_STATUS.md` | 每次 Phase W 完成、失败或阻塞后 | 当前状态、下一步、blocker |
| `CAD_AGENT_CHANGELOG.md` | 验证状态、脚本、规则或计划发生变化后 | 变更流水 |
| `CAD_AGENT_ISSUES.md` | 出现失败教训或长期风险后 | 现象、原因、修复、预防 |

---


## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `CAD_AGENT_ISSUES.md`。
