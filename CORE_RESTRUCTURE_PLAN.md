# CAD Agent vNext Migration PlanMD（唯一主线）

最后更新：2026-06-21

状态：vNext migration router。用户说 `plan.md`、主计划、主 PlanMD、开发主线，默认指这里。本文只保留当前与后续可施工路线；已完成阶段和证据流水只看 `docs/migration/execution-ledger.md`。

## 0. 本文职责

- 定义当前 active gate、后续 gate 顺序、进入条件、退出标准和禁止项。
- 保持 `README.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md` 主线一致。
- 把 CLI-Anything / agent-native CLI harness 吸收为 Tool Layer 实现规范，不替代既有 Agent Runtime / Tool Gateway / Evidence Ledger / Workbench。
- 保护旧仓库真实 CAD 证据链，防止文档治理、harness 包装、fake backend 或截图被说成 CAD 能力提升。
- 任何新增待办、优先级调整或阶段切换，先改本文，再同步辅助文档。

## 1. 当前定位

| 项 | 当前口径 |
| --- | --- |
| 当前主线 | CAD Agent vNext Migration |
| 当前 active gate | P14 Engineering Kernel / BIM minimal DiffPackage 已 closed；PlanMD 暂未定义 P15（P13 Native Thin Backend minimal scoped spike 已 closed；P12/P11/P10 均已完成） |
| 当前 blocked reason | 无 active blocker；生产级 IFC / DXF / cloud backend、多真实 live backend 同一 CAD_PLAN 对比、训练恢复、表 C 推进和正式图层 / 业务 DWG 写入仍为 not_run。 |
| 最新有效证据 | P14 no-CAD Engineering Kernel DiffPackage closeout：`output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`；P14 adapter / harness tests；P13F minimal native thin live spike verified：`output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`；P13F adapter / harness tests；P13E/P13D/P13C/P13B/P13A 单测；P12 mock plugin transaction 单测；P11 registry / CLI 越权拦截单测；P10B verified closeout：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/` |
| 当前未满足 | P14 closeout 只证明 no-CAD graph / DiffPackage 合同、registered adapter、harness route 和候选 backend docs；真实 P14 evidence 只消费 P13F native-thin source，`cad_session_host` / DXF / geometry kernel / IFC 在该 closeout 中为 candidate / not_run。P13F 只证明最小 scoped native thin create/readback/rollback/no-save 闭环，不证明生产级 native plugin、训练恢复、表 C 推进、正式图层写入或业务 DWG 保存能力。 |
| 当前禁止 | 默认不恢复训练、不推进表 C、不保存业务 DWG、不写正式图层；不得把 P14 no-CAD DiffPackage 解释为新的 `geometry_verified`、生产级 BIM / DXF export、cloud backend 或扩大 native spike scope 的放行。 |

## 2. 已完成基线

已完成内容只作为基线，不再承载施工待办：Baseline / 主线改旗 / RFC 归位 / 根目录治理 / 规则压缩 / vNext Contracts / Legacy Gateway / Evidence Ledger skeleton / Workbench 只读化 / Phase 9 单项 CAD Preview / Phase 10 Focused Harness Rehearsal / Phase 11 ToolCard Adapter Registry / Phase 12 Mock Plugin Transaction / Phase 13A Native Thin Backend Skeleton / Phase 13B preflight launch packet / Phase 13C authorization gate and execution receipt / Phase 13D readiness and operator authorization request / Phase 13E minimal live spike execution gate / Phase 13F minimal real native thin live spike，均以 `docs/migration/execution-ledger.md` 为执行事实源。

可复用成果：`TaskObject`、`ToolContract`、`ToolCard`、`EvidencePackage`、`CompletionJudge` skeleton；validate / dry-run / `CODEX_PREVIEW` / readback legacy adapter；ledger-aware fail-closed；Workbench 只读投影；`cad-session-host` 作为 Phase 9/10 的默认真实 CAD bridge；P11 `AdapterRegistry` 能注册 adapter、消费 harness result，并在后端前拦截 forbidden effects；P12 `mock-plugin.transaction` 验证 transaction / rollback / committed_preview 语义和 mock / real proof 分离；P13A-P13E `native-thin.backend` 记录 native skeleton transaction、no-save audit、rollback proof、scope/preflight/launch packet、authorization gate、execution receipt、readiness packet、operator authorization request、live spike execution gate 与 external_blocker closeout；P13F `native-thin.live-spike` 已通过 AutoCAD Core Console + native DLL 完成一个 `CODEX_PREVIEW` polyline 的 created handles readback、bbox/layer/entity audit、rollback proof 和 no-save audit；P14 `engineering-kernel.diff-package` 已能生成 task / geometry / semantic / version / evidence graphs 和 DiffPackage，比较 P13F source 与 COM / DXF / geometry kernel / IFC candidates。不可夸大：P13F / P14 仍不证明训练恢复、表 C 推进、生产级 native plugin、生产级 BIM / DXF、正式图层写入或业务 DWG 保存能力。

## 3. 不可破坏边界

| 边界 | 固定要求 |
| --- | --- |
| 事实源保护 | 不删除、不移动、不改写 `output/**`、`projects/**`、`libraries/**`、registry、training-sources、OpenSpec active changes 和历史失败教训，除非有 ledger、引用闭合和用户授权。 |
| CAD 执行 | 白话不得直接落 CAD；必须先有结构化意图或 `CAD_PLAN`，再走 validate、dry-run、`CODEX_PREVIEW`、created handles readback。 |
| 写入安全 | 默认不保存业务 DWG、不覆盖原图、不删未证据锁定对象、不改正式图层；局部错误优先 `repair_plan`。 |
| CLI Harness | 只能位于 Tool Gateway 后、具体后端前；CLI 输出只是 EvidencePackage 输入，不能绕过 ToolContract / EvidenceLedger / CompletionJudge。 |
| 状态口径 | install / probe / dry-run / fake / screenshot / model pass / CLI return code 均不能证明 `geometry_verified`。 |
| 训练 / 表 C / 插件 | 只能按后续 gate 进入；P9 期间默认暂停。 |

## 4. CLI-Anything 吸收决策

参考 [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)、[HARNESS.md](https://github.com/HKUDS/CLI-Anything/blob/main/cli-anything-plugin/HARNESS.md) 和 [Preview Protocol](https://github.com/HKUDS/CLI-Anything/blob/main/docs/PREVIEW_PROTOCOL.md)，本仓库只吸收工具层习惯：

- 后端能力包装成 agent-native CLI：稳定子命令、默认 `--json`、可安装、可测试、可发现。
- 真实软件后端留在闭环里：final proof 必须来自真实 CAD backend 或明确 native backend。
- producer / consumer 分离：CAD adapter 只发布 preview / readback 证据；Workbench / viewer 只读消费。
- preview bundle / session / trajectory：逐步输出 `manifest.json`、`summary.json`、`artifacts/`、`session.json`、`trajectory.json`，但完成声明仍只看 CompletionJudge。

不吸收：CLI 不解析自然语言、不编排任务、不决定保存 / 删除 / 正式图层写入、不以安装成功证明能力、不把 FreeCAD 的 file-backed 状态假设直接套到 AutoCAD 活动 DWG。

## 5. 可施工 Gate 路线

| Gate | 名称 | 目标 | 主要产物 | 退出条件 |
| --- | --- | --- | --- | --- |
| P9A | Live CAD 接管与 blocker 解除 | 复用单项 `CODEX_PREVIEW` CAD_PLAN，只接管既有 AutoCAD 活动对象 | readiness probe、preview report、blocked / verified EvidencePackage、CAD Session Host | completed；`cad-session-host` 单线程 bridge 完成 preview write + created handles readback，P9 Exit `phase10Allowed=true` |
| P9B | Harness Result Contract | 在不扩大 CAD scope 的前提下，把现有 runner 输出收成 CLI-harness-compatible JSON | `cad-agent-harness-result/v1` schema、thin CLI facade、unit tests | completed；validate / dry-run / probe / preview / readback / evidence 命令可 JSON 输出，fake backend 永远 `not_verified` |
| P9C | Preview Bundle Pilot | 将 P9 run dir 同步写成轻量 preview bundle，供人和 Agent 只读检查 | `manifest.json`、`summary.json`、`artifacts/`、`session.json`、`trajectory.json` | completed；bundle 路径稳定、artifact 相对路径有效，EvidencePackage ref 可追溯；不可追踪 artifact 必须显式 warning；不替代 readback |
| P9 Exit | 单项 CAD Preview 完成门 | 合并 P9A/B/C，完成一次真实单项 preview | `phase9_exit_gate.py`、harness `exit-gate`、ledger entry、judge decision、task list sync | gate evaluator completed；仍 blocked until `geometry_verified=true`、`savedCurrentDwg=false`、`missingEvidence=[]`、CompletionJudge `checked_evidence` 覆盖 `real_cad_readback` / `no_save_guard` 且 `can_claim_complete=true` |
| P10 | Focused Harness Rehearsal | 用同一 ToolContract / harness 入口重复跑一个家具族或点名能力，验证稳定性 | `phase10_rehearsal.py`、harness `rehearsal-scope-proposal` / `rehearsal-plan` / `rehearsal-scope-receipt` / `rehearsal-preflight` / `rehearsal-run` / `rehearsal-result` / `rehearsal-closeout`、多 run EvidencePackage、diff summary、failure ledger | completed；`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/` 通过 2-run live rehearsal：run_01 / run_02 均 `geometry_verified`、`savedCurrentDwg=false`、created/readback count 均为 4、diffCount=0、failureCount=0、`phase10CloseoutAllowed=true`、`phase11Allowed=true`；不是整批训练 |
| P11 | ToolCard / Adapter Registry | 把 harness 作为 Tool Gateway 后的 registered adapter，而不是散脚本 | ToolCard、allowed / forbidden effects、adapter registry tests | completed；`core/contracts/adapter_registry.py` 注册 harness / `cad-session-host` / legacy adapter，harness result 可经 registry 消费，CLI `--requested-effect` 越权在后端执行前 fail-closed |
| P12 | Mock Plugin Transaction | 用 mock plugin-like backend 验证事务字段和 rollback / committed_preview 语义 | mock backend、transaction tests、ledger refs | completed；`mock-plugin.transaction` 已接入 Adapter Registry / harness，success / failure / rollback success / rollback failure / blocked 均有 proof status，mock 不满足 `real_cad_readback` |
| P13 | Native Thin Backend | 将原生插件 thin backend 包在 harness 后，只做确定性 preview create / readback / rollback | thin backend adapter、rollback proof、no-save audit、preflight launch packet、authorization gate、execution receipt、readiness authorization request、minimal live spike execution gate、minimal real live spike evidence | completed；P13A-E 合同链已完成，P13F 已通过 `native-thin.live-spike` 在 AutoCAD Core Console 中完成一个 `CODEX_PREVIEW` scoped object 的 created handle readback、bbox/layer/entity audit、rollback 和 no-save closeout |
| P14 | Engineering Kernel / BIM | 扩展任务图、几何图、语义图、版本图和证据图，多后端共享合同 | DiffPackage、kernel adapter、IFC / DXF / cloud candidate docs | completed（minimal）；`engineering-kernel.diff-package` 已注册为 no-CAD adapter，harness `engineering-kernel-diff` 走 registry，单测覆盖同一 CAD_PLAN 的 COM / plugin / DXF / kernel / IFC candidate diff；真实 closeout 只消费 P13F source，COM / DXF / geometry kernel / IFC 在本轮为 candidate / not_run |

## 6. P9 细化施工包

P9A 已完成：旧的直接 COM 入口在用户确认 CAD 已打开后仍出现“进程可见但活动 COM / ROT 不可接管”，因此补入 `CAD Session Host` 作为长期真实 CAD bridge。Host 默认只绑定 `127.0.0.1`、必须 `CAD_SESSION_TOKEN`、单线程处理 AutoCAD COM STA 请求、只允许 `CODEX_PREVIEW` 写入。最新真实证据为 `output/validation_runs/phase9-session-host-live-verify-20260619-235547/`：`cadGeometryVerified=true`、created/readback handles 均为 4、`savedCurrentDwg=false`，P9 Exit `phase10Allowed=true`。

P9B 已完成：入口为 `scripts/cad_agent_harness.py`，核心实现为 `core/contracts/cad_agent_harness.py`；命令限定 `validate`、`dry-run`、`probe`、`preview`、`readback`、`evidence`；默认 `saveAllowed=false`、`deleteAllowed=false`、`formalLayersAllowed=false`、`connectExistingOnly=true`。`preview` 默认 backend 已切换为 `cad-session-host`；旧 `autocad-com-existing` 仅保留为显式诊断 / 兼容路径。

P9C 已完成：入口为 `build_phase9_preview_bundle()` 与 harness `bundle` 命令；默认在 run dir 下写 `preview_bundle/manifest.json`、`summary.json`、`artifacts/`、`session.json`、`trajectory.json`。bundle producer 只整理既有 P9 run artifacts，consumer 是 Workbench / viewer；consumer 不渲染、不写事实源、不补造证据；若 report artifact 不在 source run dir 或不存在，bundle 必须输出 `artifact_source_not_traceable:*` warning。P9 Exit gate 也已固化并通过：入口为 `evaluate_phase9_exit_gate()` 与 harness `exit-gate` 命令；最新 run 的 `cadGeometryVerified=true`、`savedCurrentDwg=false`、`missingEvidence=[]`、created handles / readback entities 均存在，且 CompletionJudge `checked_evidence` 覆盖 `real_cad_readback` / `no_save_guard`、`missing_evidence=[]`、`can_claim_complete=true`，因此 `phase10Allowed=true`。

P10B scope proposal contract 已完成：入口为 `build_phase10_rehearsal_scope_proposal()` 与 harness `rehearsal-scope-proposal` 命令；只读取 ready P9 Exit run、`phase9_preview_report.json` 与 source CAD_PLAN，输出 `phase10_rehearsal_scope_proposal.json` 和未确认的 `candidateScope`。proposal 固定 `scopeConfirmed=false` / `liveRunsConfirmed=false` / `cadWritesAttempted=false`，只能作为 operator scope review 入口；它不生成 receipt、不连接 AutoCAD、不执行 preview、不写实体，也不能替代用户点名确认。

P10A 已完成：入口为 `prepare_phase10_rehearsal_plan()` 与 harness `rehearsal-plan` 命令；只生成 `phase10_rehearsal_scope.json` / `phase10_rehearsal_plan.json`，不连接 CAD、不执行 preview、不写实体。P10A 强制 `scopeConfirmed=true`、引用 ready 的 P9 Exit run、`runCount>=2`、全部 CAD_PLAN 只写 `CODEX_PREVIEW`，且 backend 必须是 `cad-session-host` / `cad_session_host`。

P10B result aggregate contract 已完成：入口为 `evaluate_phase10_rehearsal_runs()` 与 harness `rehearsal-result` 命令；只读取已有 run dir 的 `phase9_preview_report.json`，生成 `phase10_rehearsal_result.json`、`phase10_rehearsal_diff_summary.json` 与 `phase10_rehearsal_failure_ledger.json`。它要求至少 2 个 run、全部 `verified` / `geometry_verified`、`savedCurrentDwg=false`、created/readback count 大于 0、backend 为 `cad_session_host`、全部 readback 在 `CODEX_PREVIEW`，且几何签名稳定；任一 run 保存 DWG、缺 readback、非 preview 图层、fake backend 或几何漂移均 blocked。最新 P10B live rehearsal 已由 `rehearsal-result` 收口稳定性 diff / failure ledger：`diffCount=0`、`failureCount=0`。

P10B scope receipt contract 已完成：入口为 `build_phase10_rehearsal_scope_receipt()` 与 harness `rehearsal-scope-receipt` 命令；只消费 ready 的 `phase10_rehearsal_plan.json`，生成 `phase10_rehearsal_scope_receipt.json`，记录用户已点名的 scope、plan hash、runSpecs、`CODEX_PREVIEW` / no-save / repeated live run 确认声明。receipt 本身不连接 CAD、不执行 preview、不写实体；缺确认声明、未 `--confirm-live-runs`、plan 非 ready 或后续 plan hash / runSpecs 漂移时，preflight / run / closeout 均 fail-closed。

P10B live-run gate contract 已完成：入口为 `execute_phase10_rehearsal_plan()` 与 harness `rehearsal-run` 命令；只消费 ready 的 `phase10_rehearsal_plan.json` 和匹配的 `phase10_rehearsal_scope_receipt.json`，默认缺 receipt、缺 `--confirm-live-runs`、缺 `CAD_SESSION_HOST_URL` / `CAD_SESSION_TOKEN` 时 blocked，runSpec 非 preview / 非真实 backend / 非 `CODEX_PREVIEW` 时 blocked。它本身不替用户选择 scope；真实 live runs 仍必须由用户点名 scope 后，通过 `cad-session-host` 写 `CODEX_PREVIEW` 并 readback。

P10B launch preflight contract 已完成：入口为 `build_phase10_rehearsal_launch_packet()` 与 harness `rehearsal-preflight` 命令；只读取 ready 的 `phase10_rehearsal_plan.json`、匹配的 scope receipt 和 session-host env 状态，生成 `phase10_rehearsal_launch_packet.json` 与可审计 `rehearsal-run --scope-receipt ... --confirm-live-runs` argv。preflight 即使 ready 也保持 `cadWritesAttempted=false`，不调用 preview executor、不创建 run dir、不连接 AutoCAD；它只说明“如果用户点名 scope、receipt 匹配且 host env 齐备，下一步可启动 live rehearsal”。

P10B closeout gate contract 已完成并加固：入口为 `evaluate_phase10_rehearsal_closeout()` 与 harness `rehearsal-closeout` 命令；只消费既有 `phase10_rehearsal_scope_receipt.json`、`phase10_rehearsal_launch_packet.json`、`phase10_rehearsal_execution.json` 与 `phase10_rehearsal_result.json`。closeout 只有在 scope receipt ready、launch ready、execution 为 production harness preview executor、`cadWritesAttempted=true`、result verified / stable geometry、无 blockers / missing evidence，且 `scopeReceiptPath`、`planHash`、`planPath`、`outputDir`、`runSpecs`、`runDirs`、run count、`resultPath` 与 aggregate result 彼此一致时才允许 `phase10CloseoutAllowed=true` / `phase11Allowed=true`。closeout 本身不连接 AutoCAD、不执行 preview、不写实体；缺 receipt、stale receipt、injected executor artifact、foreign / mixed artifact 和非 object JSON artifact 不能作为生产 closeout proof。

P10B live rehearsal 首次真实校验已收口为 external blocker：用户明确 CAD 已打开并要求真实校验后，本轮按 P9 ready evidence 收束出的默认候选 `table / single_table_preview_repeatability` 尝试启动 2-run live rehearsal。`cad-session-host` 在 `output/validation_runs/phase10-scope-confirmed-live-rehearsal-20260620-015727/` 成功启动并响应 `/rpc status`，但返回 `ready=false`，blocker 为无可接管活动 `AutoCAD.Application` / ROT 对象；status 同时确认 `acadProcessRunning=true` 且 `Dispatch fallback skipped because connect_existing_only=True`。该轮 `cadWritesAttempted=false`，未生成 preview write、created handles、readback、bbox / layer / entity audit、result aggregate 或 closeout proof，因此该轮 P10B blocked、Phase 11 不放行；后续 fast closeout live rehearsal 已解除该 blocker 并完成 P10B closeout。

P10B COM attach deep fix 已完成代码侧加固；该包当时的真实环境仍 blocked：`AutoCADComDriver(connect_existing_only=True)` 现在先尝试 versioned `GetActiveObject`，再尝试 `GetObject(Class=...)`，最后枚举 Running Object Table，并支持从 document-like ROT 对象回溯 `.Application`；session host status 会返回 `attachDiagnostics` 与稳定 `blockerCode`，且仍禁止在 existing-only 模式下 `Dispatch` 新 AutoCAD。该包 no-write readiness probe 为 `output/validation_runs/phase10-com-attach-hardened-readiness-20260620-021746/cad_session_host_readiness_summary.json`：host 可启动并响应，`hostReady=false`，`acadProcessRunning=true`，`ROT inspected=0`，`blockerCode=acad_process_running_without_visible_rot_object`，`cadWritesAttempted=false`。同目录 `independent_getactiveobject_probe.txt` 也显示 PowerShell `Marshal.GetActiveObject("AutoCAD.Application.25/25.1")` 返回 `MK_E_UNAVAILABLE`；该 blocker 已在后续 fast closeout live rehearsal 中解除并完成 P10B closeout。

P10B CAD reopened readiness retry 已完成 no-write 复验：用户再次说明 CAD 已打开后，本轮新建 `output/validation_runs/phase10-cad-reopened-readiness-20260620-023225/` 并只轮询 `cad-session-host` `/rpc status` 与独立 PowerShell `GetActiveObject` 探针。Host 成功启动并响应，`hostReady=false`、`acadProcessRunning=true`、`ROT inspected=0`、`blockerCode=acad_process_running_without_visible_rot_object`、`cadWritesAttempted=false`；独立探针对 `AutoCAD.Application.25.1` / `.25` 仍返回 `MK_E_UNAVAILABLE`，裸 `AutoCAD.Application` 仍为 `CO_E_CLASSSTRING`。该轮证明当时 Windows / AutoCAD COM 可见性、注册或同权限会话仍 blocked；后续 fast closeout live rehearsal 已重新接管活动 AutoCAD 对象并完成 P10B closeout。

P10B fast closeout live rehearsal 已完成 verified 收口：在用户授权 AutoCAD / registry / `D:\Design\CAD` 全权限操作后，本轮先从桌面配置包恢复 AutoCAD profile registry + AppData 文件，再修复 CAD-MCP stale COM reference 自愈，随后用 `cad-session-host` 接管当前 AutoCAD 活动对象。预备 run `output/validation_runs/phase10-fast-closeout-host-preview-20260620-0418/` 通过 P9 exit gate：`phase10Allowed=true`。正式 P10B run 目录为 `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`：scope `phase10.table.rehearsal` / `table` / `single_table_preview_repeatability` / `runCount=2` / backend `cad-session-host`；`rehearsal-plan`、`rehearsal-scope-receipt`、`rehearsal-preflight`、`rehearsal-run`、`rehearsal-result`、`rehearsal-closeout` 均已生成对应 artifact。run_01 与 run_02 均为 `geometry_verified` / `verified`，`driverBackend=cad_session_host`，`savedCurrentDwg=false`，created/readback count 均为 4，全部 readback 在 `CODEX_PREVIEW`，bbox size 均为 `900.0 x 450.0`；aggregate `stableGeometry=true`、`diffCount=0`、`failureCount=0`、`blockingReasons=[]`、`missingEvidence=[]`；closeout `phase10CloseoutAllowed=true`、`phase11Allowed=true`、`sourceCadWritesAttempted=true`。收尾时本轮 `cad-session-host` 已停止，AutoCAD 程序保留运行，未保存任何当前 DWG；该结论仍不恢复训练、不推进表 C、不证明 native plugin 可用。

P11 ToolCard / Adapter Registry intake 已完成最小闭环：新增 `core/contracts/adapter_registry.py`，将 harness commands、`cad-session-host.preview/readback`、legacy preview/readback 等路径登记为 `RegisteredAdapter`，每个 adapter 都有 `ToolCard`、`ToolContract`、allowed / forbidden effects、entrypoint、backend、evidence boundary 与是否执行 CAD 的显式字段。`cad_agent_harness` CLI 现在在加载 plan / run dir 或调用任何后端前先走 registry authorization；新增 `--requested-effect` / `--adapter-id` 供审计和负向测试使用，越权 effect（如 `dwg_save`、`save_current_dwg`、`formal_layer_write`、训练 / 表 C / plugin mutation）会返回 blocked JSON，不写 result artifact。P11 还提供 harness result consumption：`rehearsal-result` / `rehearsal-closeout` 只能作为既有 readback proof 消费，不触发新 CAD、不保存 DWG、不推进训练、表 C 或 native plugin。

P12 Mock Plugin Transaction 已完成最小闭环：新增 `core/contracts/mock_plugin_transaction.py`，以 `mock-plugin.transaction` adapter 验证 plugin-like transaction 合同字段：`transactionId`、`rollbackRequired`、`rollbackStatus`、`committedPreview`、`createdHandles` / `createdHandlesRef`、`blockedReason`、`retryable`、`documentState` 与 `ledgerRefs`。harness 新增 `mock-plugin-transaction` 命令，仍先走 P11 registry authorization；`plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save` 等 effect 会在后端前 blocked。P12 只产出 mock evidence：success / failure / rollback_success / rollback_failed / blocked 均有 `proofStatus`，但 `cadGeometryVerified=false`，EvidencePackage 不满足 `real_cad_readback`，不连接 AutoCAD、不调用 native plugin、不写真实 CAD。

P13A Native Thin Backend skeleton 已完成最小合同层：新增 `core/contracts/native_thin_backend.py` 与 `native-thin.backend` adapter，复用 P12 transaction 字段并补 `noSaveAudit`、`rollbackProof`、`nativePluginInvoked=false`、`previewStrategy=memory_transaction`。harness 新增 `native-thin-backend` 命令，仍先走 registry authorization；`native_plugin_execute`、`plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save` 等 effect 在 backend 前 blocked。P13A 只证明合同、ToolCard、EvidencePackage 和 CompletionJudge 后的 skeleton 路径，不连接 AutoCAD、不调用真实 native plugin、不生成 real CAD readback、不 claim `geometry_verified`。

P13B Native Thin Backend preflight / launch packet 已完成 no-CAD / no-plugin 合同层：`build_native_thin_backend_scope_receipt()` 要求 scope confirmation、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard 和 backend identity；`build_native_thin_backend_launch_packet()` 只生成 ready / blocked JSON packet，`cadWritesAttempted=false`、`nativePluginInvoked=false`、`liveExecutionAuthorized=false`。真实 native backend live spike 仍需用户单独授权。
P13C Native Thin Backend authorization gate / execution receipt 已完成 no-CAD / no-plugin 合同层：`build_native_thin_backend_authorization_gate()` 消费 P13B ready launch packet，要求用户显式确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity 与 launch packet hash；缺授权、scope/hash 漂移或越权 effect 均 fail-closed。`build_native_thin_backend_execution_receipt()` 只消费 ready authorization gate，记录 scoped execution receipt，仍固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`executionStarted=false`、`cadGeometryVerified=false`。该 P13C closeout 当时未启动真实 live spike；该历史风险已由 P13F minimal real live spike closeout 覆盖。
P13D Native Thin Backend readiness / operator authorization request 已完成 no-CAD / no-plugin 合同层：`build_native_thin_backend_readiness_packet()` 消费 P13C ready execution receipt，校验 scope、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard、backend identity、launch packet hash 与 authorization receipt hash；输出只能是 `blocked` 或 `ready_for_user_authorization`，并固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`executionStarted=false`、`cadGeometryVerified=false`。`native-thin-backend --native-backend-mode readiness` 仍先走 registry authorization；`native_plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write` 等 effect 在后端前 blocked。P13D readiness 不是 real CAD verified；真实 native backend live spike 仍必须停下来等待用户单独授权。

P13E Native Thin Backend minimal live spike execution gate 已完成 gate / blocker closeout 合同层：`build_native_thin_backend_live_spike_execution_gate()` 消费 P13D readiness packet / `operatorAuthorizationRequest`，要求 operator 单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash。缺授权或 hash 漂移返回 `blocked / missing_authorization`；授权完整但缺真实环境返回 `external_blocker`；`native-thin-backend --native-backend-mode live_spike_gate --readiness-packet ...` 仍先走 registry authorization。该 gate 固定 `cadWritesAttempted=false`、`nativePluginInvoked=false`、`executionStarted=false`、`cadGeometryVerified=false`，并记录 created handles readback / bbox / layer / entity audit、rollback proof、no-save audit 的 `not_run_no_execution` / `not_run_no_cad` 边界。P13E gate / blocker closeout 不是插件可用证明，也不是 real CAD verified；其当时的真实 live spike 未启动风险已由 P13F minimal real live spike closeout 在最小 scoped 范围内覆盖。

P13F Native Thin Backend minimal real live spike 已完成：新增 `native-thin.live-spike` adapter 与 `native-thin-live-spike` harness command，allowed effects 仅限 `native_thin_scoped_live_spike_execute`、created handles readback、bbox/layer/entity audit、created-handles rollback 与 no-save audit；泛化 `native_plugin_execute`、`plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`save_current_dwg`、`formal_layer_write` 仍在 ToolCard / ToolContract 前置授权中 blocked。真实证据位于 `output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`：AutoCAD Core Console 加载 `native_plugins/native_thin_backend/bin/Release/net8.0-windows/NativeThinBackend.dll`，只写一个 `CODEX_PREVIEW` `LWPOLYLINE`，created handle `2CF` readback 通过，bbox 为 `[100,200,0] -> [1300,800,0]`，rollback `rolled_back`，`noSaveAudit.savedCurrentDwg=false`，harness result 为 `geometry_verified` / `verified`。该包不保存业务 DWG、不写正式图层、不恢复训练、不推进表 C；只证明最小 scoped native thin backend 闭环，不等于生产级插件体系完成。
P14 Engineering Kernel / BIM minimal DiffPackage 已完成：新增 `core/contracts/engineering_kernel.py`，注册 `engineering-kernel.diff-package` adapter，并新增 harness `engineering-kernel-diff` 命令。合同生成 `taskGraph`、`geometryGraph`、`semanticGraph`、`versionGraph`、`evidenceGraph` 与 `engineering-kernel-diff-package/p14/v1`，ToolCard 只允许 `engineering_kernel_graph_build`、`engineering_kernel_diff_package_write`、`backend_candidate_profile_write`；`cad_execute`、`native_plugin_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write`、训练 / 表 C mutation 仍在 backend 前 blocked。机器证据位于 `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`：closeout 为 `ready` / `not_verified`，`cadWritesAttempted=false`，`nativePluginInvoked=false`，`savedCurrentDwg=false`，`cadGeometryVerified=false`，只消费 P13F native-thin live source；`cad_session_host`、`dxf_file`、`geometry_kernel`、`ifc_bim` 在该 closeout 中为 candidate / not_run。P14 不是新的 CAD readback，也不 claim `geometry_verified`、生产级 BIM / DXF export、训练恢复或表 C 推进。

## 7. 每包施工规则

- 每个包必须先明确写集、禁止触碰路径、验证命令和可回滚范围。
- 代码包必须有单测；CAD 链路包还要有真实链路或 `external_blocker` 证据。
- 文档包必须跑 doc governance audit、PlanMD / doc governance tests、OpenSpec validate 和 `git diff --check`。
- 修改当前 next 时，同步 `CORE_CONTEXT_BRIEF.md` 与 `docs/planning/任务清单.md`；执行事实写 `docs/migration/execution-ledger.md`。
- 不把 helper note、临时 MD、OpenSpec change 或 handoff 写成第二套主计划。

## 8. 完成声明标准

- 普通治理：说明改动范围、验证命令和未验证项；没跑就标 `not_run`。
- CAD 输出：必须有 `CAD_PLAN`、validate、dry-run、`CODEX_PREVIEW`、created handles、readback、layer / bbox / entity audit。
- Harness 输出：只证明工具层可解析；完成仍由 EvidenceLedger + CompletionJudge 裁决。
- 训练、表 C、资产沉淀、插件：必须等对应 gate 和用户 scope；不得由 P9 文档或 CLI 产物暗示完成。

## 9. 事实源地图

| 事实类型 | 主入口 |
| --- | --- |
| 短上下文 / 当前 next | `CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md` |
| 唯一主计划 / 执行 ledger | `CORE_RESTRUCTURE_PLAN.md`、`docs/migration/execution-ledger.md` |
| 长期治理 / Target RFC | `docs/governance/cad-agent-rules.md`、`docs/rfcs/vnext-super-cad-agent-architecture.md`、`docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` |
| 旧架构归并 / 历史包 | `docs/architecture/system-architecture-convergence.md`、`docs/planning/archive/**`、`docs/status/changelog.md` |
| 机器证据 / protected evidence | `output/validation_runs/**`、`output/runs/**`、`projects/**`、`libraries/**`、`docs/training/training-sources.json`、`libraries/system_library/registry.json` |
