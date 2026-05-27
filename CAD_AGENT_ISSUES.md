# CAD Agent 问题与修复记录

本文现在只保留活跃风险和高频教训。压缩前完整问题库已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_ISSUES.md`。

## 当前活跃风险

| 风险 | 当前影响 | 处理口径 |
| --- | --- | --- |
| 根目录 MD 过长 | 旧完成流水会撑大每轮上下文，稀释当前主线 | 根目录只保留短摘要；旧记录查 `docs/history/root-md-full-snapshot-2026-05-26/` |
| 场景 Alpha / Beta 被误读为 Scene Product | 可能误以为工装、办公、住宅、餐饮 Agent 已产品化 | 统一四级成熟度；Scene Product 必须有真实项目样本、图块 metadata、真实 CAD smoke、用户确认流 |
| 真实 CAD 校验样本不足 | 不能证明任意项目 DWG 或任意 `CAD_PLAN` 几何准确 | 继续推进 §5 `RCAD-22+` 与 §3 `V-PROOF` 链式回写 |
| ActiveDocument / guard 仍需真实会话复验 | `LCAD-13/14` 已有 snapshot 与 strict guard 包装，但仍需更多真实 CAD 场景确认 | 优先用 `RCAD-21/22` 和后续真实 CAD smoke 扩样，不把 guard-only 当几何 verified |
| no-CAD deferred 被误读 | 顶层 pass 可能被误写成真实 CAD verified | 必须区分 `deferred`、`not_verified_without_cad_readback`、`geometry_verified` |
| 截图被误当几何证据 | 视觉辅助不能证明尺寸、图层、handle 和 bbox 准确 | 几何声明必须看 created handles readback |
| 路径边界回归 | runner 新增参数时可能越界读写 | 复用 `core.path_safety`，真实 CAD 连接前先做路径预检 |
| Schema 未登记 | schema 文件可能存在但 validator 不知道 | 新 schema 必须同步 registry、example、invalid fixture 和 tests |
| Markdown 进度漂移 | 表 A/B/C、RCAD 烟囱和 coverage JSON 容易被旧快照覆盖 | 表 C 以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；任务 next 以 PlanMD + 任务清单同步为准 |
| 精简回复漏报表 C | 聊天输出变短后，可能又用 Core 96% 或 RCAD 76% 暗示画图实力 | 精简表第一行必须是表 C 主指标；完整状态、交接、审计和表 C 专题再展开 A/B/C |

## 最近修复教训

### 聊天最终回复可精简，但表 C 主指标不能消失

日期：2026-05-27

现象：每轮交付强制输出完整表 A/B/C 后，信息量变大但思考价值下降，容易让真正关键的“本轮做了什么、有没有证据、真实 CAD 实力有没有变化”被表格淹没。

影响：后续 Agent 可能机械复制三表，或者相反地为了省字数漏掉表 C 主指标，导致工程进度 / RCAD 烟囱完成度再次被误读成真实 CAD 能力。

修复 / 计划：默认聊天交付改为 1 张精简进度表，第一行固定为表 C 主指标；完整 A/B/C 只在完整状态、交接、审计、进度盘点、表 C 专题或计数变更时展开。本次只改展示口径，不重构 §3 / §4 / §5 的真实任务分母。

以后规则：精简不是删除证据。涉及真实 CAD 能力时仍以 coverage JSON、created handles 回读和 `geometry_verified` 为准；handoff、状态页和能力模板保留完整证据结构。

### 表 A/B/C 数字必须以机器值和任务台账为准

日期：2026-05-27

现象：`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 与 `docs/planning/任务清单.md` 同时保留了 `0%`、`48.85%`、`49.24%`、`4.55%`、`4.35%` 等不同时间点快照，且 RCAD 烟囱也有 `21/29` 与 `22/29` 两套说法。

影响：后续 Agent 可能用旧 Markdown 数字覆盖最新机器报告，或把 RCAD / 工程进度误当成真实 CAD 实力。

修复 / 计划：收尾时复跑 `scripts/run_capability_coverage.py`，把表 C 同步为 `130/276 = 47.10%`、主指标 `4.35%`、最高 `L4`；把任务台账同步为 §3 `24/43`、§4 约 `42/55`、§5 `22/29`。

以后规则：表 C 一律以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准；历史 changelog 数字只作为当时快照。任务 next 若冲突，先按 `CORE_RESTRUCTURE_PLAN.md` 的决策边界修正 `docs/planning/任务清单.md`，再汇报。

### 临时文件清理失败不应掩盖已完成的模型构建

日期：2026-05-27

