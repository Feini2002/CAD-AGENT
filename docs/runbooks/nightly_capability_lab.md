# Nightly Capability Lab（CI / 手动）

最后更新：2026-05-28（V-PROOF-72）

本 runbook 描述 **Capability Lab** nightly 入口。默认 **L1 = no-CAD**，可在无 AutoCAD 的 CI 或开发机 nightly 跑通；不替代 RCAD 真实几何补验。

## 前置

```powershell
cd "D:\工作文件\CAD-AGENT"
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

## CI / Nightly（推荐 L1）

```powershell
& $py scripts\run_capability_lab.py --tier L1 --output-dir output\validation_runs\nightly-lab-<yyyyMMdd>
```

退出码 `0` 且 `capability_lab_report.json` 中 `status=pass` 即 nightly 绿。

### L1 步骤（机器清单见 manifest）

1. `self_check.py`
2. `run_negative_cad_plan_suite.py`
3. `run_local_cad_regression.py --no-cad`
4. `run_cad_validation.py --no-cad --environment-optional`
5. `run_capability_coverage.py`
6. `run_project_sample_protocol_scan.py`

## 快速 smoke（L0）

仅 registry coverage，适合 PR 轻量门禁：

```powershell
& $py scripts\run_capability_lab.py --tier L0 --output-dir output\validation_runs\nightly-lab-l0-<yyyyMMdd>
```

## 能力证明登记（V-PROOF-72）

```powershell
& $py scripts\run_vproof_72_nightly_lab_sync.py
```

## 与表 C / RCAD 的关系

| 口径 | 来源 | 说明 |
| --- | --- | --- |
| 表 C 主指标 | `capability-lab/cad_capability_coverage.json` | L1 会复算 coverage，但 smoke 行不计入证明率 |
| 真实 CAD 几何 | §5 RCAD | L1 nightly **不包含** strict regression / hatch 等真实 CAD |
| 趋势 Dashboard | `run_vproof_71_trend_dashboard_sync.py` | 可选；不在 L1 默认 6 步内 |

## 失败排查

- **self_check 失败**：先修 Python / 路径 / 依赖，再跑 Lab。
- **local regression / cad_validation no-CAD 失败**：看对应 `output-dir` 下子报告 `status` 与 `stderr_tail`（Lab 报告内嵌）。
- **不要把 deferred 当成几何失败**：no-CAD 下 `deferred_cad_readback_required` 为预期，除非 step 顶层 `status=fail`。
