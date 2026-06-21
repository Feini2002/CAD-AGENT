# 当前交接包窗口

当前窗口：P14 Engineering Kernel / BIM minimal DiffPackage 已 closed；PlanMD 暂未定义 P15。P14 已通过 `engineering-kernel.diff-package` registered adapter 和 `engineering-kernel-diff` harness command 生成 no-CAD graph / DiffPackage closeout。P13F 已通过 `native-thin.live-spike` 在 AutoCAD Core Console 中完成一个 `CODEX_PREVIEW` scoped object 的 native thin create/readback/rollback/no-save 闭环。P13E minimal live spike execution gate / external_blocker closeout、P13D readiness / operator authorization request、P13C live spike authorization gate / execution receipt、P13B preflight / launch packet 与 P13A Native Thin Backend skeleton 均已 closed。P12 Mock Plugin Transaction、P11 ToolCard / Adapter Registry intake 与 P10B focused live rehearsal 均已 closed。旧 P10 blocker、Worker、模型桥、资产智能等更早包不再占用当前窗口，简版流水见 `docs/status/changelog.md`，全量索引见 `docs/handoffs/package-index.md`。

## CAD-AGENT-VNEXT-PHASE14-ENGINEERING-KERNEL-DIFF-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE14-ENGINEERING-KERNEL-DIFF-01`
2. **修改文件列表**：新增 `core/contracts/engineering_kernel.py`；更新 `core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md` 与 `AGENTS.md`；新增 P14 evidence 目录 `output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`。
3. **关键设计说明**：P14 新增 no-CAD `engineering-kernel.diff-package` registered adapter 和 `engineering-kernel-diff` harness command。合同生成 `taskGraph`、`geometryGraph`、`semanticGraph`、`versionGraph`、`evidenceGraph` 与 `engineering-kernel-diff-package/p14/v1`，并记录 backend candidate docs。ToolCard 只允许 `engineering_kernel_graph_build`、`engineering_kernel_diff_package_write`、`backend_candidate_profile_write`；`cad_execute`、`native_plugin_execute`、`real_cad_readback`、`dwg_save`、`formal_layer_write`、训练 / 表 C mutation 均在 backend 前 blocked。
4. **新增/修改测试**：新增 P14 tests，覆盖 CAD_PLAN graph projection、COM / plugin / DXF / geometry kernel / IFC candidate DiffPackage、registry 注册、allowed / forbidden effects，以及 harness 不能绕过 ToolCard。
5. **实际运行的命令和结果**：P14 红测先失败于缺 `core.contracts.engineering_kernel` 和缺 `engineering-kernel.diff-package` 注册；实现后 `tests.core.test_vnext_contract_adapters.P14EngineeringKernelBimTests` 3 OK，`tests.core.test_vnext_contract_adapters` 42 OK。
6. **是否运行真实 CAD**：否。P14 未连接 AutoCAD、未调用 native plugin、未写 CAD、未保存 DWG、未修改正式图层。P14 evidence 只读取 P13F 已有 source 并生成新 closeout JSON。
7. **机器可读证据路径**：`output/validation_runs/phase14-engineering-kernel-diff-package-20260621-162452/`；核心文件为 `phase14_engineering_kernel_closeout.json`、`p13f-source-diff/engineering_kernel_graphs.json`、`p13f-source-diff/engineering_kernel_diff_package.json` 与 `engineering_kernel_harness_result.json`。Closeout 显示 `status=ready`、`verificationStatus=not_verified`、`cadWritesAttempted=false`、`nativePluginInvoked=false`、`savedCurrentDwg=false`、`cadGeometryVerified=false`、`registryAdapterId=engineering-kernel.diff-package`；真实 source 只消费 P13F native-thin live result，`cad_session_host` / `dxf_file` / `geometry_kernel` / `ifc_bim` 在该 closeout 中为 candidate / not_run。
8. **结论分类**：P14 证明 graph / DiffPackage / registry / harness route 的最小闭环；不证明新的 `geometry_verified`、生产级 BIM / DXF / cloud backend、训练恢复、表 C 提升、正式图层写入或业务 DWG 保存能力。
9. **剩余风险**：真实多 backend 同一 CAD_PLAN live 对比、生产级 IFC / DXF / cloud backend、正式 native plugin 体系扩大范围仍为 not_run；若后续进入这些范围，必须另立 scope、CAD_PLAN、回滚/no-save/readback 证据和禁止触碰路径。

