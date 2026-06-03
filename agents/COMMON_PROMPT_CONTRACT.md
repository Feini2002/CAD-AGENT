# Common Prompt Contract

本文件是 CAD Designer Agent 与 pipeline Agent 的共享 Prompt 合同。各 Agent 的 `prompt_addendum.md` 只保留角色专属训练经验；以下通用安全、证据和反馈规则统一从这里读取，避免多处复制后漂移。

## 通用 CAD 训练规则

- CAD 测试必须使用中文标注；图层名、文件名、Schema key 等技术名允许保留原文。
- 落图前先选择不覆盖旧图形的测试画布，避免重叠用户已有图块。
- 通过前必须回读 created handles，并说明 checked / not_checked。
- 真实 CAD 测试默认只写 CODEX_PREVIEW，不保存 DWG，不污染正式图层。

## 视觉与位置反馈规则

- 用户用箭头、蓝圈或截图指定 CAD 位置时，先识别被指对象及相对位置，不得默认另起训练模块。
- 图像反馈类 CAD 修正应优先从当前 AutoCAD 实体回读参照 bbox，再按当前画面语义定位；不要套旧 execution summary 坐标。
- 若用户要求同尺寸补画样本，先从已存在样本 bbox 推导尺寸，再画新对象并回读 created handles。
- 误画在其它区域的预览实体默认保留，未经用户明确批准不得删除 CAD 对象或保存 DWG。

## 截图编排规则

- CAD 截图必须走任务级截图编排：局部修复优先传 target_handles、repair_plan.target_handles 或 repair_plan.target_bbox；没有局部目标时才退到 execution_summary.created_handles。
- AutoCAD 会话截图默认保留 CAD / IDE 布局，用 AutoCAD 客户区 PrintWindow；只有 PrintWindow 失败或 CAD 完全不可见时才短暂置顶。
- 单项复验、focused retraining、视觉复核和正式验收需要截图时，Agent 必须报告 screenshotDecision 和 visualPreview，并说明截图只是 visual_aid_only。
- 截图不得替代 created handles、CAD readback、bbox / 属性审计或用户验收；目标句柄不可用时报告 focus_target_unavailable，不得把 whole modelspace / 当前屏幕当作成功证据。

## 系统资产与样式复用规则

- 白话出现调用、复用、套用或强匹配系统库资产时，先检索 libraries/system_library/registry.json，并生成 system_asset_reuse_workflow；弱匹配只给候选，不直接落图。
- 线型、尺寸、文字、引线等 style_standard 资产只走 style_export / style_definition / 原生样式源；不得把 training_panel、current_screen、whole_modelspace 或全 CODEX_PREVIEW 复制成对象 block。
- 沉淀 style_standard 或其它系统资产时，元数据合同不等于真沉淀；native_style_definition_written 必须同时有 nativeVisiblePanelEvidence 或等价可见 native 证据，verified 资产还必须有 reuseWorkflowProbe 或真实 reuseReplay。
- native_style_definition_written 表示系统资产 DWG 已有原生样式定义，可生成 style_definition 复用计划；跨 DWG 真正应用仍需 style import / readback gate，且不得保存当前业务 DWG。
- 资产复用交付必须报告 matched asset、sourceSpec、target、readbackStatus 和 savedCurrentDwg=false；样式 importer 缺失时返回 deferred，不得声称 asset_reused。

## 系统资产 DWG 视觉仓库验收规则

- 系统资产 DWG 仓库验收不能只看截图非空、DWG 已保存或 overlapCount=0；还必须检查通道可读、内容密度、源/证明角色分离、图层语义和非截图证据。
- pipeline_visual_layout_reviewer 必须输出 layoutReadabilityAcceptable、aisleClearanceAcceptable、contentDensityAcceptable、sourceProofRolesSeparated、layerSemanticsAcceptable 和 nonScreenshotEvidenceChecked；缺任一字段时 visual_layout_review 继续阻断。
- 样式标准的可视面板只表示 proof panel；真正可复用来源是命名样式定义或精确边界 clean source，标签、边框、尺寸线、截图、证据卡片和 proof panel 默认 never-copy。
- 系统资产 DWG 的 proof content 不得继续留在 CODEX_PREVIEW；应迁到 ASSET_PROOF_CONTENT 等角色图层，并把 ASSET_SOURCE_BOUNDARY 控制为小的 source token，而不是框住证明图形的大边框。

## 证据边界

训练沉淀只更新 Agent 经验、Prompt 和检查口径；不提升表 C，不代表完整施工图能力。
