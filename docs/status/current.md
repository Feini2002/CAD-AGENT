# 通用 CAD Agent 开发包当前进展

最后更新：2026-05-28（方案 A：家装 Agent 训练期）

本文只保留“现在到哪、证据是什么、风险边界是什么”。历史流水见 `docs/status/changelog.md`，瘦身前全文快照见 `docs/history/snapshots/finished-architecture-2026-05-28/docs__status__current.md`，能力矩阵见 `CORE_STATUS.md`，唯一 `PlanMD` / 主计划见 `CORE_RESTRUCTURE_PLAN.md`。后续任务和优先级只写入 PlanMD，避免状态页变成第二份计划。

## 当前一句话

**Agent 训练期（方案 A）**：主训家装（`docs/training/residential-primary.md`）；案例模板 `projects/residential_training_template/`。Core 与 Lab 三轨已收口；默认 next 是案例 + `feedback.md`，不是 V-PROOF 施工包。

## 默认输出口径

普通最终回复默认不附进度表、表单或表 A/B/C；只有用户明确点名开发状态查询、进度、完整状态、交接、审计、表 A/B/C、表 C、真实 CAD 实力或刷新表 C 时，才展开表格。

## 工具中立口径

训练链路和交接材料面向 Codex、Cursor 及其它同类 agent 工具通用；Phase A 是“一个交互式 Agent 会话按角色分步”，不强制绑定 Cursor 或任一单一软件。

## 表 C 当前机器快照

机器报告：`output/validation_runs/capability-lab/cad_capability_coverage.json`。

| 指标 | 当前值 |
| --- | --- |
| **真实 CAD 实力（主指标）** | **90.99%**，最高 L4 |
| CAD 证明覆盖率 | **90.99%**（333 行；**0 verified + 303 showcase**；25 smoke + 5 deferred） |
| CAD 实力指数 | **93.53%** |
| 场景片段实力（L3+） | **93.62%**（88/94） |
| 展示就绪度 | **90.99%** |

禁止用工程节奏、RCAD 烟囱、截图或 no-CAD benchmark 替代表 C。

## 工程节奏（表 A）

| 指标 | 当前值 |
| --- | --- |
| Core 底座 | **100%**（`docs/verification/core_platform_completion_gate.md`） |
| Agent 多场景 | 约 93% |
| 总进度 | 约 97% |

## 最近有效包

