# Deletion Ledger - Candidates Only

日期：2026-06-14

本文只记录删除候选，不表示已经删除或授权删除。Phase 3 不删除任何文件。

## 删除候选

| path | category | candidate_reason | required_before_delete | Phase 3 action |
| --- | --- | --- | --- | --- |
| `cad_mcp.log` | local_artifact | 根目录本机运行日志，不是事实源 | 确认无状态 / handoff / issue / evidence 引用；确认不需要保留最近调试日志 | candidate_only_not_deleted |
| `Claude Code DeepSeek.lnk` | local_artifact | 本机快捷方式，不是仓库事实源 | 确认不是用户日常入口；确认无需迁入本机工具说明 | candidate_only_not_deleted |

## 不进入删除候选

| path | reason |
| --- | --- |
| `CORE_STATUS.md` | protected_evidence，高风险状态口径；只登记不移动不删除 |
| `MODEL_DATA_EXPORT_AUTHORIZATION.md` | governance / 授权边界；只登记不移动不删除 |
| `capability-map.html` | derived_view，但仍是工作台显示入口；不删除 |
| `capability-map-data.js` | derived_view，但由同步链使用；不删除 |
| `超全家装工装CAD总图库.dwg` | binary_reference / protected_candidate；不移动不删除 |
| `output/**` | protected evidence；不移动不删除 |
| `projects/**` | protected evidence；不移动不删除 |
| `libraries/**` | protected evidence；不移动不删除 |
| `docs/training/training-sources.json` | training fact source；不移动不删除 |
| `libraries/system_library/registry.json` | asset registry fact source；不移动不删除 |
| `openspec/**` | active / historical change contracts；不移动不删除 |

## Phase 3 结果

实际删除：none。

能力声明边界：删除候选登记只证明根目录治理候选已识别，不证明引用闭合已允许删除，也不证明 CAD 能力、训练、表 C、插件或真实 CAD 链路有任何提升。
