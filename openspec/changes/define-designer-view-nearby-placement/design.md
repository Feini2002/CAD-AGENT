## Context

当前仓库已经有 `CAD_PLAN`、validate / dry-run、`CODEX_PREVIEW` 写入、created handles 回读和 preview-only 安全边界。`CAD_PLAN.placement` 目前支持 `absolute`、`space_reference`、`relative_to_object`，但缺少一种面向真实操作场景的中间语义：用户看着当前 CAD 屏幕说“在旁边画个……”，通常是在表达“我眼前这一屏附近的空位”，不是要求 Agent 在全局模型空间里找任意空白。

这项能力应服务 `CAD Designer Agent` 的成长路径：让主 Agent 模拟设计师在电脑前画 CAD 时的视域判断。它不是对象训练本身，也不是沙发能力；它是白话位置理解、当前视口上下文和 CAD 坐标解析之间的通用底座。

## Goals / Non-Goals

**Goals:**

- 将“旁边 / 附近 / 边上 / 上面 / 右侧”等白话位置解析为当前视口中的邻近候选区。
- 在不依赖截图的情况下，通过 AutoCAD 当前视口、可见实体 bbox、最近 handles 或选中对象建立 `CAD_VIEW_CONTEXT`。
- 优先模拟人的视线判断：当前视口内、围绕焦点、距离近、不会遮挡、无需移动视角即可看到。
- 最终仍产出确定的 CAD 坐标，并通过 `CAD_PLAN` validate / dry-run / preview-only execution / handles bbox readback 验证。
- 报告清楚 checked / not_checked：证明“放在当前视域邻近空位”，不证明对象造型、施工图规范或用户审美通过。

**Non-Goals:**

- 不在本变更中训练沙发、床、桌等具体对象族。
- 不把截图识别作为必需输入；截图只作为人工视觉辅助或后续增强。
- 不实现复杂平面布局优化、自动排版系统或跨房间设计判断。
- 不默认保存 DWG、不修改正式图层、不删除或移动用户原有对象。
- 不提升表 C，不写 capability registry verified 结论。

## Decisions

1. **采用“视域优先，坐标收口”的解析模型。**

   白话“旁边”先进入 `CAD_VIEW_CONTEXT` 和 `placement_resolution`，再收口为 `CAD_PLAN.placement.base_point`。这样既能保留设计师视角的语义，又不破坏现有执行链路对确定坐标的要求。

   替代方案是直接扩 `CAD_PLAN.placement.mode=nearby` 并让 executor 临场推断。放弃原因是执行端会混入语义判断，验证和 dry-run 都难以稳定复现。

2. **`CAD_VIEW_CONTEXT` 捕捉“我当前眼睛看到的 CAD”。**

   最小上下文包含：

   - `viewport_bbox`: 当前视口在模型空间中的范围。
   - `visible_entities_summary`: 当前视口内实体的 handle / layer / type / bbox 摘要，数量可限流。
   - `recent_created_handles`: 最近由 Agent 创建且仍可回读的 handles。
   - `selected_handles`: 如果用户当前选择了对象，作为最高优先级锚点。
   - `focus_cluster_bbox`: 由选中对象、最近对象或屏内主要可见实体聚合出的视觉焦点。
   - `capture_policy`: 是否允许截图；本能力基础路径不要求截图。

   如果无法读取当前视口，应返回 `needs_confirmation` 或 `blocked`，不得静默退回全局最右侧远处。

3. **锚点优先级模拟设计师注意力。**

   `focus_anchor` 的选择顺序：

   1. 用户明确指向的对象或 handles。
   2. 当前选中对象。
   3. 最近 created handles 且仍在当前视口内。
   4. 当前视口内主要可见内容簇。
   5. `CODEX_PREVIEW` 现有内容簇。

   只有前面来源缺失或不可回读时，才使用后面来源。报告必须写明锚点来源，例如 `selected_handles`、`recent_created_handles`、`visible_focus_cluster`。