## CAD-AGENT-VNEXT-PHASE13F-NATIVE-THIN-LIVE-SPIKE-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13F-NATIVE-THIN-LIVE-SPIKE-01`
2. **修改文件列表**：更新 `core/contracts/native_thin_backend.py`、`core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md`、`docs/handoffs/package-index.md` 与 `AGENTS.md`；新增 `native_plugins/native_thin_backend/NativeThinBackend.csproj` 与 `native_plugins/native_thin_backend/NativeThinBackendCommands.cs`。
3. **关键设计说明**：P13F 新增 `native-thin.live-spike` registered adapter 和 `native-thin-live-spike` harness command。ToolCard 只允许 `native_thin_scoped_live_spike_execute`、created handles readback、bbox/layer/entity audit、created-handles rollback 与 no-save audit；泛化 `native_plugin_execute`、`plugin_execute`、`cad_execute`、`real_cad_readback`、`dwg_save`、`save_current_dwg`、`formal_layer_write` 仍在 backend 前 blocked。真实 backend 通过 AutoCAD Core Console `NETLOAD` 加载 `NativeThinBackend.dll`，只创建一个 `CODEX_PREVIEW` polyline，readback 后删除自身创建 handle，且不调用 save。
4. **新增/修改测试**：新增 P13F tests，覆盖 live adapter 注册、allowed / forbidden effects、直接合同 proof 裁决、harness 经 registry 路由 live spike、以及 `native_plugin_execute` 越权不能绕过 ToolCard。
5. **实际运行的命令和结果**：P13F 红测先失败于缺 `native-thin.live-spike`、缺 `execute_native_thin_live_spike()` 与缺 live runner 符号；实现后 `tests.core.test_vnext_contract_adapters.P13FNativeThinLiveSpikeTests` 3 OK，`tests.core.test_vnext_contract_adapters` 39 OK。安装本地项目专用 .NET 8 SDK 到 `C:\Users\User\.codex\cad-agent-tools\dotnet-sdk\` 后，`dotnet build native_plugins\native_thin_backend\NativeThinBackend.csproj -c Release` 0 errors（AutoCAD 引用版本 warning），随后真实 P13F live spike 输出 `geometry_verified` / `verified`。
6. **是否运行真实 CAD**：是，仅限 AutoCAD Core Console 临时模板会话和 `CODEX_PREVIEW` scoped object。未保存当前 DWG，未修改正式图层，未推进训练，未推进表 C，未写业务 DWG。
7. **机器可读证据路径**：`output/validation_runs/phase13f-native-thin-live-spike-20260621-160230/`；核心文件为 `native_thin_live_spike_harness_result.json`、`native_thin_live_spike_result.json`、`native_thin_plugin_result.json`、`native_thin_live_spike_execution_gate.json` 与 `native_thin_core_console.log`。插件 report 显示 handle `2CF`、`LWPOLYLINE`、layer `CODEX_PREVIEW`、bbox `[100,200,0] -> [1300,800,0]`、rollback `rolled_back`、`savedCurrentDwg=false`。
8. **结论分类**：P13F 证明最小 scoped native thin backend create/readback/rollback/no-save 闭环；不证明生产级 native plugin 体系、训练恢复、表 C 提升、正式图层写入或业务 DWG 保存能力。
9. **历史剩余风险**：该 P13F closeout 当时仍未启动 P14 Engineering Kernel / BIM；该风险已由 P14 minimal DiffPackage closeout 覆盖。当前剩余风险见 P14：生产级 IFC / DXF / cloud backend、多真实 live backend 同源对比、扩大 native backend 对象范围或进入正式插件体系均需另立 scope、CAD_PLAN、回滚/no-save/readback 证据和禁止触碰路径。

## CAD-AGENT-VNEXT-PHASE13E-NATIVE-THIN-LIVE-SPIKE-GATE-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13E-NATIVE-THIN-LIVE-SPIKE-GATE-01`
2. **修改文件列表**：更新 `core/contracts/native_thin_backend.py`、`core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md` 与 `docs/handoffs/package-index.md`。
3. **关键设计说明**：P13E 只做真实 live spike 前的 execution gate / external_blocker closeout。`build_native_thin_backend_live_spike_execution_gate()` 消费 P13D readiness packet，要求 operator 单独确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity、launch packet hash 与 authorization receipt hash。缺授权或 hash 漂移返回 `blocked / missing_authorization`；授权完整但缺真实 backend / AutoCAD / readback / rollback / no-save 环境返回 `external_blocker`。
4. **新增/修改测试**：新增 P13E tests，覆盖缺 operator authorization blocked、authorization receipt hash drift blocked、授权完整但缺环境 external_blocker、registry allowed / forbidden effects、harness 不能绕过 ToolCard。
5. **实际运行的命令和结果**：Targeted P13E red run 先失败于缺 `build_native_thin_backend_live_spike_execution_gate()` 与 P13E allowed effects；实现后 `tests.core.test_vnext_contract_adapters.P13ENativeThinLiveSpikeGateTests` 4 OK。最终验证结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未调用 native plugin、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P13E 使用 deterministic unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P13E 只证明 execution gate、missing authorization blocker、external blocker closeout、registry authorization 和 fake / mock / skeleton / real proof 分离；不证明真实 native plugin、real CAD readback、几何验证、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P13E closeout 当时仍未启动真实 scoped native backend live spike；该风险已由 P13F minimal real live spike closeout 覆盖。后续 Engineering Kernel / BIM minimal 风险已由 P14 minimal DiffPackage closeout 覆盖；当前剩余风险见 P14：生产级 backend、多真实 live backend 同源对比和扩大 native/backend 范围需另立 scope 与证据边界。

