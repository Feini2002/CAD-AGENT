# 后置包路由台账

最后更新：2026-05-28

Core 与三轨已收口后，后续工作按本台账路由。优先级以 `CORE_RESTRUCTURE_PLAN.md` Decision Gate 为准；表 C 机器值以 coverage JSON 为准。

## 包状态图例

| 状态 | 含义 |
| --- | --- |
| **done** | 本仓库内已交付证据或文档 |
| **ready** | 可立即开包，无用户样本依赖 |
| **blocked** | 需用户输入（DWG、块库、正式图层批准等） |
| **cancelled** | 不建议做或会破坏语义 |

## 拆包清单

| 包 ID | 方向 | 状态 | 依赖 | 退出门槛 | 证据入口 |
| --- | --- | --- | --- | --- | --- |
| BACKLOG-SKIP-01 | 表 C 100%（改 `real_cad_guard`） | **cancelled** | — | 不破坏负例 smoke 语义 | — |
| **VCAD-03** | CAD 画面：零售展厅平面 | **done** | AutoCAD `CODEX_PREVIEW` | fake 单测 + 真实 CAD readback | `output/validation_runs/vcad-03-retail-20260528/` |
| **VCAD-04** | CAD 画面：卫浴/厨房模块 | **done** | AutoCAD `CODEX_PREVIEW` | fake 单测 + 真实 CAD readback | `output/validation_runs/vcad-04-20260528/` |
| **BETA-PROJECT-SAMPLE-07** | 样本 intake 空模板 | **done** | 无 | 协议扫描 pass | `projects/sample_intake_template/` |
| **BETA-PROJECT-SAMPLE-08** | 合成脱敏样本真实 CAD | **done** | AutoCAD `CODEX_PREVIEW` | geometry_verified + 协议 pass | `projects/sample_test_fitout_20260528/`、`output/validation_runs/sample-08-test-fitout-20260528/` |
| **BETA-DRAWING-READ-06** | 读图人工确认 runbook | **done** | 无 | runbook 已交付 | `docs/runbooks/drawing-read-user-gate.md` |
| **BETA-SCENE-04** | 展陈/医疗 scene benchmark | **done** | 场景 manifest | exhibition 7/7 + healthcare 6/6 no-CAD benchmark pass | `docs/verification/beta_scene_04_exhibition_healthcare_boundaries.md`、`output/validation_runs/beta-scene-04-20260528/` |
| **BETA-CROSS-MACHINE-02** | 换机复验 P0 gate | **done** | AutoCAD 测试会话 | `run_beta_cross_machine_02_gate.py` + MCP 手动画 1 次 | `docs/runbooks/cross-machine-reverify.md` |
| BETA-AGENT-REGISTRY-01 | 垂直行业登记策略 | **done** | 无 | 策略文档已交付 | `docs/verification/agent_vertical_registry_strategy.md` |
| BETA-PROPOSAL-02 | 多方案确认流产品化 | ready | 产品需求 | 确认 schema + 测试 | `core/proposal_engine` |

## 已收口（勿重复开旧轨包）

| 项 | 结果 |
| --- | --- |
| 表 C 主指标 | **99.68%**（316/317 showcase；1 smoke） |
| 证据路径 / hard audit | **0 missing / 0 fail** |
| VCAD-EXPAND-01 | 房间平面 136 handles + 餐桌组合 20 handles |
| TABLE-C-FINAL-GAP | 末 4×none→showcase |
| EVIDENCE-DEBT-01 | 路径与契约债清零 |

## Agent 训练（方案 A）

| 包 ID | 方向 | 状态 | 证据 |
| --- | --- | --- | --- |
| **TRAIN-RESIDENTIAL-00** | 家装主训 + 案例模板 + 训练控制面 | **done** | `docs/training/`、`projects/residential_training_template/`、`agents/AGENT_TRAINING_STATUS.md` |

## 口令路由

| 用户说 | 默认包 |
| --- | --- |
| 开一轮训练 / 家装案例 | `docs/training/README.md` + `projects/<case_id>/` |
| 推进 CAD 画面 | 后置 VCAD 系列已收口；新画面需求另开受控包 |
| 给样本 / 行业闭环 | `BETA-PROJECT-SAMPLE-08`（合成样本已证；用户 DWG 另开目录复制 07 模板） |
| 准备接项目 | `BETA-PROJECT-SAMPLE-07` 填模板 → 复制为 `projects/<your_id>/` |
| 读图 / DWG 识别 | `BETA-DRAWING-READ-06` + 已有 READ-01~05 |
| 换机 | `run_beta_cross_machine_02_gate.py`（见 cross-machine-reverify runbook） |
| 推进表 C | 仅当新增 registry 行；当前顶格除 smoke |