| 包 | 状态 | 证据 | 边界 |
| --- | --- | --- | --- |
| `CORE-PLATFORM-100` | Core 平台门禁收口 | `scripts/run_core_platform_gate.py`；969 tests OK | **≠** 表 C 100% |
| `VCAD-ROUND12-VISUAL-FIRST-SOFA` | 家装沙发 round12 视觉契约落图 | `projects/residential_sofa_2seat_20260528/runs/round12_preview.png`；56 preview handles；`expected/style_target_reference_crop.png` 来源于真实 AutoCAD 截图 crop；generated style target 被 gate 禁止；`round12_style_compare.md` 非 pending；delivery gate pass | 训练案例待用户目视验收，不改表 C |
| `TABLE-C-20260528-P` | smoke→probe showcase ×17 | **98.42%** | 非负例几何；`real_cad_guard` 仍 smoke |
| `TABLE-C-20260528-O` | core.api non_cad_suite | **93.06%** | — |
| `TABLE-C-20260528-N` | scene **100%** | **92.74%** | — |
| `TABLE-C-20260528-M` | scene beta + block 库 | **90.22%** | — |
| `TABLE-C-20260528-L` | 冲突 composition CAD | **86.44%** | — |
| `TABLE-C-20260528-K` | fixture + L3 smoke | **77.27%** | — |
| `TABLE-C-20260528-J` | core.api/guard writeback | `cad_proof` **81.07%** | 当时 headline 76.14% |
| `TABLE-C-20260528-I` | component_role 批量 | 表 C headline **75.71%** | — |
| `TABLE-C-20260528-H` | object/symbol 批量 CAD | 表 C **62.78%** | 旧 evidence audit 债仍在 |
| `TABLE-C-20260528-E` | regression 6 case CAD | 表 C **40.91%**；verified→0 | 下一门 scene_fragment / 实力指数 |
| `TABLE-C-20260528-D` | intent/block/demand/symbol | showcase +27 | — |
| `TABLE-C-20260528-C` | object/domain/glyph | showcase +45 | — |
| `TABLE-C-20260528-B` | composition + benchmark 镜像 | 三波 composition CAD；showcase +10 | 全库 hard audit 仍 fail |
| `TABLE-C-20260528-A` | 工装 catalog showcase | `tablec-fitout-catalog-20260528-cad/` 14/14 | 全库 hard audit 仍 fail |
| `DOC-FINISH-ARCH-01` | 本轮文档架构升级 | 活跃入口瘦身、history snapshot、planning archive、doc governance 预算门禁 | 不改 registry，不新增真实 CAD 几何证明 |
| `CAD-EVIDENCE-01` | 表 C hard audit + visual gate 已建立 | `output/validation_runs/table-c-evidence-gate/` | 旧 registry 审计 131 audited / 59 pass / 72 fail，需另包补债 |
| `V-PROOF-73` | §3 能力证明轨收口 | `output/validation_runs/vproof-73-cross-machine/cross_machine_report.json` | no-CAD 4/4；真实换机仍需人工 gate |
| `STRUCT-MERGE-01` | drawing policy 合并已完成 | composition focused tests、repo audit 历史记录 | 不改变表 C，不运行真实 CAD |
| `VCAD-02` | CAD 视觉表达 P1 已有真实 AutoCAD 证据 | `output/previews/vcad-02-visual-room-plan.png`、99 handles 回读 | 视觉表达不等于施工图交付能力 |

完整历史继续查 `docs/status/changelog.md` 与 `docs/handoffs/package-index.md`。

## 当前风险

| 风险 | 影响 | 当前处理 |
| --- | --- | --- |
| 表 C 旧证据债 | 旧 verified/showcase 报告缺路径或契约字段会阻止新 writeback | 表 C 新包先跑 hard audit、visual review、table C gate |
| CAD 画面与几何扩样仍少 | 用户看到的复杂 CAD 图面仍需持续提升 | 需要时优先 `VCAD-*` 或真实 CAD 扩样包 |
| 自动读图未到交付预备 | 未确认 shell candidates 不能直接落 CAD | 保持人工确认 gate |
| 文档入口再膨胀 | 默认上下文会被 done 明细重新占满 | `run_doc_governance_audit.py` 增加活跃文档体量预算 |

更多风险和教训见 `docs/status/issues.md`。

## 当前入口

| 需要 | 看哪 |
| --- | --- |
| Agent 训练 / 家装主训 | `docs/training/README.md` |
| 案例 backlog | `docs/planning/任务清单.md` §0 |
| 唯一主线 / 后置 Backlog | `CORE_RESTRUCTURE_PLAN.md` |
| 能力矩阵 / 表 A/B/C | `CORE_STATUS.md` |
| 已完成包明细 | `docs/planning/archive/` |
| 当前交接 | `docs/handoffs/current.md` |
| 全量交接索引 | `docs/handoffs/package-index.md` |
| 历史快照 | `docs/history/snapshots/finished-architecture-2026-05-28/` |

## 最近验证入口

最近完整门禁记录：全量 `unittest discover -s tests` **1018 OK**；`run_doc_governance_audit.py` pass；训练 round12 `visual_contract` / `delivery` gate pass。当前 coverage 表 C 主指标以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准：**90.99%**。

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py -m unittest tests.core.test_doc_governance tests.core.test_planmd_governance -v
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

真实 CAD 完成声明仍必须补 validate、dry-run、`CODEX_PREVIEW`、created handles 回读、实体检查和必要截图；截图只作视觉辅助。
