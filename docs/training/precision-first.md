# 精度优先宪章（Precision First）

最后更新：2026-05-28

## 产品 north star

**多 Agent 可以越来越聪明、体量越来越大、思考链路越来越长——但一切必须精准。**

- 不准 = 不能用 = 一切白搭
- 聪明但画错，不如慢但可验证
- 训练、架构、功能扩面，都服从这一条

---

## 「精准」在本系统里的定义（可验证，非感觉）

**顺序：** 参照款任务先 [**视觉优先**](vision-first-style.md)（截图分析 + 常识部件），再机器数字。

| 层级 | 什么叫准 | 证据（缺一不可） |
| --- | --- | --- |
| **视觉** | 截图并排像 brief 同款；部件齐全（常识） | `visual_style_brief` + `audit_review.md` + 参考截图对比 |
| **安全** | 不毁图、不 save、不改正式层 | `preview_only_audit` |
| **语义** | 开放总成/凸出/靠垫等造型语言对 | checklist `semantic` + `agent_review_required` |
| **几何** | 尺寸、分区在容差内 | handles 回读 + `training_geometry_audit` |
| **洁净** | 无杂线、无 schematic、**部件级闭合少断线** | checklist `cleanliness` + `forbidden_patterns` |

**禁止：** 用工程进度、表 C、截图「看起来还行」代替上表。

---

## 精度 > 速度 > 体量（决策顺序）

```text
1. 这条链路能不能证明准？     → 不能就不交付（**先看截图像不像**）
2. 视觉过了，尺寸差几十 mm？ → **取整 approximate_ok**，不为小数 Repair
3. 能不能复跑得到同样结果？   → 不能就不晋升全局规则
4. 能不能让 Agent 更省事？   → 在前三条成立后再做
```

多 Agent「变聪明」只允许通过：

- 更准的 **Intent**（少误解 brief）
- 更准的 **Audit**（少漏检、少误绿）
- 更准的 **Repair**（对症而非补丁）

不允许通过：

- 跳过审计、降低门槛、口头说「应该对了」
- 案例私有脚本绕过 Core
- 为 pass 改 checklist 却不改几何

---

## 全链路硬门槛（从头 enforce）

每个全局 Agent 必须遵守；违反 = 链路 bug，写 `pipeline-changelog.md`。

| Agent | 不准就不能做的下一步 |
| --- | --- |
| **Intent** | `open_questions` 非空 → 禁止 Execute；**参照款无 `visual_style_brief` → 禁止 Execute** |
| **Execute** | validate/dry-run 未过 → 禁止写 CAD |
| **Audit** | `audit_pass: false` → exit 1，禁止 Delivery |
| **Repair** | 无根因记录 → 禁止再跑 Execute |
| **Delivery** | `agent_review_required` 未 **全部 pass** → 禁止截图、禁止请你 feedback |
| **Orchestrator** | 用户未 feedback pass → 案例不得标 done |

**黄金规则：** 机器审计是**必要非充分**；Agent 目视 + 你 feedback 才是训练期最终准绳。

---

## 聪明如何「只增不减准」

```text
案例失败
  → 先改 checklist 阈值 / 几何（本案）
  → 若 repeatable → 晋升 core 探针 或 pipeline 禁止项
  → 写 TRAINING_ERRORS + pipeline-changelog
  → 回归：旧案例 checklist 仍须 pass（防回归）
```

体量变大的合法方向：

| 增什么 | 必须附带 |
| --- | --- |
| 新 Core 探针 | unittest + 至少 1 个案例回归 |
| 新全局 Agent 步骤 | manifest 输入输出 + 禁止项 |
| 新场景 plugin | 不改 Core 精度门槛 |
| 更长 Repair 链路 | `max_auto_repair_rounds` + 每步 audit 证据 |

---

## 与表 C / Lab 的边界

- **表 C / V-PROOF / RCAD**：Core 能力登记，烟囱通过 ≠ 白话指哪打哪
- **训练案例 pass**：你的 `feedback.md` + 上表证据
- 两者都重要，**不可互相替代**

---

## 当前缺口（诚实）

| 已有 | 仍缺（精准相关） |
| --- | --- |
| 全局 audit 引擎 + checklist v2 | 款式目视仍靠 Agent/你（`forbidden_schematic` 仅拦一类） |
| 6 全局 Agent 注册 | Phase B 独立派发未做 |
| 洁净度 + profile 比例 | round7 落图仍 fail audit（正确红灯） |

**下一步优先级：** round7 几何准 + audit 绿 + Agent 目视过 → 再扩 Agent 体量。

---

## 相关文件

- 多 Agent 流水线：`docs/training/global-agent-pipeline.md`
- 审计架构：`docs/training/audit-architecture.md`
- 训练主链路：`docs/training/README.md`
- Agent 注册：`agents/pipeline/pipeline_manifest.json`
