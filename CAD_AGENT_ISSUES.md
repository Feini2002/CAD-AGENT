# CAD Agent 问题与修复记录

本文现在只保留活跃风险和高频教训。压缩前完整问题库已归档到 `docs/history/root-md-full-snapshot-2026-05-26/CAD_AGENT_ISSUES.md`。

## 当前活跃风险

| 风险 | 当前影响 | 处理口径 |
| --- | --- | --- |
| 根目录 MD 过长 | 旧完成流水会撑大每轮上下文，稀释当前主线 | 根目录只保留短摘要；旧记录查 `docs/history/root-md-full-snapshot-2026-05-26/` |
| 场景 Alpha / Beta 被误读为 Scene Product | 可能误以为工装、办公、住宅、餐饮 Agent 已产品化 | 统一四级成熟度；Scene Product 必须有真实项目样本、图块 metadata、真实 CAD smoke、用户确认流 |
| 真实 CAD 校验样本不足 | 不能证明任意项目 DWG 或任意 `CAD_PLAN` 几何准确 | 优先推进 `LCAD-03+` 真实 CAD 扩样 |
| ActiveDocument guard 未落硬门禁 | 真实 CAD preview 写入还需更强前后守卫 | 下一包 `LCAD-03-ACTIVE-DOCUMENT-GUARD` |
| no-CAD deferred 被误读 | 顶层 pass 可能被误写成真实 CAD verified | 必须区分 `deferred`、`not_verified_without_cad_readback`、`geometry_verified` |
| 截图被误当几何证据 | 视觉辅助不能证明尺寸、图层、handle 和 bbox 准确 | 几何声明必须看 created handles readback |
| 路径边界回归 | runner 新增参数时可能越界读写 | 复用 `core.path_safety`，真实 CAD 连接前先做路径预检 |
| Schema 未登记 | schema 文件可能存在但 validator 不知道 | 新 schema 必须同步 registry、example、invalid fixture 和 tests |

## 最近修复教训

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
