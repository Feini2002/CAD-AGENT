# CAD Agent 启动路由器

本目录是可迁移的 CAD Agent 开发包，不绑定某一张 DWG、某一套家装图纸或某一台电脑。`AGENTS.md` 只承担会话启动路由和高风险边界索引；长期规则不堆在根级启动卡片里。

## 默认中文输出

面向用户的说明、状态汇报、方案讨论、结论和追问默认使用中文。代码、命令、路径、文件名、Schema 字段、JSON key，以及 CAD / Python / Git / MCP / AutoCAD 等专有名称保留英文或原文。引用外部技能、插件或工具模板时，先理解含义，再用中文转述。

## 启动顺序

1. 普通任务先读 `CORE_CONTEXT_BRIEF.md`，再按其中“按需展开”表读取 1-2 个相关文件。
2. 唯一 `PlanMD` 是 `CORE_RESTRUCTURE_PLAN.md`；Phase 顺序、active phase、退出标准和 next 只以它为准。
3. 当前仓库级主线是 **CAD Agent vNext Migration**；Phase 9 单项 CAD Preview 已通过 `cad-session-host` 真实 readback 与 P9 Exit 门禁；Phase 10 Focused Harness Rehearsal 已完成真实 2-run closeout；Phase 11 ToolCard / Adapter Registry intake 已完成最小闭环；Phase 12 Mock Plugin Transaction 已完成 mock plugin-like transaction / rollback / committed_preview 闭环；Phase 13 Native Thin Backend 已完成 P13A skeleton、P13B preflight / launch packet、P13C authorization / execution receipt、P13D readiness / operator authorization request、P13E live spike gate 和 P13F minimal real native thin live spike。P13F evidence 为 `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`：AutoCAD Core Console + `NativeThinBackend.dll` 只写 `CODEX_PREVIEW` handle `2CF`，readback / bbox / layer / entity audit verified，rollback `rolled_back`，`savedCurrentDwg=false`，`cadGeometryVerified=true`。Phase 14 Engineering Kernel / BIM minimal DiffPackage 已完成，evidence 为 `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`：`engineering-kernel.diff-package` 只生成 no-CAD graph / DiffPackage，`cadWritesAttempted=false`，`nativePluginInvoked=false`，`cadGeometryVerified=false`，`cad_session_host` / DXF / geometry kernel / IFC 在该 closeout 中为 candidate / not_run。当前 PlanMD 暂未定义 P15；P13F / P14 不代表生产级 native plugin、训练恢复、表 C 推进、正式图层写入或业务 DWG 保存放行。
4. `docs/planning/任务清单.md` 只镜像当前 next，不承载第二套主计划。
5. `docs/migration/execution-ledger.md` 记录迁移执行事实、边界和验证状态。

旧架构归并成果只作为 `legacy mapping / evidence baseline`，不再定义 current next。

## 迁移期硬边界

vNext Migration 前段默认不恢复正式训练、不推进表 C、不做插件、不写真实 CAD、不沉淀系统资产大包。只有进入对应阶段且用户明确给出范围时，才允许打开这些链路。

文档治理、主线改旗、README 变清楚、审计通过或 no-CAD 测试通过，都不能说成 CAD 能力提升。

Protected evidence 默认不移动、不删除、不改写，除非有明确 ledger、引用闭合、用户授权和对应阶段：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG / DWT / 大型二进制 CAD 参考文件
- `agents/pipeline/pipeline_manifest.json`
- `config/entrypoint_custody_manifest.json`

根目录 `capability-map.html` 和 `capability-map-data.js` 是派生显示，不是训练事实源。

## 高风险入口索引

