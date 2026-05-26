# BETA-PROJECT-SAMPLE-01 脱敏样本目录协议

最后更新：2026-05-26

> 后置主线：**真实项目样本闭环** 第 1 小包。机器入口：`core/project_samples/protocol.py`、`projects/README.md`。

## 目标

定义 `projects/` 下脱敏样本的**目录结构**、**可提交字段**（`sample.manifest.json`）与 **README 章节**，并提供文档/manifest **扫描器**。

## 已交付

| 项 | 说明 |
| --- | --- |
| 协议文档 | `projects/README.md`（六大章节） |
| Schema | `core/schemas/project_sample_manifest.schema.json` |
| 扫描 | `scan_projects_root()`、`scan_project_sample()` |
| CLI | `scripts/run_project_sample_protocol_scan.py` |
| 基线样本 | `sample_blank_shell/` + `sample.manifest.json` + 样本 `README.md` |

## 行为摘要

- 每个样本必须有 `README.md`、`sample.manifest.json`、`input/`、`expected/expected_notes.md`。
- manifest 经 schema 校验；`input_files[].path` 必须存在。
- 样本树内不得含 `.dwg` / `.dxf` / `.bak`。

## 不能声称什么

- 协议扫描 pass **≠** 项目已在真实 CAD 几何验证。
- **不是** 已接入任意用户原始 DWG 或全公司项目库。

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_project_sample_protocol -v
& $py scripts\run_project_sample_protocol_scan.py
```

## 下一小包

`BETA-PROJECT-SAMPLE-03`：样本 workflow 输出 CAD_PLAN / dry-run。
