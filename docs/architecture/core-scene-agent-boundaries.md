# Core 与场景 Agent 边界

最后更新：2026-05-26

本文用于消除一个容易误读的口径：当前仓库确实已经有 `office`、`residential`、`restaurant` 等场景目录、preferences、benchmark 和边界扫描，但这些并不等于具体场景 Agent 已经产品化完成。它们主要是在开发通用底座时，为了证明 Core 可以被不同场景复用而建立的轻量验证层。

## 四级成熟度

| 层级 | 含义 | 当前仓库状态 | 可以声称 | 不能声称 |
| --- | --- | --- | --- | --- |
| Core 底座 | 通用 schema、workflow、CAD_PLAN、执行、验证、读图、对象、图块、benchmark、安全门禁 | 已有较厚 Alpha 原型和有限真实 CAD 验证 | 通用链路可复验，有限 baseline / 受控样本有 CAD 证据 | 任意项目、任意块库、任意 CAD_PLAN 都准确 |
| Scene Alpha 壳层 | 场景 preferences、词汇、默认参数、排序权重、解释模板、边界扫描 | `office` / `residential` / `restaurant` 已有 Alpha 验收 | 多场景可复用同一 Core pipeline，差异可观察 | 场景 Agent 产品完成，真实 CAD 多场景几何准确 |
| Scene Beta 能力包 | 某个场景有对象体系、微场景、失败样本、benchmark 和非 CAD 证据门禁 | office / residential / restaurant 已有 non-CAD beta benchmark | 该场景的对象和组合语义可重复跑通 non-CAD benchmark | 真实业务场景已能自动设计或真实 CAD verified |
| Scene Product 场景产品 | 面向某类业务的可用 Agent，有真实项目样本、块库策略、真实 CAD smoke、用户确认流和交付边界 | 尚未完成 | 可在受控真实项目中闭环交付 | 当前不可声称 |

## 什么属于 Core 底座

- `CAD_PLAN` schema、validate、dry-run、执行和 verification。
- AutoCAD COM 写入、`CODEX_PREVIEW` 安全策略、created handles 回读和 `geometry_verified` 证据门槛。
- 通用空壳、动线、功能区、对象放置、候选方案、评分和用户确认接口。
- 通用对象模型、图块 metadata、block insertion alpha、图层 / 样式 profile。
- benchmark runner、evidence gate、failure 分类、repo audit 和本地 CAD regression runner。
- 自动读图 / 空壳识别的通用只读能力。

这些能力进入 `core/` 或 `libraries/`，不应复制到 `agents/<scenario>/`。

## 什么才算具体场景开发

以工装为例，只有进入下面这些工作，才算真正开发“工装 Agent”：

- 拆出工装子场景：开放办公、独立办公室、会议室、前台、洽谈区、茶水间、储物、走廊等。
- 建立工装对象体系：办公桌、工位组、会议桌、文件柜、前台、屏风、设备柜、打印区等。
- 建立或接入工装图块 metadata：尺寸、插入点、朝向、缩放、属性、图层、替代 fallback。
- 写清业务规则：办公桌椅关系、柜前净空、门前避让、通道宽度、会议座位数、屏风方向等。
- 建立成功 / 失败 benchmark：太小房间、入口冲突、柜前净空不足、通道不达标、对象缺失等。
- 选择至少一组脱敏真实样本，从 `projects/` 到 `SHELL_MODEL` / proposal / `CAD_PLAN` / `CODEX_PREVIEW` / readback 形成闭环。
- 有真实 CAD smoke 或 regression，至少部分代表 case 取得 created handles 与 `geometry_verified`。
- 有解释模板说明为什么该方案符合工装，而不是泛化摆放几个矩形。

## 目标架构：中控 + 场景能力模块

未来场景 Agent 不应散落成互相复制的独立系统，而应像可插拔能力模块一样被 Core 中控按需调用：

```text
USER_REQUEST
-> Core Orchestrator
-> Scene Router
   -> no_scene: 使用通用 Core 默认能力
   -> commercial_fitout: 加载工装 Scene Capability Module
   -> residential: 加载住宅 Scene Capability Module
   -> restaurant: 加载餐饮 Scene Capability Module
-> Core workflow / CAD_PLAN / verification
```

