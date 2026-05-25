# Phase W CAD Readback Alpha Check

最后更新：2026-05-25 21:42

补充：后续 CAD 调用底座加固已新增 `cad_capability_probe` 硬门禁。最新总证据见 `docs/verification/cad_foundation_capability_check.md` 与 `output\validation_runs\cad-foundation-full-cad-20260525\report.json`。

## 最新复验结论

本轮对 Phase W 做了全量修复复验：先发现一次 `run_cad_validation.py` 顶层 `status=pass` 但 `readback_report.status=screenshot_captured` 的误判风险，随后修复总控门禁和真实 CAD 定向回读，再在用户会话下复跑 Phase W W-07。最终真实 CAD 回读闭环已通过 baseline 验证：

```text
status: pass
readback_report.status: geometry_verified
geometry_verified: yes
output_dir: output\validation_runs\full-repair-cad-retry-20260525-212916
```

关键证据：

| 证据 | 路径 / 值 | 结论 |
| --- | --- | --- |
| 误判暴露 | `output\validation_runs\full-repair-cad-20260525-212001\readback_report.json` | 顶层 report 曾为 `pass`，但 readback 仍是 `screenshot_captured`；该结果不能作为几何通过 |
| no-cad 复验 | `output\validation_runs\full-repair-no-cad-final-20260525\report.json` | 非 CAD 总控 `status=pass`，203 tests OK |
| 沙箱内诊断 | `output\validation_runs\cad-com-diagnostic-20260525-210153\cad_com_diagnostic.json` | Codex 默认命令身份为 `desktop-r40v31q\codexsandboxoffline`，看不到用户桌面的 `acad.exe`、窗口和 COM 活动对象 |
| 用户会话诊断 | `output\validation_runs\cad-com-diagnostic-elevated-20260525-210219\cad_com_diagnostic.json` | `desktop-r40v31q\user` 下可见 AutoCAD PID 20880、窗口 `Autodesk AutoCAD 2026 - [A1_page2_vector_full.dwg]`，`AutoCAD.Application` / `.25.1` / `.25` 均可 `GetActiveObject` |
| 真实 CAD 总验证 | `output\validation_runs\full-repair-cad-retry-20260525-212916\report.json` | 顶层 `status=pass`，且 inspect readback 门禁通过 |
| 落图摘要 | `output\validation_runs\full-repair-cad-retry-20260525-212916\execution_summary.json` | 只写入 `CODEX_PREVIEW`，created handles 为 `38E9, 38EA, 38EB, 38EC, 38ED, 38EE, 392A` |
| 截图 | `output\validation_runs\full-repair-cad-retry-20260525-212916\cad-validation-screen.png` | 视觉辅助证据已生成，文件大小 527661 bytes |
| 实体回读 | `output\validation_runs\full-repair-cad-retry-20260525-212916\readback_report.json` | `status=geometry_verified`，文件大小 4761 bytes |

`readback_report.json` 关键 checks 全部通过：

| check | status | 摘要 |
| --- | --- | --- |
| `readback_scope` | `pass` | 回读范围限定为本轮 |
| `layer_entities` | `pass` | `CODEX_PREVIEW` 上回读到 7 个实体 |
| `bbox_size` | `pass` | 回读 bbox 为 1800.0 x 600.0，符合 1800 x 600 |
| `base_point` | `pass` | bbox min 为 `[0.0, 0.0]`，符合 base `[0, 0]` |
| `label_text` | `pass` | 标签为 `测试柜` |
| `dimension_count` | `pass` | 回读到 2 个标注实体 |
| `created_handles_scope` | `pass` | 回读覆盖本轮 created handles |

本轮仓库加固：

- `core/verification/cad_validation_runner.py`：`inspect_readback` 即使命令返回 0，也必须解析 stdout / `readback_report.json`，只有 `status=geometry_verified` 且关键 checks 全部 `pass` 才允许该 step 通过。
- `core/verification/inspect_dwg.py` 与 `core/cad_io/autocad_com.py`：当 `execution_summary.created_handles` 存在时，优先通过 `Document.HandleToObject(handle)` 定向回读本轮实体，避免在真实大 DWG 中全量枚举 ModelSpace。
- `tests/core/test_cad_validation_runner.py` 与 `tests/core/test_verification_report.py`：新增回归测试，锁住非 `geometry_verified` 不得通过、按 handle 回读不得扫描全 ModelSpace。

安全边界：本轮只写入 `CODEX_PREVIEW`，没有保存 DWG，没有覆盖原图，没有删除实体，没有修改正式图层。此结论只覆盖 Phase W baseline `examples\plans\draw_test_cabinet.json` 的真实 CAD 几何闭环，不扩大为真实项目图纸或任意 CAD_PLAN 全部已验证。