## CAD-AGENT-VNEXT-PHASE13D-NATIVE-THIN-READINESS-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13D-NATIVE-THIN-READINESS-01`
2. **修改文件列表**：更新 `core/contracts/native_thin_backend.py`、`core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md` 与 `docs/handoffs/package-index.md`。
3. **关键设计说明**：P13D 只做真实 live spike 前的 readiness packet 与 operator authorization request。`build_native_thin_backend_readiness_packet()` 消费 P13C ready execution receipt，校验 scope、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard、backend identity、launch packet hash 与 authorization receipt hash；输出只能是 `blocked` 或 `ready_for_user_authorization`，但不启动 AutoCAD 或 native plugin。
4. **新增/修改测试**：新增 P13D tests，覆盖 ready receipt 生成 operator authorization request、缺 receipt blocked、authorization receipt hash drift blocked、receipt 冒充执行 / real proof blocked、registry allowed / forbidden effects、harness 不能绕过 ToolCard。
5. **实际运行的命令和结果**：targeted P13D red run 先失败于缺 readiness 函数与 P13D allowed effects；实现后 `tests.core.test_vnext_contract_adapters.P13DNativeThinReadinessTests` 4 OK，`tests.core.test_vnext_contract_adapters` 32 OK。最终验证结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未调用 native plugin、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P13D 使用 deterministic unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P13D 只证明 readiness packet、operator authorization request、receipt hash/scope 漂移拦截、registry authorization 和 fake / mock / skeleton / real proof 分离；不证明真实 native plugin、real CAD readback、几何验证、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P13D closeout 当时仍未启动真实 scoped native backend live spike；该风险已由 P13F minimal real live spike closeout 覆盖。后续 Engineering Kernel / BIM minimal 风险已由 P14 minimal DiffPackage closeout 覆盖；当前剩余风险见 P14：生产级 backend、多真实 live backend 同源对比和扩大 native/backend 范围需另立 scope 与证据边界。

