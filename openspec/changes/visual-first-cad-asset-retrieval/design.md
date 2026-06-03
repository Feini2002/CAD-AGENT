## Context

本仓库已有 `core/assets/raw_intake.py`、场景 block mapping 和 CAD COM readback 能力，但当前“根据截图和语义找对应图块”的实际路径仍偏向全量 CAD 构造读取：枚举块参照、读取线弧数量，再人工判断。这条路径适合证明，不适合大图库检索。

本变更实现 V0：只针对当前打开 DWG 的模型空间块参照，建立视觉优先召回和 CAD 回读确认的最小闭环。它为后续图库文件夹离线缩略图索引、embedding 检索和 `system_library` 晋升预留数据结构。

## Goals / Non-Goals

**Goals:**

- 用户给出“找截图里的沙发”一类语义/视觉意图时，系统 SHALL 先生成视觉查询画像，而不是直接进入全量线条构造比对。
- 系统 SHALL 在当前 DWG 内快速返回 Top-K 候选块，并记录候选排序理由和耗时。
- 系统 SHALL 对最终候选输出 CAD readback 证据，包括 `handle`、`block_name`、`layer`、`bbox` 和候选分数。
- 系统 SHALL 明确证据边界：视觉相似度只证明候选召回，不证明真实尺寸准确。

**Non-Goals:**

- 不在本变更中实现跨文件 DWG 图库索引、向量数据库或真实图像 embedding 服务。
- 不写入、保存、删除或修改当前 DWG。
- 不改变表 C、capability registry 或施工图能力口径。
- 不把截图像素估算当作真实 CAD 尺寸。

## Decisions

1. **先做当前 DWG 内 V0，而不是直接做全图库向量平台。**

   理由：用户当前痛点是“我给语义 + 截图，你应更快找到当前 CAD 里的对应块”。V0 能用现有 COM readback 立即验收，同时保留后续图库索引扩展点。

   替代方案：直接建跨 DWG 索引和 embedding 管线。放弃原因是范围过大，需要文件批量打开、缩略图生成策略和依赖选型，容易拖慢本轮可验证交付。

2. **视觉查询画像是召回主入口，CAD 构造摘要只做 Top-K 复核。**

   V0 中 `VisualQueryProfile` 从中文/英文语义中解析对象类别、视角、座位数、典型宽高比和视觉部件。候选初排主要依赖 bbox 比例、类别词、图层语义和家具尺度；只有 Top-K 需要读取 block 定义摘要。

   替代方案：一开始就读取所有 block definitions 的线弧结构。放弃原因是这正是用户指出的不可扩展路径。

3. **证据报告分为视觉证据、语义证据和 CAD 证据。**

   视觉证据用于“像不像”；语义证据用于“是不是用户要的对象”；CAD 证据用于“是否真实存在、可回读、可定位”。报告必须避免混用这些层级。

4. **CLI 使用只读 AutoCAD 连接并支持计时验收。**

   `scripts/run_visual_block_retrieval.py` 输出 JSON，记录总耗时、各阶段耗时、候选数量和最佳命中。真实 CAD 自测使用用户当前 AutoCAD 会话，不保存 DWG。

## Risks / Trade-offs

- [风险] V0 没有真实图像 embedding，截图理解仍依赖用户语义和 Agent 视觉归纳。→ 缓解：报告写明 `visual_input_mode=profile`，不声明像素级视觉匹配。
- [风险] 数字块名如 `5S03232` 没有语义标签。→ 缓解：用 bbox 比例、来源图层、家具尺度和少量 block definition 摘要补充排序。
- [风险] 未来图库非常大时，当前 DWG 扫描仍不足。→ 缓解：V0 数据结构预留 `thumbnail_path`、`visual_embedding_ref`、`source_dwg`，后续 V1 可替换候选来源。
- [风险] CAD COM 不可见会阻断真实验收。→ 缓解：CLI 支持 fake JSON / unit test；真实验收失败时标为 external blocker，不得声称 CAD 命中。

## Migration Plan

1. 新增 V0 core 模块和 CLI，不改现有 CAD 执行路径。
2. 用单元测试验证画像解析和候选排序。
3. 用当前 AutoCAD 会话模拟“找沙发”命令计时验收。
4. 后续若进入 V1，再新增离线图库 manifest / thumbnail / embedding 索引，不破坏 V0 当前 DWG 检索入口。

## Open Questions

- V1 阶段选用本地 embedding、外部视觉模型，还是先用纯缩略图 perceptual hash？
- 大图库入库时是否允许批量打开 DWG 生成缩略图，还是要求用户提供预渲染图片？
- `system_library` 晋升是否需要人工确认标签和版权来源？