现象：全量自检时，当前沙箱对 `tempfile` 创建的随机临时目录/文件可能返回 `PermissionError`，导致 `shell_confirmation.py` 在 `temp_path.unlink()` 清理阶段失败；此时 SHELL_MODEL 已经成功构建，失败点只是临时文件清理。

修复：`apply_shell_drawing_read_confirmation()` 保留原有临时 JSON round-trip，但在 finally 清理时捕获 `PermissionError`，避免把清理失败误报为业务转换失败。

以后规则：临时文件用于内部 round-trip 时，业务结果与清理结果要分层；清理失败可以记录或忽略，但不能覆盖已经完成的验证/转换结论。

### 真实 COM 写入守卫必须在 Add* 前触发

日期：2026-05-27

现象：负向安全复核发现 `AutoCADComDriver.draw_line()` 等方法曾在 COM `AddLine/AddCircle/...` 之后才调用 preview-layer guard；这会造成正式图层负向 case 虽然抛错，但实体可能已经被创建到当前 DWG。

修复：`AutoCADComDriver` 的 line / rectangle / circle / arc / polyline / text / dimension 写入均改为先执行 `_guard_preview_layer_write(layer)`，再调用 COM `Add*`；新增 `negative_cad_runner` 报告 no-handle/no-save/no-delete/no-formal-layer 证据。

以后规则：任何真实 CAD 写入入口都必须先做权限、图层、路径、ActiveDocument/snapshot 预检，再执行 COM 写入；负向 runner 的 `created_handles=[]` 和 modelspace delta 不能省略。

### 根目录 MD 历史权重过高

日期：2026-05-26

现象：`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_STATUS.md` 等根文档持续累积已完成流水，每轮恢复上下文时噪声过高。

修复：创建 `docs/history/root-md-full-snapshot-2026-05-26/` 保存压缩前完整快照；根目录改为当前摘要、活跃队列、证据索引和风险边界。

以后规则：旧完成记录不要重新复制回根目录；需要追溯时展开 `docs/history/`。

### 场景成熟度口径容易误读

日期：2026-05-26

现象：已有 `office`、`residential`、`restaurant` 的 preferences、Scene Alpha 验收和 scene beta benchmark，容易被误读为具体场景 Agent 已完成。

修复：新增 `docs/architecture/core-scene-agent-boundaries.md`，统一 `Core 底座`、`Scene Alpha 壳层`、`Scene Beta 能力包`、`Scene Product 场景产品` 四级成熟度。

以后规则：没有真实项目样本、图块策略、真实 CAD readback 和用户确认流，不得称为 Scene Product。

### 本地真实 CAD 校验样本仍不足

日期：2026-05-26

现象：non-CAD 单测和 benchmark 较多，但真实 AutoCAD 用户会话下的 `geometry_verified` 样本仍有限。

修复 / 计划：唯一 `PlanMD` 已登记 `LCAD-01` 到 `LCAD-11`。当前 `LCAD-01`、`LCAD-02` 和 complex smoke 已完成，下一步推进 `LCAD-03`。

以后规则：任何新 CAD 能力没有 created handles readback 和 `geometry_verified` 时，只能写 deferred / non-CAD / fake-driver evidence。

### CAD 回归入口曾分散

日期：2026-05-26

现象：baseline validation、project sample check、composition check 曾经分散运行。

修复：新增 `core/verification/local_cad_regression.py` 和 `scripts/run_local_cad_regression.py`，支持 manifest、selected case、strict rollup 和 no-CAD deferred。

以后规则：进入下一阶段或做本地 CAD 回归时，优先跑 local CAD regression 矩阵。

## 不再高频展开的历史问题

以下问题仍可追溯，但不在根目录全文展开：

- 默认沙箱身份看不到用户会话 AutoCAD COM 活动对象。
- AutoCAD COM 点参数需要 `VT_ARRAY`。
- 顶层 validation pass 不能替代 readback `geometry_verified`。
- block alpha 失败路径必须先拒绝再写入。
- Windows / PowerShell 编码会影响中文路径和 JSON 输出。
- `sys.path` 注入、系统 temp、路径越界和 schema registry 缺口。
- blank-shell 早期几何、placement、zone、benchmark 和 workflow schema 问题。

完整条目见 `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_ISSUES.md`。

## 记录模板

新增问题按这个短格式写，避免再次膨胀：

```markdown
### 问题：一句话概括

日期：YYYY-MM-DD

现象：发生了什么。

影响：为什么危险。

修复 / 计划：已经做了什么，或下一步在哪里登记。

以后规则：后续如何避免。

相关文件：`path`
```
