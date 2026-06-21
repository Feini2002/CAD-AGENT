# Root Cleanup Ledger

本文记录 vNext migration 中根目录文件的归位、保留、移动和删除决策。它不是 PlanMD，不承载第二套 next。

## Phase 2 - Target RFC 归位

日期：2026-06-14

状态：completed

| 原根目录文件 | 新位置 | 动作 | 说明 |
| --- | --- | --- | --- |
| `超级CADAgent系统架构参考文档.md` | `docs/rfcs/vnext-super-cad-agent-architecture.md` | moved | Target Architecture RFC source；不替代 PlanMD，不定义 current next |
| `CAD工具演进与原生插件引入阶段说明.md` | `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` | moved | Tool Layer / Native Plugin RFC source；不授权插件抢跑 |

未删除文件：none。

事实源影响：none。未触碰 `output/**`、`projects/**`、`libraries/**`、registry、training-sources、OpenSpec 或任何 DWG。

## Phase 3 - 根目录治理与旧主线 MD 分层

日期：2026-06-14

状态：completed

目标：让根目录只保留少量活跃入口和必要本机入口；其余根级文档、部署停闸、派生物、本机产物、二进制参考和外部母稿按类别登记。高风险事实源只登记不移动。

### 低风险 Markdown 移动登记

| old_path | new_path | category | action | reason | references_checked |
| --- | --- | --- | --- | --- | --- |
| `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` | `docs/governance/arch-doc-governance-boundary-package.md` | governance | moved | 根级临时治理侧包已不应长期占用根目录；归入 governance 后仍作为文档治理参考包 | `rg ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md`，排除 `output/**`、`projects/**`、`libraries/**`、`node_modules/**` 和派生快照 |
| `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md` | `docs/deploy/worker-orchestrator-deploy-checklist.md` | deploy_checklist | moved | Worker 部署停闸清单属于部署治理资料；迁入 `docs/deploy/`，保留停闸语义，不授权新增部署 | `rg WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md`，排除 `output/**`、`projects/**`、`libraries/**`、`node_modules/**` 和派生快照 |

### 高风险仅登记不移动

| path | category | action | reason |
| --- | --- | --- | --- |
| `CORE_STATUS.md` | protected_evidence | keep_root_for_now | 能力 / 证据 / 风险口径仍被 `AGENTS.md` 和 brief 引用；Phase 3 只登记，后续需专门引用闭合后再评估是否迁入 `docs/status/` |
| `MODEL_DATA_EXPORT_AUTHORIZATION.md` | governance | keep_root_for_now | 模型桥数据外传授权是长期安全边界，且 `AGENTS.md` 明确引用根目录路径；本轮不移动，Phase 4 压缩规则时再归位 |
| `capability-map.html` | derived_view | keep_root_for_now | 训练工作台显示器，不是事实源；日常入口仍依赖根目录 HTML |
| `capability-map-data.js` | derived_view | keep_root_for_now | 由同步脚本生成的派生快照，不作为训练事实源；本轮不移动、不重建 |
| `cad_mcp.log` | local_artifact | deletion_candidate_only | 本机运行日志，先登记到 deletion ledger 候选，不删除 |
| `Claude Code DeepSeek.lnk` | local_artifact | deletion_candidate_only | 本机快捷方式，先登记到 deletion ledger 候选，不删除 |
| `超全家装工装CAD总图库.dwg` | binary_reference | protected_candidate_only | 根级大型 DWG / CAD 参考二进制，本轮不移动、不打开、不保存、不删除 |
| `CAD_AGENT_vNext_v2_2_FINAL.docx` | external_authority_source | absent_from_worktree | 用户侧外部母标准；当前 worktree 根目录未发现该文件，本轮无移动对象 |

未删除文件：none。

禁止触碰确认：未移动、未删除、未改写 `output/**`、`projects/**`、`libraries/**`、registry、training-sources、OpenSpec 或任何 DWG。
