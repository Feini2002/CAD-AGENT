# Target Architecture RFCs

本目录存放 CAD Agent vNext 迁移期的 **Target Architecture RFC**。

RFC 的作用是提供目标蓝图、术语、边界和未来建设路线。它们可以被 `CORE_RESTRUCTURE_PLAN.md` 吸收为阶段任务、验收标准或后续设计，但不能直接替代 PlanMD，也不能独立定义当前 next。

当前文件：

| 文件 | 角色 |
| --- | --- |
| `vnext-super-cad-agent-architecture.md` | 超级 CAD Agent 目标系统 RFC，描述中立工程数据内核、Agent Runtime、治理控制平面、证据账本和工作台等目标面 |
| `vnext-tool-layer-native-plugin-roadmap.md` | 工具层与原生插件路线 RFC，描述 Tool Gateway、Tool Contract、CAD Adapter、原生插件 thin spike 和多后端演进 |

边界：

- RFC 不承载当前执行台账。
- RFC 不替代 `CORE_RESTRUCTURE_PLAN.md`。
- RFC 不直接授权训练、表 C 推进、插件开工或真实 CAD 写入。
- RFC 正文在 Phase 2 只移动归位，不重写。
