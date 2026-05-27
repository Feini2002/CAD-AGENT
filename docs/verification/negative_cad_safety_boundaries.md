# LCAD-10.4：负向 CAD 安全边界

最后更新：2026-05-27

> 机器入口：`scripts/run_negative_cad_plan_suite.py`、`scripts/run_write_guard_cad_runner.py`、`scripts/run_negative_cad_runner.py`  
> 最新 fake/no-CAD 证据：`output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json`  
> 最新真实 CAD 负向安全证据：`output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json`  
> 最新覆盖率可读证据：`output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json`

本文只定义负向输入、安全守卫和声明边界。它不证明正向 CAD 几何准确，也不把 `negative_guard_verified` 计入几何证明。

## 包边界

| 包 ID | 状态 | 证明内容 | 机器入口 | 后续映射 |
| --- | --- | --- | --- | --- |
| `LCAD-10.1` | done | 负向 `CAD_PLAN` fixture 必须被 schema / validator 拒收 | `scripts/run_negative_cad_plan_suite.py` | `V-PROOF-50` |
| `LCAD-10.2` | done | preview-only write guard 必须阻断正式图层写入、保存、覆盖、删除 | `scripts/run_write_guard_cad_runner.py` | `V-PROOF-50` |
| `LCAD-10.3` | done | 负向 CAD runner 汇总 plan suite、write guard、session snapshot、no-handle / no-save 证据 | `scripts/run_negative_cad_runner.py` | `RCAD-20`、`V-PROOF-51` |
| `LCAD-10.4` | done | 本文：把负向与安全边界写成可审计声明 | `tests.core.test_negative_cad_safety_boundaries_doc` | `V-PROOF-50` |

## 负向 fixture 分类

`examples/plans/negative/negative_plan_manifest.json` 中的每个 case 都必须带 `failure_category`，并且只能证明“正确拒绝”，不能证明任何绘图能力已经准确。

| failure_category | 当前含义 | 期望结果 |
| --- | --- | --- |
| `unsupported_version` | `CAD_PLAN.version` 不受支持 | schema / validator 拒收 |
| `unsupported_domain` | domain 不在允许列表 | schema / validator 拒收 |
| `unsupported_intent` | intent 不在允许列表 | schema / validator 拒收 |
| `missing_base_point` | absolute placement 缺少 base point | validator 拒收 |
| `zero_width` | 对象尺寸无效 | schema / validator 拒收 |
| `confidence_out_of_range` | confidence 超出 0~1 | schema / validator 拒收 |
| `glyph_missing_primitives` | glyph primitive 缺失 | schema / validator 拒收 |
| `block_alpha_wrong_layer` | `insert_block_alpha` 不在 `CODEX_PREVIEW` | validator 拒收 |

## 安全边界扫描

负向 runner 通过后，只能声明以下守卫成立：

| 检查 | 必须满足 | 证据字段 |
| --- | --- | --- |
| 预览层限制 | 写入目标只允许 `CODEX_PREVIEW` | `write_guard.checks.block_formal_layer_write=pass` |
| 不保存 DWG | 不调用保存或覆盖正式图纸 | `safety.saved_dwg=false` |
| 不删除实体 | 不执行不可逆删除 | `safety.deleted_entities=false` |
| 不修改正式图层 | 正式层写入被阻断 | `safety.modified_formal_layers=false` |
| 不创建实体 | 负向检查后仍 `created_handles=[]` | `created_handles=[]` |
| 会话稳定 | ActiveDocument identity 不变 | `session_guard.comparison.active_document_identity_stable=pass` |
| 预览层无增量 | 负向检查没有新增预览实体 | `preview_layer_entity_delta=0` |
| ModelSpace 无增量 | 负向检查没有新增任意实体 | `modelspace_entity_delta=0` |

## 可声称

- `negative_guard_verified` 表示负向输入与禁止操作被拦截，且没有新增 handles、保存 DWG、删除实体或修改正式图层。
- fake/no-CAD 模式下，最新报告为 `status=pass`，可用于证明 runner 结构、字段和安全口径可复跑。
- `RCAD-20` 已在用户 CAD 会话下补验为 `status=pass` / `negative_guard_verified`，且 `created_handles=[]`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`。
- `LCAD-10.1` 到 `LCAD-10.4` 形成负向安全包链路，可支撑 `V-PROOF-50` 的负向登记。

## 不得声称

- 不得声称 `negative_guard_verified` 是 `geometry_verified`。
- 不得声称 fake/no-CAD pass 自身代表真实 AutoCAD 会话已经安全通过；真实 CAD 结论必须引用 `RCAD-20` 证据路径。
- 不得声称负向 runner 证明任意正向 `CAD_PLAN` 能画准。
- 不得声称截图、dry-run、schema pass 或 write guard pass 可替代 created-handle readback。
- 不得声称 `negative_guard_verified` 计入 CAD 证明覆盖率；它只属于 guard-only 证据，不计入几何证明。

## 真实 CAD 补验边界

`RCAD-20` 已于 2026-05-27 在用户 AutoCAD 会话下补验通过。复跑命令如下：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_negative_cad_runner.py --real-cad --output-dir output\validation_runs\rcad-20-negative-cad-20260527-escalated
```

只有当 `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0` 且安全字段全部为 false 时，才可把 `RCAD-20` 标成真实 CAD 负向安全通过。即便如此，它仍然不计入几何证明。

## 子校验

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_negative_cad_safety_boundaries_doc tests.core.test_negative_cad_plans tests.core.test_write_guard_cad_runner tests.core.test_negative_cad_runner
& $py scripts\run_negative_cad_runner.py --output-dir output\validation_runs\neg-cad-proof-sync\negative-runner-fake-final
& $py scripts\run_capability_readability_report.py --output-dir output\validation_runs\neg-cad-proof-sync\capability-readability-final --guard-report output\validation_runs\neg-cad-proof-sync\negative-runner-fake-final\negative_cad_runner_report.json
```
