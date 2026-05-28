# 项目样本 Intake（BETA-PROJECT-SAMPLE-07）

最后更新：2026-05-28

## 用途

用户准备接入真实项目前，复制 `projects/sample_intake_template/`（办公等）或 **`projects/residential_training_template/`（家装训练）** 为 `projects/<your_sample_id>/`，按协议填 manifest 与 README，**不提交原始 DWG**。

## 步骤

1. 复制模板目录并重命名 `sample_id`。
2. 编辑 `sample.manifest.json`：`display_name`、`domain`、`input_files`。
3. 在 `input/` 放入结构化 JSON（如 `shell.manual.json`）。
4. 填写 `expected/expected_notes.md`。
5. 运行协议扫描：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_project_sample_protocol_scan.py
```

## 升级到真实 CAD（BETA-PROJECT-SAMPLE-08）

- 用户会话下 AutoCAD 已开，`CODEX_PREVIEW` 可用。
- 为样本新增 `examples/workflows/<sample_id>_project_loop.json`（指向该样本 `projects/<sample_id>/` 路径）。
- 先跑 workflow（产出 `cad_plan_items/`），再跑 `run_project_sample_cad_check.py --require-cad-verified` 并收集 created handles。
- 合成回归样本见 `projects/sample_test_fitout_20260528/`；用户真实项目仍复制 07 模板为 `projects/<your_id>/`。
- 通过 `run_table_c_evidence_gate.py` 后再考虑 registry writeback。

## 阻塞项

- 无脱敏结构化输入 → 停在 07；可用仓库内合成样本（08 已证）验证 CAD 链，不等同客户 DWG。
- 含 `.dwg` / `.dxf` → 协议扫描 fail。
