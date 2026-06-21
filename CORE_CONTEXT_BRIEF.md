# Core Context Brief

最后更新：2026-06-21。本文是新会话短上下文入口，不是状态库、计划库或历史库。若 `AGENTS.md` 已自动加载，从本文开始恢复；普通任务只按“按需展开”追加 1-2 个文件。

## 当前一句话

本仓库正在执行 **CAD Agent vNext Migration**：旧仓库作为 `Legacy Core + Evidence Harness` 保留真实 CAD 证据链，迁移目标是逐步建立中立工程数据内核、Agent Runtime、Tool Gateway、Governance Plane、Evidence Ledger 和 Workbench。

## 当前 next

Phase 8 已通过 **Workbench 只读化 closeout**。Phase 9 已完成单项 preview scope lock / preflight / runner、CAD-open direct COM blocker 归档、P9B Harness Result Contract、P9C Preview Bundle Pilot、P9 Exit Gate Guard，以及 CAD Session Host 根因修复；P9 Exit gate 输出 `phase10Allowed=true`。P10B focused live rehearsal 已 verified closeout，最新 P10 evidence 为 `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`：runCount=2、run_01 / run_02 均 `geometry_verified` / `verified`、backend `cad_session_host`、created/readback count 均为 4、全部在 `CODEX_PREVIEW`、`savedCurrentDwg=false`、`stableGeometry=true`、`diffCount=0`、`failureCount=0`、`phase10CloseoutAllowed=true`、`phase11Allowed=true`。P11 ToolCard / Adapter Registry intake 已完成最小闭环。P12 Mock Plugin Transaction 已完成最小闭环。P13A Native Thin Backend skeleton、P13B scoped spike preflight / launch packet、P13C live spike authorization gate / execution receipt、P13D readiness / operator authorization request、P13E minimal live spike execution gate / external_blocker closeout 均已完成。P13F minimal real native thin backend live spike 已完成：新增 `native-thin.live-spike` adapter 与 `native-thin-live-spike` harness command，真实 AutoCAD Core Console 加载 `NativeThinBackend.dll`，只写一个 `CODEX_PREVIEW` scoped preview polyline，created handle `2CF` 已 readback，bbox `[100,200,0]` -> `[1300,800,0]`，entity `LWPOLYLINE`，rollback `rolled_back`，`savedCurrentDwg=false`，证据为 `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`。P14 Engineering Kernel / BIM minimal DiffPackage 已完成：新增 `engineering-kernel.diff-package` registered adapter 与 harness `engineering-kernel-diff`，生成 task / geometry / semantic / version / evidence graphs 和 DiffPackage；机器证据为 `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`，closeout `ready` / `not_verified`，`cadWritesAttempted=false`、`nativePluginInvoked=false`、`savedCurrentDwg=false`、`cadGeometryVerified=false`，只消费 P13F source，`cad_session_host` / DXF / geometry kernel / IFC 在该 closeout 中为 candidate / not_run。`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 等泛化越权 effect 仍在后端前 fail-closed。当前 PlanMD 暂未定义 P15；训练、表 C、生产级 native plugin、正式图层写入和业务 DWG 保存仍未放行。

## 活跃事实

- **Phase ledger**：Phase 0-8 的 closeout、Phase 9 CAD-open blocker、CAD Session Host 根因修复、真实 readback closeout、P9 Exit、P10 focused live rehearsal closeout、P11 adapter registry intake、P12 mock plugin transaction、P13A native skeleton、P13B native preflight / launch packet、P13C native authorization / execution receipt、P13D readiness / operator authorization request、P13E minimal live spike execution gate / external_blocker closeout、P13F minimal real native live spike closeout 与 P14 Engineering Kernel / BIM minimal DiffPackage closeout 事实见 `docs/migration/execution-ledger.md`。
- **Root governance**：根目录分类、移动记录和删除候选见 `docs/migration/repo-inventory.md`、`docs/migration/root-cleanup-ledger.md` 和 `docs/migration/deletion-ledger.md`；没有实际删除文件。
- **AGENTS.md**：只保留默认中文、启动顺序、vNext / Phase 9 路由、protected evidence 硬边界和高风险入口索引；长期规则见 `docs/governance/cad-agent-rules.md`、`docs/training/README.md`、`docs/training/cad-designer-growth-path.md`、`docs/architecture/system-asset-sedimentation-protocol.md` 和 `docs/migration/execution-ledger.md`。
- **当前施工区**：`C:\Users\User\Desktop\CAD Agent WorkTree`，分支 `vnext-main`。
- **外部母标准**：用户侧 `CAD_AGENT_vNext_v2_2_FINAL.docx` 是迁移期 authority source；当前 worktree 中未跟踪该 Word 文件。
- **RFC source**：`docs/rfcs/vnext-super-cad-agent-architecture.md` 与 `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` 是 Target Architecture RFC source；它们不直接替代 PlanMD，也不定义 current next。
- **Legacy mapping**：上一阶段架构归并成果不再定义当前 next；旧映射见 `docs/architecture/system-architecture-convergence.md`。
- **唯一 PlanMD**：`CORE_RESTRUCTURE_PLAN.md`。
- **训练和表 C**：训练事实源、coverage JSON、registry、projects、libraries 和 output 仍是 protected evidence；本阶段不恢复训练、不推进表 C。
- **P11-P14 tool registry**：`core/contracts/adapter_registry.py` 只做注册、授权、既有 harness result / mock transaction / native skeleton / authorization packet / readiness authorization request / P13E live spike gate / P13F scoped live spike / P14 engineering-kernel diff 消费；CLI `--requested-effect` 越权会 fail-closed。P13F 只允许 `native_thin_scoped_live_spike_execute` 等窄 effect，通过 `native-thin.live-spike` 执行 `CODEX_PREVIEW` scoped write + readback + rollback + no-save；P14 只允许 graph / diff / candidate profile 写入，不执行 CAD 或 plugin；泛化 `native_plugin_execute` / `cad_execute` / `real_cad_readback` / `dwg_save` / `formal_layer_write` 仍 blocked。

## 不能声称

- 不能把文档治理、主线改旗、README 变清楚说成 CAD 能力提升。
- 不能用表 C、截图、dry-run、no-CAD benchmark、模型 pass、工作台页面或旧 coverage 百分比证明端到端 CAD 能力。
- 不能把 Target Architecture RFC、skeleton-level Evidence Ledger 或 Workbench projection / readonly adapter 写成 Tool Gateway、生产级 Evidence Ledger、完整 Workbench 产品、Phase 9 真实 preview/readback 已几何验证或插件已经落地。
- 不能默认保存、覆盖、删除 DWG，不能修改正式图层；真实 CAD 默认只写 `CODEX_PREVIEW` 并需要 readback。

## 主从关系

- `CORE_RESTRUCTURE_PLAN.md` 是唯一 PlanMD。
- `docs/planning/任务清单.md` 只镜像当前 vNext migration next，不承载第二套主计划。
- `docs/migration/execution-ledger.md` 记录迁移执行事实和验证状态。
- `docs/governance/cad-agent-rules.md` 继续承载长期治理规则；`AGENTS.md` 只作为启动路由器和高风险边界索引。
- `docs/training/training-sources.json` 是训练事实源；工作台和 sync report 只是派生显示。
- `output/validation_runs/**`、`projects/**`、`libraries/**` 和 registry 是 protected evidence，本阶段不移动、不删除、不改写。

## 按需展开

| 目标 | 先读 |
| --- | --- |
| vNext 迁移当前主线 | `CORE_RESTRUCTURE_PLAN.md` + `docs/migration/execution-ledger.md` |
| Phase 0 盘点口径 | `docs/migration/execution-ledger.md` 的 Phase 0 摘要 |
| 目标系统 RFC | `docs/rfcs/vnext-super-cad-agent-architecture.md` |
| 工具层 / 原生插件 RFC | `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` |
| 旧架构归并映射 | `docs/architecture/system-architecture-convergence.md` |
| 长期治理规则 | `docs/governance/cad-agent-rules.md` |
| 文档治理 / 反膨胀 | `docs/governance/arch-doc-governance-boundary-package.md` + `scripts/run_doc_governance_audit.py` |
| 训练边界 | `docs/training/README.md` + `docs/training/cad-designer-growth-path.md` |
| 资产沉淀 / 复用 | `docs/architecture/system-asset-sedimentation-protocol.md` + `core/assets/semantic_rules.py` |
| 完整能力状态 | `CORE_STATUS.md` + `docs/status/current.md` + coverage JSON |
| 历史 / 风险 / 交接 | `docs/status/changelog.md` / `docs/status/issues.md` / `docs/handoffs/current.md` |

## 常用验证

Phase 10 / Phase 9 回归轻量验证优先：

```powershell
git diff --stat
$py -m unittest tests.core.test_phase10_rehearsal tests.core.test_cad_session_host tests.core.test_cad_agent_harness tests.core.test_phase9_single_preview tests.core.test_phase9_exit_gate tests.core.test_phase9_preview_bundle -v
$py -m unittest tests.core.test_vnext_contracts tests.core.test_vnext_contract_roundtrip tests.core.test_vnext_contract_adapters tests.core.test_legacy_gateway tests.core.test_legacy_gateway_adapters tests.core.test_legacy_gateway_preview_readback tests.core.test_evidence_ledger tests.core.test_workbench_projection tests.core.test_workbench_readonly_adapter -v
```

文档治理审计可按需运行：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py --fail-on-findings
```

未运行的验证必须标 `not_run`。P13 Native Thin Backend 最小 scoped live spike 已完成并有真实 Core Console / plugin evidence；它只证明一个最小 `CODEX_PREVIEW` 对象的 native thin create/readback/rollback/no-save 闭环，不替代训练、表 C、生产级 native plugin、正式图层或业务 DWG 保存能力。P14 minimal DiffPackage 已完成 no-CAD 合同 / registry / harness route；真实多 backend 同一 CAD_PLAN live 对比、生产级 IFC / DXF / cloud backend 仍为 not_run。
