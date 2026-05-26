# Office Alpha Benchmark 证据（R-OFFICE-MICRO）

最后更新：2026-05-26

## 运行命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks.BenchmarkRunnerTests.test_office_alpha_benchmark_runs_phase_r_contract -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_r_micro
```

## 证据目录

`output/test_artifacts/benchmarks/office_alpha_r_micro/`

| 文件 | 说明 |
| --- | --- |
| `benchmark_summary.json` | suite 汇总：`summary`、`evidence_summary`、逐 case `actual` / `expected` |
| `<case_id>/` | 各 case 的 object/composition/shell 产物与 dry-run / verification 报告 |

## Suite 规模（2026-05-26）

| 维度 | 数量 |
| --- | ---: |
| 总 cases | 18 |
| object spec | 6 |
| micro-scene composition | 4 |
| blank-shell scene | 4 |
| failure（预期 blocked） | 3 |
| failure（预期 invalid） | 1 |

## 证据状态汇总

| evidence_state | cases | 含义 |
| --- | ---: | --- |
| `benchmark_pass_non_cad` | 14 | pipeline ok + dry-run valid + verification unverified |
| `blocked_expected_non_cad` | 3 | 预期布局/净空冲突，benchmark 断言 blocked |
| `readback_geometry_verified` | 0 | office alpha **未**做真实 CAD 几何回读 |

| geometry_accuracy | cases |
| --- | ---: |
| `not_verified_without_cad_readback` | 17 |

| failure_category（仅 blocked cases） | cases |
| --- | ---: |
| `insufficient_space` | 1 |
| `entry_clearance_conflict` | 1 |
| `clearance_conflict` | 1 |

## Alpha 退出门槛（R-OFFICE-08）

- [x] `office_alpha_benchmark.json` 覆盖 object / micro-scene / scene / failure 四类。
- [x] 全部 17 cases `run_benchmark_suite` 为 `status=pass`（含 3 个预期 blocked case）。
- [x] pass cases 均为 `benchmark_pass_non_cad`，`geometry_accuracy=not_verified_without_cad_readback`。
- [x] failure cases 均为 `blocked_expected_non_cad`，带 `failure_category` 与 `blocked_reasons` 子串断言。
- [x] suite 输出 `benchmark_summary.json` 可机器读取证据计数。
- [ ] 真实 AutoCAD office 布局 readback（**不在本 Alpha 范围**；见 `R4-EVIDENCE-GATES` / 后续 CAD 包）。

## 与具体场景产品的边界

Office Alpha / Beta 主要是为了验证 Core 可以处理办公相关对象、微场景、blank-shell 和失败样本。它可以作为后续工装 Scene Product 的素材来源，但本身还不是工装产品化开发。

工装或办公 Scene Product 还需要：真实或脱敏项目样本、工装子场景拆分、正式对象体系、图块 metadata、真实 CAD smoke、用户确认流和交付边界。

## 可声称 / 不可声称

**可声称**

- office 对象规格、微场景组合语义、blank-shell 场景样本与 failure 样本均可重复跑通 non-CAD benchmark。
- runner 能区分 `benchmark_pass_non_cad` 与 `blocked_expected_non_cad`，并汇总证据计数。
- 失败样本不会因少放对象而误判为 pass。

**不可声称**

- 办公布局几何已在真实 AutoCAD 中 `geometry_verified`。
- 已有完整碰撞、通道、多边形净空或最优布局算法。
- 工装或办公场景 Agent 已经产品化完成。
- 截图、SVG 预览或 dry-run valid 等同于 CAD 回读几何准确。
- `benchmark_pass_non_cad` 等同于 `readback_geometry_verified`。

## 相关文档

- 用例规格：`docs/planning/phase-r-office-benchmark-cases.md`
- 开发包交接：`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` §10–§14（`R-OFFICE-MICRO-01`～`05`）
