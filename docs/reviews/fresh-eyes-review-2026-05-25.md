# Fresh Eyes Review 2026-05-25

本评审模拟多个第一次接触系统的只读专家 agent，从 CAD 自动化、图块标准、空间业务、平台架构和验证门禁五个角度审视当前 CAD Agent Core。所有 agent 只读文件，不修改仓库。

## 评审边界

- 不推翻当前系统定位：仍是通用 CAD Agent Core Lab。
- 不把场景 Agent 做成独立算法系统。
- 不把 Phase W baseline 真实 CAD 通过扩大到真实项目图纸、真实块库、块插入或任意 CAD_PLAN。
- 不把截图、no-CAD benchmark 或 dry-run 当成几何准确证据。
- 本次只输出规划建议，不改代码、不运行 CAD。

## 参与视角

| 视角 | 关注点 | 主要结论 |
| --- | --- | --- |
| CAD 自动化与 COM 执行底座专家 | CAD_PLAN 到真实 CAD 写入、created handles、readback、能力矩阵 | 下一步应把基础图元写入/回读/验证固化为正式能力契约，再做最小块插入闭环 |
| CAD 图块库与制图标准专家 | BLOCK_LIBRARY、OBJECT_SPEC、图层、样式、属性块、hatch | 图块库缺单位、版本、锚点、连接点、footprint、clearance、属性、图层/样式绑定和验证状态 |
| 空间设计/工装/办公场景业务专家 | 真实办公/工装闭环、桌椅柜体、入口和通道 | 下一轮应先用办公基础闭环 Alpha 打穿系统，不急着做更聪明的自动设计 |
| 平台架构 / Agent 产品负责人 | 新人接手、多 agent 协作、主计划结构 | 应新增 Phase R，把新鲜视角评审制度化，并补可信基线、Phase 状态、Decision Gate 和接口归属 |
| 验证 / Benchmark 专家 | office 微场景、failure benchmark、证据状态 | 应把办公桌/椅/电脑桌做成小而硬的对象级、微场景和场景级 benchmark |

## 关键共识

1. 当前不是“没有 CAD 底座”，而是已有有限但严谨的 baseline CAD 闭环。
2. 最大缺口是把单一 baseline 扩展为可复用、可分级、可回读验证的通用 CAD 执行契约。
3. 下一轮不应泛泛铺更多场景名，而应用办公基础闭环验证真实业务语义。
4. 图块库必须作为通用资源进入 `libraries/` 和 `core/block_engine/`，不能塞进场景 Agent。
5. benchmark 必须覆盖 pass 和 failure；failure 要结构化说明原因，不允许 traceback 或静默少放。
6. no-CAD、dry-run、真实 CAD readback、截图必须有不同证据口径。
7. 每完成一个大阶段后，应固定做一次 Fresh Eyes Review，防止文档和能力口径重新漂移。

## 下一轮建议方向

| 方向 | 建议 |
| --- | --- |
| CAD 能力契约 | 固化 line / circle / arc / polyline / rectangle / text / dimension 的 write-read-verify 字段、容差和失败分类 |
| 块插入 | 先做受控测试块，不直接接真实公司块库；验证 block name、插入点、旋转、缩放、图层、属性和 handle readback |
| 办公基础闭环 | 小办公室、长条办公室、入口接待、桌椅柜体组合、会议/电脑桌混合、失败样本 |
| 图块库设计 | 补 units、schema_version、block_version、source、cad_identity、anchor_points、connection_points、footprint_2d、clearance_zones、symbol_2d、attributes、layer/style bindings、validation |
| benchmark | 增加对象级、微场景、场景级三层 benchmark，支持 min/max、contains_object_types、must_pass_checks 等断言 |
| 平台治理 | 建立 Phase R、Agent Contribution Contract、Core 变更入口门禁、Scenario finding 到 Core upgrade 流程 |

## 不应做的事

- 不要把通用对象尺寸、块 schema、图层样式、CAD 执行或回读逻辑写进 `agents/<scenario>/`。
- 不要把截图命名为几何验证。
- 不要让 benchmark summary 只写 `status=pass` 而不说明 `geometry_accuracy`。
- 不要一上来接真实公司块库；先用受控测试块验证底座。
- 不要把“文档拆分完成”或“新鲜视角评审完成”当成 Core Alpha 完成。

