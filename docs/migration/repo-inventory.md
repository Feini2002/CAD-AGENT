# Repo Inventory - Phase 3 Root Governance

日期：2026-06-14

本文记录 vNext Migration Phase 3 对根目录文件的分类。它不是 PlanMD，不承载第二套 next；唯一 PlanMD 是 `CORE_RESTRUCTURE_PLAN.md`。

## 分类口径

| category | 含义 | Phase 3 默认动作 |
| --- | --- | --- |
| active_control | 根级活跃入口、工程配置或迁移路由 | 保留根目录 |
| external_authority_source | 用户侧或外部母标准 | 本轮只登记；缺失时记录 absent |
| rfc_source | 目标架构 RFC | 归入 `docs/rfcs/` |
| governance | 长期治理、授权或规则边界 | 低风险可迁入 `docs/governance/`；高风险先保留 |
| runbook | 操作说明 / 运行入口 | 归入 `docs/runbooks/` 或保留本机入口 |
| deploy_checklist | 部署停闸 / 发布检查 | 归入 `docs/deploy/` |
| derived_view | 派生显示文件，不是事实源 | 登记，不移动 |
| local_artifact | 本机日志、快捷方式、工作区副产物 | 登记为候选，不删除 |
| protected_evidence | 事实源 / 证据链 / 高风险状态口径 | 登记，不移动 |
| binary_reference | 二进制参考资料或 CAD 文件 | 登记，不移动 |
| archive_candidate | 历史材料或可归档对象 | 先登记，后续需引用闭合 |

## 当前根目录文件

| path | category | status | Phase 3 decision | note |
| --- | --- | --- | --- | --- |
| `.git` | local_artifact | keep | no_manual_edit | Worktree gitdir 指针，不作为迁移对象 |
| `.gitignore` | governance | keep | keep_root | 仓库忽略规则，根级配置 |
| `AGENTS.md` | active_control | keep | keep_root_until_phase_4 | 自动加载规则入口；Phase 4 再压缩，不在 Phase 3 修改结构 |
| `README.md` | active_control | keep | keep_root | 项目入口，已更新 Phase 3 / Phase 4 口径 |
| `CORE_CONTEXT_BRIEF.md` | active_control | keep | keep_root | 新会话短上下文入口，已指向 Phase 4 next |
| `CORE_RESTRUCTURE_PLAN.md` | active_control | keep | keep_root | 唯一 PlanMD，已指向 Phase 4 next |
| `CORE_STATUS.md` | protected_evidence | keep | keep_root_for_now | 能力 / 证据 / 风险口径仍被入口规则引用；本轮只登记 |
| `MODEL_DATA_EXPORT_AUTHORIZATION.md` | governance | keep | keep_root_for_now | 模型桥数据外传授权边界；Phase 4 规则压缩时再评估归位 |
| `package.json` | active_control | keep | keep_root | Node / Worker tooling 配置 |
| `package-lock.json` | active_control | keep | keep_root | Node dependency lockfile |
| `wrangler.jsonc` | active_control | keep | keep_root | Cloudflare Worker 配置；本轮不部署 |
| `start_training_workbench.bat` | runbook | keep | keep_root_local_entry | 日常打开训练工作台入口；当前保留根目录 |
| `capability-map.html` | derived_view | keep | keep_root_for_now | 工作台显示器，不是事实源；未重建 |
| `capability-map-data.js` | derived_view | keep | keep_root_for_now | 派生快照，不是训练事实源；未重建 |
| `cad_mcp.log` | local_artifact | candidate | deletion_candidate_only | 本机运行日志；只登记候选，不删除 |
| `Claude Code DeepSeek.lnk` | local_artifact | candidate | deletion_candidate_only | 本机快捷方式；只登记候选，不删除 |
| `超全家装工装CAD总图库.dwg` | binary_reference | keep | protected_candidate_only | 大型 CAD 参考二进制；不移动、不打开、不保存、不删除 |

## 已迁出根目录的 Markdown

| old_path | new_path | category | status | note |
| --- | --- | --- | --- | --- |
| `超级CADAgent系统架构参考文档.md` | `docs/rfcs/vnext-super-cad-agent-architecture.md` | rfc_source | moved_in_phase_2 | Target Architecture RFC source |
| `CAD工具演进与原生插件引入阶段说明.md` | `docs/rfcs/vnext-tool-layer-native-plugin-roadmap.md` | rfc_source | moved_in_phase_2 | Tool Layer / Native Plugin RFC source |
| `ARCH_DOC_GOVERNANCE_BOUNDARY_PACKAGE.md` | `docs/governance/arch-doc-governance-boundary-package.md` | governance | moved_in_phase_3 | 文档治理 / 反膨胀侧包 |
| `WORKER_ORCHESTRATOR_DEPLOY_CHECKLIST.md` | `docs/deploy/worker-orchestrator-deploy-checklist.md` | deploy_checklist | moved_in_phase_3 | Worker 部署停闸清单 |

## 外部 / 未跟踪母标准

| path | category | status | decision | note |
| --- | --- | --- | --- | --- |
| `CAD_AGENT_vNext_v2_2_FINAL.docx` | external_authority_source | absent_from_worktree | no_move | 用户侧外部母标准；当前 worktree 根目录未发现该文件 |

## Protected Evidence 边界

本轮未移动、未删除、未改写：

- `output/**`
- `projects/**`
- `libraries/**`
- `docs/training/training-sources.json`
- `libraries/system_library/registry.json`
- `openspec/**`
- 任何 DWG

Phase 3 只证明根目录控制面更清晰，不证明 CAD 能力提升、训练恢复、表 C 提升、插件可用或真实 CAD preview 通过。
