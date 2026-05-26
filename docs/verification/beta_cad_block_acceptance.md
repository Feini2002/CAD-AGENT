# BETA-CAD-BLOCK 父包总验收（真实 CAD 能力扩展 · 01–05）

最后更新：2026-05-26

> 机器入口：`core/verification/cad_beta_evidence_rollup.py`、`scripts/run_cad_beta_evidence_rollup.py`。证据词表见 [`evidence_gate_handoff_rules.md`](evidence_gate_handoff_rules.md)。

## 父包 `BETA-CAD-BLOCK` 已交付（01–05）

| 小包 | 能力 | 边界文档 / 机器入口 |
| --- | --- | --- |
| `BETA-CAD-BLOCK-01` | 受控 block transform beta（锚点 / rotation / uniform scale） | `block_alpha_beta_suite.json` |
| `BETA-CAD-BLOCK-02` | 属性块 / tag readback 探针（deferred 与不误报） | `block_attribute_probe.py` |
| `BETA-CAD-BLOCK-03` | capability probe entity-level evidence（polyline / hatch deferred） | `cad_capability_probe.py` |
| `BETA-CAD-BLOCK-04` | `drawing_standard_profile`（role→预览层 / 语义层 / 样式） | `codex_preview_beta.json` |
| `BETA-CAD-BLOCK-05` | 本 rollup + 总验收测试 | `cad_beta_evidence_rollup.json` |

**最新 rollup 证据**：`output/test_artifacts/cad_beta_evidence/beta_cad_block_05/cad_beta_evidence_rollup.json`（non-CAD，5/5 subpackages pass）。

## 现在可以声称什么

- 受控 `insert_block_alpha` 在多种 transform 下 **validate + dry-run valid**（01）。
- 属性 readback **探针契约**已固化：无 probe 不误报；缺 tag → `deferred`（02）。
- Fake-driver capability probe 可输出 **`cad_capability_verified`** 与 `entity_evidence`（hatch **deferred**）（03）。
- `drawing_standard_profile` 在 **preview_only** 下把角色解析到 **`CODEX_PREVIEW`**，并保留语义层名（04）。
- 01–05 子包证据可由 **单一 rollup JSON** 机器汇总（05）。

## 不能声称什么（必须继续遵守）

- **不能说** 本父包 rollup **`geometry_verified`** 或真实项目图纸已画准。
- **不能说** beta suite / Fake driver probe **等于** 用户 AutoCAD 会话下的全面 CAD 验证。
- **不能说** 任意公司块库、正式图层（`A-FURN` 等）写入、或 hatch COM 已验证。
- **不能把** `geometry_verified_by_capability_probe` 扩大为任意 `CAD_PLAN` 几何准确。
- **不能跳过** `R-BLOCK-CAD-05` / CAD validation runner 的 **created-handle readback** 与证据门控。

## 真实 CAD 参考（非 rollup 自动执行）

| 参考 | 说明 |
| --- | --- |
| `output/validation_runs/r-block-alpha-cad/` | 受控块 alpha 真实 CAD（`R-BLOCK-CAD-05`） |
| `output/validation_runs/codex-second-gate-block-alpha-cad-final/` | 二次门禁 block alpha 实跑 |

rollup **仅引用路径**，不在 CI/单测中自动重跑 COM。

## 子校验（总验收）

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_beta_block_acceptance -v
& $py scripts\run_cad_beta_evidence_rollup.py
```

## 下一主线（PlanMD）

`BETA-CAD-BLOCK` 父包已收口。下一后置主线默认：**`BETA-PROJECT-SAMPLE-01`**（脱敏项目样本协议）；须继续遵守证据门槛。