4. **“旁边”是当前视口内的邻近候选槽位，不是无限远空白。**

   resolver 为 anchor bbox 生成右、左、上、下、右上、左上等候选槽位，并按以下因素评分：

   - 目标 bbox 是否完整或近乎完整位于原始当前视口内。
   - 与 anchor 的间距是否在近邻范围内。
   - 是否与可见实体、路径面、已有 preview 对象或保护对象冲突。
   - 是否符合用户方向词；没有方向词时优先选最近且最干净的位置。
   - 是否保留可读间距，避免贴边、重叠或遮挡文字 / 标注。

   可配置默认值应保守：最小间距约 100-300mm；最大近邻距离可按目标对象尺寸、anchor 尺寸和视口尺度综合限制。具体公式应进入实现和测试，而不是写死在 Agent Prompt。

5. **禁止用自动视图移动伪装“旁边”。**

   审计使用 draw 前捕获的 `viewport_bbox` 作为证明边界。落图后可以为了截图做可选取景，但“是否在旁边”的判断必须基于原始视口。若目标画在原视口外，再 zoom 到它，不能算通过。

6. **输出 `placement_resolution` 作为证据合同。**

   resolution 应包含：

   - `phrase`: 用户原始位置词。
   - `anchor_source` 和 `anchor_bbox`。
   - `viewport_bbox_before_draw`。
   - `candidate_slots`、评分和失败原因。
   - `selected_slot`、`base_point`、`target_bbox_expected`。
   - `readback_bbox`、`in_viewport`、`near_anchor`、`collision_status`。
   - `checked`、`not_checked`、`assumptions`。

   `CAD_PLAN` 可以继续保持 v0.1 的 `absolute` base point，但应在 plan 或 sidecar report 中引用 resolution，避免丢失白话解释链路。

7. **先做 no-CAD 可测核心，再接真实 CAD 验收。**

   第一阶段实现纯函数 resolver：输入 viewport / anchor / obstacles / target size，输出候选和选中 base point。第二阶段接 AutoCAD 当前视口和实体摘要。第三阶段用 `CODEX_PREVIEW` 执行和 handles 回读证明。

## Risks / Trade-offs

- [风险] 当前视口 COM 读取在不同 AutoCAD 版本中不稳定。→ 缓解：将 `CAD_VIEW_CONTEXT` schema 与 resolver 分开；COM 采集失败时明确 `blocked`，单元测试先覆盖 resolver。
- [风险] “旁边”具有主观性，不同设计师可能偏好右侧、下方或更宽间距。→ 缓解：将方向词、近邻距离、最小间距和候选排序参数化，并在 report 中暴露决策理由。
- [风险] 仅用 bbox 可能忽略文字、标注、复杂块内部空洞。→ 缓解：V0 先做保守 bbox 避让；复杂语义遮挡进入后续增强，不影响本能力的最小闭环。
- [风险] 如果当前视口非常满，新对象无法放在“旁边”。→ 缓解：返回 `needs_confirmation`，建议用户指定方向、缩小对象或允许新区域；不得偷偷画远。
- [风险] 最近 handles 被用户移动、删除或炸开。→ 缓解：每次 resolution 前先回读 handles 当前 bbox；失效则降级到 visible focus cluster，并记录 fallback。

## Migration Plan

1. 新增 schema / dataclass 和 no-CAD resolver，不触碰现有 executor 默认行为。
2. 增加 `CAD_PLAN` sidecar resolution 生成和 validate / dry-run 检查。
3. 接入 AutoCAD 当前视口采集，只读获取 `viewport_bbox`、可见实体摘要、选中对象和最近 handles。
4. 增加 preview-only quick trial：输入“在旁边画个测试矩形 / 沙发占位”，输出 `placement_resolution_report.json` 和 created handles readback。
5. 将规则沉淀到 `CAD Designer Agent` 或 pipeline prompt：遇到“旁边”先走视域邻近解析，不从白话直接跳绝对点。

回滚策略：如果真实 CAD 视口采集不稳定，可保留 no-CAD resolver 和 schema，暂时关闭 AutoCAD 采集入口；现有 `absolute` placement 执行不受影响。

## Open Questions

- 视口内“主要可见内容簇”的默认聚类是否优先排除坐标轴、导航 UI 和非常远的孤立对象？
- 无方向词时，默认方向是否应偏向右侧，还是完全由最近空位评分决定？
- 训练期是否需要记录用户对“旁边远近”的个人偏好，作为 `CAD Designer Agent` 的可迁移记忆？