## CAD-AGENT-VNEXT-PHASE13C-NATIVE-THIN-AUTHORIZATION-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13C-NATIVE-THIN-AUTHORIZATION-01`
2. **修改文件列表**：更新 `core/contracts/native_thin_backend.py`、`core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md` 与 `docs/handoffs/package-index.md`。
3. **关键设计说明**：P13C 只做真实 live spike 前的授权门和执行收据。`build_native_thin_backend_authorization_gate()` 消费 P13B ready launch packet，要求用户显式确认 scope、CAD_PLAN、`CODEX_PREVIEW`、readback、rollback、no-save guard、backend identity 与 launch packet hash；缺授权或 scope/hash 漂移均 fail-closed。`build_native_thin_backend_execution_receipt()` 只消费已授权 gate，记录 scoped receipt，但不启动 AutoCAD 或 native plugin。
4. **新增/修改测试**：新增 P13C tests，覆盖 ready packet 进入 authorization pending、缺授权 execution receipt blocked、显式授权只生成 scoped receipt、不执行、scope/hash drift blocked、registry allowed / forbidden effects、harness 不能绕过 ToolCard。
5. **实际运行的命令和结果**：targeted P13C red run 先失败于缺 authorization / execution receipt 函数与 P13C allowed effects；实现后 `tests.core.test_vnext_contract_adapters` 28 OK。最终验证结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未调用 native plugin、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P13C 使用 deterministic unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P13C 只证明 live spike 授权门、执行收据、hash/scope 漂移拦截、registry authorization 和 fake / mock / skeleton / real proof 分离；不证明真实 native plugin、real CAD readback、几何验证、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P13C closeout 当时仍未启动真实 scoped native backend live spike；该风险已由 P13F minimal real live spike closeout 覆盖。后续 Engineering Kernel / BIM minimal 风险已由 P14 minimal DiffPackage closeout 覆盖；当前剩余风险见 P14：生产级 backend、多真实 live backend 同源对比和扩大 native/backend 范围需另立 scope 与证据边界。

## CAD-AGENT-VNEXT-PHASE13B-NATIVE-THIN-PREFLIGHT-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13B-NATIVE-THIN-PREFLIGHT-01`
2. **修改文件列表**：更新 `core/contracts/native_thin_backend.py`、`core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
3. **关键设计说明**：P13B 只做 scoped spike 发车前合同。`build_native_thin_backend_scope_receipt()` 要求 scope confirmation、CAD_PLAN、`CODEX_PREVIEW`、readback plan、rollback plan、no-save guard 和 backend identity；`build_native_thin_backend_launch_packet()` 只生成 ready / blocked JSON，ready 不授权 live execution。
4. **新增/修改测试**：新增 P13B tests，覆盖缺 scope / CAD_PLAN / safety plans blocked、非 `CODEX_PREVIEW` blocked、ready receipt、ready launch packet、缺或 blocked receipt、registry allowed / forbidden effects、harness 不能绕过 ToolCard。
5. **实际运行的命令和结果**：targeted P13B red run 先失败于缺 P13B 函数 / allowed effects / harness 参数；实现后 `tests.core.test_vnext_contract_adapters` 23 OK。最终回归结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未调用 native plugin、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P13B 使用 deterministic unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P13B 只证明 native thin backend launch 前置合同、registry authorization、越权拦截和 fake / mock / skeleton / real proof 分离；不证明真实 native plugin、real CAD readback、几何验证、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P13B closeout 当时仍未启动真实 scoped native backend live spike；该风险已由 P13F minimal real live spike closeout 覆盖。后续 Engineering Kernel / BIM minimal 风险已由 P14 minimal DiffPackage closeout 覆盖；当前剩余风险见 P14：生产级 backend、多真实 live backend 同源对比和扩大 native/backend 范围需另立 scope 与证据边界。

## CAD-AGENT-VNEXT-PHASE13-NATIVE-THIN-SKELETON-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE13-NATIVE-THIN-SKELETON-01`
2. **修改文件列表**：新增 `core/contracts/native_thin_backend.py`；更新 `core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`AGENTS.md`、`README.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
3. **关键设计说明**：`native-thin.backend` 是 Tool Gateway / Adapter Registry 后的 native thin backend skeleton；第一包只做合同层和 registry / harness 接入，不连接 AutoCAD、不调用真实 native plugin。复用 P12 transaction 字段：`transactionId`、`rollbackRequired`、`rollbackStatus`、`committedPreview`、`createdHandlesRef`、`blockedReason`、`retryable`、`documentState` 与 `ledgerRefs`，并新增 `noSaveAudit`、`rollbackProof`、`nativePluginInvoked=false`、`cadGeometryVerified=false`。
4. **新增/修改测试**：新增 P13 adapter / harness tests，覆盖 skeleton transaction 字段、blocked mode、registry 注册、allowed / forbidden effects、`native_plugin_execute` / `cad_execute` / `real_cad_readback` / `dwg_save` 越权拦截，以及 harness 不能绕过 ToolCard / ToolContract。
5. **实际运行的命令和结果**：targeted P13 red run 先失败于缺 `native_thin_backend` module、registry adapter 和 harness 参数；实现后 `tests.core.test_vnext_contract_adapters` 17 OK。最终回归结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未调用 native plugin、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P13A 使用 deterministic skeleton result / unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P13A 只证明 native thin backend 的合同字段、ToolCard / registry authorization、no-save audit 字段、rollback proof 字段和 fake / mock / native / real CAD proof 分离；不证明真实 native plugin、real CAD readback、几何验证、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P13A closeout 当时仍未启动真实 scoped native backend spike；该风险已由 P13F minimal real live spike closeout 覆盖。后续 Engineering Kernel / BIM minimal 风险已由 P14 minimal DiffPackage closeout 覆盖；当前剩余风险见 P14：生产级 backend、多真实 live backend 同源对比和扩大 native/backend 范围需另立 scope 与证据边界。

