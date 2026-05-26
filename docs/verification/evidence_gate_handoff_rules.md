# Evidence Gate 与交接包填写规则（R4-05）

最后更新：2026-05-26

> 词表与机器门禁见 [`evidence_state_vocabulary.md`](evidence_state_vocabulary.md) 与 `core/verification/evidence_contract.py`。本文规定 **Cursor 每包交接** 与 **Codex 审计** 时必须写清的证据边界。

## 1. 每包交接第 8 项（结论分类）必填

第 8 项不得只写「pass / fail」，必须包含下表至少一行（可多行）：

| 列 | 必填内容 |
| --- | --- |
| **结论** | 本包声称完成了什么（例如 suite pass、runner pass、COM 写入） |
| **证据类型** | 从下表选 **一个词**（禁止自造） |
| **geometry_verified** | 明确写 **是** 或 **否**；若为「是」，必须给出 readback / capability 路径 |

### 证据类型（交接用语）

| 证据类型 | 含义 | 可否声称几何准确 |
| --- | --- | --- |
| `non_cad_only` | 仅 validate / dry-run / benchmark pipeline / `--no-cad` | **否** |
| `benchmark_pass_non_cad` | benchmark case `pipeline_status=ok` 且未 CAD readback | **否** |
| `blocked_expected_non_cad` | 预期 failure（blocked / invalid） | **否** |
| `dry_run_valid_plan_only` | 仅 plan dry-run | **否** |
| `deferred_cad_readback_required` | 步骤故意 deferred，待补 CAD | **否** |
| `readback_geometry_verified` | `readback_report` / block alpha 报告 `geometry_verified=true` | **是**（须列 handles） |
| `cad_capability_verified` | capability probe 在约定范围内 verified | **是**（须列 probe 范围） |
| `visual_aid_only` | 仅有截图 | **否**（截图不得升级几何结论） |

## 2. 禁止声称（全局）

- 不得把 `benchmark_pass_non_cad`、`dry_run_valid_plan_only`、`blocked_expected_non_cad` 说成「图纸几何已验证」。
- 不得把 `cad-validation-window.png` 或任意截图当成 `geometry_verified`。
- 不得把 suite / case **顶层 pass** 当成「全部对象已在 CAD 中几何正确」——须核对 `evidence_summary` / `readback_geometry_verified_count`。
- office alpha 与三组 Core benchmark 当前均为 **non-CAD**；交接中 `readback_geometry_verified_count` 应为 **0**，除非包内单独跑了真实 CAD readback 步骤。

## 3. 机器可读证据路径（按运行类型）

| 运行类型 | 优先打开的文件 | 交接第 7 项应引用 |
| --- | --- | --- |
| CAD validation `--no-cad` | `output/validation_runs/<包名>-no-cad/report.json` | `evidence_summary.non_cad_only` 应为 `true` |
| CAD validation 全量 CAD | `.../report.json` + `readback_report.json` + 相关 `*_report.json` | `created_handles`、各子报告 `evidence_state` |
| Benchmark suite | `output/test_artifacts/benchmarks/<run>/benchmark_summary.json` | `evidence_summary` 与 suite `expected_evidence_summary` 比对结果 |
| Block alpha CAD | `output/validation_runs/r-block-alpha-cad/block_alpha_report.json` | `geometry_verified` + `created_handles` |

## 4. Codex 校验清单（每包）

1. 读 `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 对应章节，9 项是否齐全。
2. 第 8 项是否区分 **non-CAD** 与 **`geometry_verified`**。
3. 若包声明真实 CAD：打开第 7 项路径，核对 `evidence_state` / `geometry_accuracy` 与交接一致。
4. 若 `report.json.status=pass`：核对 `evidence_gate_failure` 为空，且 `evidence_summary` 与运行模式一致（no-CAD → `non_cad_only=true`）。
5. 能力边界以 `CORE_CONTEXT_BRIEF.md`「不能声称的事」为准。

## 5. 与标准 9 项模板的对应

| 模板项 | evidence gate 要求 |
| --- | --- |
| 6. 是否运行真实 CAD | 必须明确 **是 / 否**；否则不能写 readback verified |
| 7. CAD 证据路径 | 列出 `report.json`（及 readback / 截图）；non-CAD 可写 benchmark_summary |
| 8. 结论分类 | 使用上文表格；**禁止**用「测试通过」代替证据类型 |
| 9. 剩余风险 | 若本包未做 CAD，须写明「几何未验证」；若仅受控样本 CAD，须写明未覆盖范围 |

## 6. 父包 `R4-EVIDENCE-GATES` 收口结论

- R4-01～R4-04 已在代码与 `evidence_state_vocabulary.md` 落地词表、benchmark 汇总、CAD runner 顶层 gate。
- R4-05 将上述规则固化为交接必读；后续小包（`Y-MULTI-CANDIDATE`、`X-SCENE-ALPHA` 等）默认遵守本文。