建议命名：

| 名称 | 职责 |
| --- | --- |
| `Core Orchestrator` | 主底座中控，负责请求解析、路由、调用 Core workflow、汇总证据 |
| `Scene Router` | 判断是否需要某个场景；没有明确场景时返回 `no_scene` |
| `Scene Registry` | 记录可用场景模块、触发词、能力清单、成熟度和禁用条件 |
| `Scene Capability Module` | 场景独立能力包，放在 `agents/<scenario>/` 下 |
| `Scene Activation Policy` | 场景何时可被启用、何时必须保持通用 Core、何时要追问用户 |

默认激活规则：

- 用户没有提到专门场景，也没有项目 manifest 指定场景时，必须走 `no_scene`，不自动套用 office / residential / restaurant。
- 用户明确说“工装、办公室、餐饮、住宅、展陈”等，才允许路由到对应场景。
- 如果系统只能猜测场景，但置信度不足，应先追问，不要默默调用场景模块。
- 场景模块只能补业务语义、对象偏好、规则映射、图块选择和解释模板；真实 CAD 执行、几何、验证仍回到 Core。

## 需求侧 Agent 层

`agents/demand_side/` 是独立于 Scene Product 的需求压力测试层。它用于模拟用户画像和自然语言需求，把“用户会怎么问”记录成可跑 benchmark case，并映射到 Core 能力缺口。它是开发期脚手架，不是最终系统形态；能力验收完成后，可以删除角色表和需求侧表单，只保留最终生成能力、理解能力和回归测试。

允许内容：

- 需求侧角色画像。
- 用户原话。
- 场景归属。
- 需求焦点。
- `core_capability_targets`。
- 指向现有 benchmark pipeline 的 demand case。

禁止内容与场景 Agent 一致：不得在需求侧 Agent 中实现 CAD 执行、几何、验证、布局算法或真实项目资料。需求侧 benchmark 通过只证明需求记录可被 Core 现有 pipeline 接住，不证明真实 CAD 几何准确。

## 场景模块目录建议

当前 `agents/<scenario>/` 仍以轻量数据层为主。进入 Scene Product Alpha 时，可以逐步演进为：

```text
agents/commercial_fitout/
  agent.json
  preferences.json
  rules.md
  registry.json
  capabilities/
    object_catalog.json
    micro_scenes.json
    failure_cases.json
    block_mapping.json
    explanation_templates.md
```

如果未来确实需要场景专属函数，应先建立统一接口，例如：

```text
agents/<scenario>/capabilities/
  adapters.py  # 只做业务语义到 Core 输入的转换
```

但这需要先更新边界扫描和测试。即使允许场景函数，也仍禁止在 `agents/` 内实现通用几何、碰撞、CAD 执行、回读或验证。

## 当前推荐路线

1. 先继续补 `LCAD-*` 本地真实 CAD 校验扩样，防止后续场景开发建立在不足的 CAD 证据层上。
2. 再选择首个真实场景产品线，建议从 `commercial_fitout` / 工装开始，因为它和当前 office 样本、图块、通道和净空规则最接近。
3. 在工装专项前先补 `Scene Router / Registry / Activation Policy`，确保没有明确场景时不调用任何场景模块。
4. 工装先做 `Scene Product Alpha`：开放办公 + 会议室 + 前台接待三个子场景，配 1 组脱敏样本和 1 组受控块库。
5. 每个子场景都按“对象规格 -> 微场景 -> failure benchmark -> CAD_PLAN -> 真实 CAD smoke -> 状态同步”的顺序推进。
6. 只有当真实 CAD readback 与用户确认流都闭环后，才把进度从 Scene Beta 上调为 Scene Product。

## 文档口径

- `CORE_RESTRUCTURE_PLAN.md` 维护开发顺序和未来小包。
- `CORE_STATUS.md` / `docs/status/current.md` 维护成熟度和证据。
- `agents/SCENE_AGENT_RULES.md` 维护 `agents/` 目录可写边界。
- `docs/verification/scene_alpha_acceptance.md` 只证明 Scene Alpha，不证明场景产品完成。