## CAD-AGENT-VNEXT-PHASE12-MOCK-PLUGIN-TRANSACTION-01

1. **包名**：`CAD-AGENT-VNEXT-PHASE12-MOCK-PLUGIN-TRANSACTION-01`
2. **修改文件列表**：新增 `core/contracts/mock_plugin_transaction.py`；更新 `core/contracts/adapter_registry.py`、`core/contracts/cad_agent_harness.py`、`core/contracts/__init__.py`、`tests/core/test_vnext_contract_adapters.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`AGENTS.md`、`README.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
3. **关键设计说明**：`mock-plugin.transaction` 是 Tool Gateway / Adapter Registry 后的 mock plugin-like adapter；最小 transaction 字段为 `transactionId`、`rollbackRequired`、`rollbackStatus`、`committedPreview`、`createdHandles` / `createdHandlesRef`、`blockedReason`、`retryable`、`documentState`、`ledgerRefs` 与 `proofStatus`。
4. **新增/修改测试**：新增 P12 tests，覆盖 success、failure、rollback_success、rollback_failed、blocked，allowed / forbidden effects，harness registry 路径，mock 不满足 `real_cad_readback`，以及 ledger refs。
5. **实际运行的命令和结果**：targeted P12 red run 先失败于缺 mock module / registry / harness 参数；实现后 `tests.core.test_vnext_contract_adapters` 13 OK。最终回归结果见本轮终端记录。
6. **是否运行真实 CAD**：否。未连接 AutoCAD、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：本包没有新增 protected evidence；P12 使用 deterministic mock result / unit test proof。P10B 真实 evidence 仍是只读引用：`output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：P12 只证明 mock plugin-like transaction 合同、rollback / committed_preview 语义、ledger refs 与 mock / real proof 分离；不证明 native plugin、real CAD readback、训练恢复或表 C 提升。
9. **历史剩余风险**：该 P12 closeout 当时仅到 P13A skeleton，尚无真实 native plugin/backend 证据；该风险已由 P13F minimal real live spike closeout 在最小 scoped 范围内覆盖。当前剩余风险见 P13F：不代表生产级 native plugin 体系完成。

## CAD-AGENT-VNEXT-PHASE11-ADAPTER-REGISTRY-01
1. **包名**：`CAD-AGENT-VNEXT-PHASE11-ADAPTER-REGISTRY-01`
2. **修改文件列表**：新增 `core/contracts/adapter_registry.py`；更新 `core/contracts/cad_agent_harness.py`、`tests/core/test_vnext_contract_adapters.py`、`tests/core/test_phase10_rehearsal.py`、`CORE_RESTRUCTURE_PLAN.md`、`CORE_CONTEXT_BRIEF.md`、`docs/planning/任务清单.md`、`docs/migration/execution-ledger.md`、`docs/status/current.md`、`AGENTS.md`、`README.md`、`docs/handoffs/current.md` 和 `docs/handoffs/package-index.md`。
3. **关键设计说明**：将 harness commands、`cad-session-host.preview/readback`、legacy preview/readback 注册为 Tool Gateway 后的 `RegisteredAdapter`；每个 adapter 声明 `ToolCard`、`ToolContract`、allowed / forbidden effects、entrypoint、backend、evidence boundary 和是否执行 CAD。
4. **新增/修改测试**：新增 P11 adapter registry 单测，覆盖 adapter 注册、allowed / forbidden effects、harness result 只读消费、带 `cadWritesAttempted=true` 的 result 拒绝消费，以及 CLI `--requested-effect dwg_save` 不能绕过 registry authorization。
5. **实际运行的命令和结果**：TDD 红灯先失败于缺少 `adapter_registry`、`requested_effects` 参数和 CLI 选项；实现后 targeted P11/P10 单测 49 OK；主合同/legacy/harness/phase10 回归 97 OK。文档治理和收尾验证结果见本轮终端记录。
6. **是否运行真实 CAD**：否。本包未连接 AutoCAD、未执行 CAD 回归、未写实体、未保存 DWG、未修改正式图层。
7. **机器可读证据路径**：P11 消费的既有 P10 evidence 为 `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`；本包只读取该目录，不移动、不删除、不改写 protected evidence。
8. **结论分类**：P11 证明 ToolCard / Adapter Registry 最小闭环、harness result 受控消费路径和 CLI 越权 fail-closed；不证明训练恢复、表 C 提升、native plugin readiness 或生产级 Tool Gateway 完成。
9. **剩余风险**：P13A skeleton 已完成，但真实 native plugin thin spike 仍需后续阶段和单独验证。

## CAD-AGENT-VNEXT-PHASE10-FOCUSED-LIVE-CLOSEOUT-12
1. **包名**：`CAD-AGENT-VNEXT-PHASE10-FOCUSED-LIVE-CLOSEOUT-12`
2. **修改文件列表**：本窗口仅记录 evidence 引用；P10B closeout evidence 位于 `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
3. **关键设计说明**：P10B scoped `table / single_table_preview_repeatability` 通过 `cad-session-host` 完成 2-run focused live rehearsal，全部写入 `CODEX_PREVIEW` 并执行 created handles readback。
4. **新增/修改测试**：该 closeout 属于既有 P10B evidence；P11 本轮新增测试只消费该 result / closeout，不重新执行 CAD。
5. **实际运行的命令和结果**：`phase10_rehearsal_closeout.json` 显示 `phase10CloseoutAllowed=true`、`phase11Allowed=true`、`stableGeometry=true`、`diffCount=0`、`failureCount=0`；run_01 / run_02 均 `geometry_verified` / `verified`。
6. **是否运行真实 CAD**：历史 P10B closeout 运行过 scoped `CODEX_PREVIEW` preview/readback；P11 本轮没有新跑 CAD、没有保存 DWG、没有改正式图层。
7. **机器可读证据路径**：`phase10_rehearsal_result.json`、`phase10_rehearsal_execution.json`、`phase10_rehearsal_closeout.json` 与 run_01 / run_02 子目录均在 `output/validation_runs/phase10-fast-closeout-live-rehearsal-20260620-0422/`。
8. **结论分类**：只证明 scoped P10 `CODEX_PREVIEW` 2-run preview/readback 稳定性，并放行 P11 registry intake；不恢复训练、不推进表 C、不证明 native plugin 可用。
9. **剩余风险**：后续真实 CAD 回归仍需用户确认，并继续遵守 `CODEX_PREVIEW`、readback、bbox / layer / entity audit 和 no-save guard。

## 近期历史口径

- 旧 P10 blocker `CAD-AGENT-VNEXT-PHASE10-CAD-REOPENED-READINESS-11`、`CAD-AGENT-VNEXT-PHASE10-COM-ATTACH-HARDENED-10`、`CAD-AGENT-VNEXT-PHASE10-LIVE-ATTACH-BLOCKED-09` 已由 P10B focused live closeout 解除，不再定义 current next。
- P10 scope proposal / receipt / closeout hardening 是已完成合同链记录；P11/P12 以后只把其 result / closeout 作为受控 evidence 或 mock proof 参照。
- Worker、模型桥、资产智能等旧窗口包仍按历史记录查询，不参与本次 vNext P13A 完成声明。