| 事项 / 口令 | 先读 | 当前默认 |
| --- | --- | --- |
| **继续迁移** / **vNext migration** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 默认查看 P14 minimal DiffPackage closeout 和剩余 not_run 项；先读取 P14 evidence、P13F live spike closeout、P13A-E closeout、P12/P11 closeout 和最新 P10 evidence |
| **Phase 4** / **规则压缩** | `CORE_RESTRUCTURE_PLAN.md` + `docs/planning/任务清单.md` | 作为已完成记录查看；不回灌长规则 |
| **Phase 5** / **vNext Contracts** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成记录查看：合同 skeleton、no-CAD roundtrip 和 read-only adapter 已收口 |
| **Phase 6** / **Legacy Gateway** | `CORE_RESTRUCTURE_PLAN.md` + `docs/governance/cad-agent-rules.md` | 作为已完成记录查看：legacy skeleton、validate / dry-run adapter、preview / readback registration guards 已收口 |
| **Phase 7** / **Evidence Ledger** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 skeleton-level 记录查看：Evidence Ledger 只记录证据包引用与裁判状态，不证明真实 CAD readback |
| **Phase 8** / **Workbench 只读化** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 closeout 查看；工作台只能展示 evidence / judge / blocked reason，不反向写事实源 |
| **Phase 9** / **单项 CAD Preview** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` + `docs/governance/cad-agent-rules.md` | 作为已完成 closeout 查看：`cad-session-host` 单项真实 preview/readback 已通过，P9 Exit `phase10Allowed=true` |
| **Phase 10** / **Focused Harness Rehearsal** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` + `docs/governance/cad-agent-rules.md` | 作为已完成 closeout 查看：P10B 真实 2-run live rehearsal 已 verified，`phase11Allowed=true`；不代表训练、表 C 或 native plugin 放行 |
| **Phase 11** / **ToolCard / Adapter Registry** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 closeout 查看：harness、`cad-session-host` 和 legacy preview/readback 已注册为 Tool Gateway 后的 adapter，CLI 越权 effect 会在后端前 blocked |
| **Phase 12** / **Mock Plugin Transaction** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 closeout 查看：mock plugin-like backend 已验证 transaction 字段、rollback / committed_preview 语义、ledger refs 和 mock / real proof 分离，仍不代表 native plugin |
| **Phase 13** / **Native Thin Backend** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 closeout 查看：P13F minimal real native thin live spike 已 verified；只证明 scoped `CODEX_PREVIEW` create/readback/rollback/no-save，不代表生产级插件或正式写图能力 |
| **Phase 14** / **Engineering Kernel / BIM** | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` | 作为已完成 minimal DiffPackage closeout 查看：`engineering-kernel.diff-package` 只证明 graph / DiffPackage / registry / harness route；生产级 IFC / DXF / cloud backend、多真实 live backend 同源对比仍为 not_run |
| **CAD 写入** / **真实 CAD** / **CAD 补验** | `docs/governance/cad-agent-rules.md` + `docs/runbooks/blocker-playbook.md` | 当前只允许明确 scoped CAD 回归或单项补验；默认仍只写 `CODEX_PREVIEW` 并 readback，不保存当前 DWG、不改正式图层 |
| **CAD 基础课** / **总设计师训练** | `docs/training/README.md` + `docs/training/cad-designer-growth-path.md` | 当前默认暂停正式训练；不得静默扩大为整批训练 |
| **真实 CAD 实力** / **推进表 C** / **刷新表 C** | `docs/planning/任务清单.md` + `CORE_STATUS.md` + `docs/status/current.md` | 当前阶段只解释 `Core Proof Coverage` 边界，不跑 coverage、不改 registry |
| **资产沉淀** / **资产复用** | `docs/architecture/system-asset-sedimentation-protocol.md` + `docs/governance/cad-agent-rules.md` + `core/assets/semantic_rules.py` | 不做系统资产大包；复用必须先查 registry 并保留 source spec / readback / no-save 边界 |
| **插件** / **原生插件** | `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` | P13F 已完成最小 scoped native thin live spike；生产级 native plugin、扩大范围、正式图层写入或保存能力仍需后续 gate |
| **根目录治理** / **清理候选** | `docs/migration/repo-inventory.md` + `docs/migration/root-cleanup-ledger.md` + `docs/migration/deletion-ledger.md` | 只按 ledger 看分类和候选；不得直接删除事实源 |

## CAD 安全速记

自然语言不得直接跳到 CAD。正式落图必须先形成结构化绘图意图或 `CAD_PLAN`，再走 validate、dry-run、`CODEX_PREVIEW`、created handles readback、bbox / layer / entity audit 和 closeout。

默认不保存当前 DWG，不覆盖原图，不修改正式图层，不清空全模型空间，不删除未被证据锁定的对象。任何 CAD 完成或准确性声明都必须说明 checked / not_checked。

## 长期规则归位

- 长期治理、CAD 写入、状态口径、模型桥和收口验证：`docs/governance/cad-agent-rules.md`
- 训练路由、Visual-First、`visual_parts`、`reference_match` 和案例训练边界：`docs/training/README.md`、`docs/training/cad-designer-growth-path.md`
- 系统资产沉淀、复用、native source 和 registry 边界：`docs/architecture/system-asset-sedimentation-protocol.md`
- 迁移执行事实、Phase closeout、根目录分类和未触碰边界：`docs/migration/execution-ledger.md`