## 历史阻塞记录（20:52）

本轮已执行 Phase W W-07 真实 CAD 总验证入口，但未完成真实 CAD 落图、截图或实体回读闭环。

当前结论为：

```text
status: external_blocker
failure_category: cad_connection_failed
blocked_step: autocad_com_connect
geometry_verified: no
```

不能声明 baseline 真实 CAD 几何通过。原因是 `autocad_com_connect` 无法取得活动 AutoCAD COM 对象；后续 `execute_sample_plan`、`capture_screen`、`inspect_readback` 已由 runner 依赖门标记为 `not_run`，没有生成真实几何证据。

## 证据路径

| 证据 | 路径 | 结论 |
| --- | --- | --- |
| W-04 preflight | `output\validation_runs\phase-w-preflight-no-cad\report.json` | `status=pass` |
| W-06 只读探针 | `output\validation_runs\phase-w-w06-cad-probe\autocad_com_connect.stderr.txt` | `AutoCAD.Application` COM 不可用 |
| W-07 总验证 | `output\validation_runs\cad-readback-alpha-retry-20260525-205208\report.json` | `status=external_blocker` |
| W-07 COM stderr | `output\validation_runs\cad-readback-alpha-retry-20260525-205208\autocad_com_connect.stderr.txt` | `AutoCAD.Application` 无效；`AutoCAD.Application.25/25.1` 操作无法使用 |
| CAD 进程探测 | PowerShell `Get-Process` | 存在两个 `acad.exe` 进程，但 `MainWindowTitle` 均为空 |
| CAD 窗口枚举 | `win32gui.EnumWindows` | 未发现包含 AutoCAD / CAD / DWG / Autodesk 的可见窗口标题 |
| Dispatch 探测 | `win32com.client.Dispatch(...)` | 版本化 ProgID 探测 30 秒超时 |

## W-07 step 摘要

| step | status | 说明 |
| --- | --- | --- |
| `python_import_pillow` | `pass` | Pillow 可导入 |
| `python_import_pywin32` | `pass` | pywin32 可导入 |
| `python_import_win32gui` | `pass` | win32gui 可导入 |
| `self_check` | `pass` | 仓库自检通过 |
| `unit_tests` | `pass` | 199 tests OK |
| `validate_sample_plan` | `pass` | baseline `CAD_PLAN` 合法 |
| `dry_run_sample_plan` | `pass` | dry-run 与 baseline 意图一致 |
| `render_preview_check` | `pass` | 截图依赖检查 ready |
| `non_cad_benchmark` | `pass` | 非 CAD benchmark 通过 |
| `autocad_com_connect` | `fail` | `cad_connection_failed` |
| `execute_sample_plan` | `not_run` | blocked by `autocad_com_connect` |
| `capture_screen` | `not_run` | blocked by `autocad_com_connect` |
| `inspect_readback` | `not_run` | blocked by `autocad_com_connect` |

## 缺失的真实 CAD 证据

以下证据本轮没有生成，因此不能进入几何通过口径：

- `execution_summary.json`
- `cad-validation-screen.png`
- `readback_report.json`
- `readback_report.json.status=geometry_verified`

## 本轮仓库加固

- `core/cad_io/autocad_com.py`：连接失败时保留底层 COM detail，并尝试常见版本化 AutoCAD ProgID。
- `core/verification/cad_validation_runner.py`：`autocad_com_connect` 或 `execute_sample_plan` 失败后，后续依赖 CAD step 标记为 `not_run`，避免连锁错误污染顶层状态。
- `core/verification/cad_validation_runner.py`：清理本轮派生 artifact，避免复用输出目录时旧 `execution_summary.json` / `readback_report.json` / 截图冒充本轮证据。
- `tests/core/test_autocad_com_driver.py` 与 `tests/core/test_cad_validation_runner.py` 已覆盖上述行为。

## 外部阻塞处理

进入 W-07 前，需要用户侧环境满足：

- 当前打开的是 AutoCAD，而不是仅有后台 `acad.exe` 进程。
- AutoCAD 主窗口可见，且已经打开活动测试 DWG。
- `AutoCAD.Application.25` 或 `AutoCAD.Application.25.1` 可被 COM `GetActiveObject` 发现。
- 没有授权弹窗、启动页、插件弹窗或权限隔离阻止 COM 自动化。
- 当前 Codex 进程与 AutoCAD 处在同一用户会话和权限级别；如果 AutoCAD 以管理员运行，Codex 侧普通权限 COM 可能无法取得活动对象。

满足后重新运行：

```powershell
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\cad-readback-alpha
```
