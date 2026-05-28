# 家装主训场景（Residential Primary）

最后更新：2026-05-28

前期只用 **家装** 突破「白话 → 懂 → 可校验计划 → 预览图对上」。办公、餐饮、展陈等保留在 `agents/`，默认不扩面。

## 训练目标（分三步记反馈）

| 步骤 | 你要的感觉 | 记在 `feedback.md` |
| --- | --- | --- |
| 1 听懂 | 我说人话，它问的点对、不漏关键房间/尺寸 | §理解 |
| 2 计划对 | `CAD_PLAN` / 结构化意图和我想的一致，validate/dry-run 过 | §计划 |
| 3 图画对 | `CODEX_PREVIEW` 上位置、尺寸、图层大致对；handles 回读支持 | §几何 |

理想状态是三步都 pass；实际会大量时间在 1→2 和 2→3 之间来回。

## 只改这些文件（产品层）

| 允许改 | 不要改（除非真 bug） |
| --- | --- |
| `agents/residential/rules.md` | `core/*` 执行与回读 |
| `agents/residential/preferences.json` | 其它 `agents/*` 的算法复制 |
| `agents/residential/workflows/*.md`（说明） | 正式图层、保存 DWG |
| `projects/<case>/brief.md`、`feedback.md` | 把公司块库塞进 git |

`agent.json` 中 `status=primary_training` 表示当前仓库默认场景。

## 家装词汇与偏好（起点）

已有 `rules.md` 覆盖：床靠实墙、衣柜通道、厨房操作三角、电视墙/玄关柜等。训练时遇到**新白话**优先追加到 `rules.md` 的 Scene Differences，而不是写 Python。

Core 映射见 `rules.md` 内 Preference → Core Mapping；benchmark 参考：`examples/workflows/blank_shell_residential_layout_loop.json`。

## 第一个案例怎么建

```text
复制 projects/residential_training_template/
  → projects/<your_case_id>/
改 sample.manifest.json 的 sample_id
填 brief.md（粘贴你的真实需求，可脱敏）
按需改 input/shell.manual.json
```

然后对话里说：**「开一轮训练，案例 id 是 \<your_case_id\>」**。

## 其它场景何时再开

当家装连续 **≥3 个案例** 在 §几何 稳定 pass，再选一个场景复制本模式。开新场景前不要并行训多个 Agent，避免反馈分散。

## 状态

| 场景 | 训练状态 |
| --- | --- |
| residential | **primary_training** |
| commercial_fitout, office, restaurant, exhibition, healthcare, custom | **paused** |

详见 `agents/AGENT_TRAINING_STATUS.md`。
