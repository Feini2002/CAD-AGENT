# V-PROOF-70：可提交脱敏项目回归 manifest

最后更新：2026-05-28

> 机器入口：`core/verification/project_regression_manifest.py`、`scripts/run_vproof_70_project_manifest_sync.py`
> Manifest：`examples/capability_proof/project_regression_manifest.json`
> Schema：`core/schemas/project_regression_manifest.schema.json`

## 登记行（1 + N 样本）

| capability_id | 说明 |
| --- | --- |
| `project.regression.manifest` | 父行：manifest 审计 + protocol scan 交叉核对 |
| `project.regression.sample.<sample_id>` | 每个 `projects/` 样本一行 |

全部 `claim_level=smoke`、`ladder_level=L0`；协议扫描 pass **不等于** `geometry_verified` 或真实 CAD 几何已证明。

## 退出条件（PROJ-02）

- `project_regression_manifest.schema.json` 校验通过
- **≥2** 个 `submittable=true` 脱敏样本
- 与 `examples/cad_regression/project_sample_cad_rollup.json` 中 CAD rollup 样本 ID 一致（可提交样本）
- `scan_projects_root` 对可提交样本均为 `pass`

## 不得声称

- 不得把 protocol / manifest 审计 pass 升为 `verified` / `showcase` 或抬高表 C 主指标。
- 不得把 `non_cad_with_optional_cad_preview` 说成已在真实 CAD 上完成几何回读验证。
- `sample_blank_shell_too_small` 为负向 fixture（`submittable=false`），仅登记 `blocked_expected_non_cad`。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_project_sample_protocol_scan.py
& $py scripts\run_vproof_70_project_manifest_sync.py
```
