# STRUCT-MERGE-PREP-01 合并 / 保留规则

日期：2026-05-28

本页承接 `STRUCT-AUDIT-01`，只规定 Python 文件整理的判断口径；它不是执行合并清单，也不改变 CAD 能力表 C。

## 1. 可以合并

一个文件同时满足下列多数条件时，才进入“应合并”候选：

- 只被 1 个相邻实现文件使用，且不是 public CLI / facade / compatibility wrapper。
- 文件本身没有独立测试价值，测试更自然地落在调用方行为上。
- 文件名表达的是调用方内部细节，而不是仓库长期边界。
- 阅读时必须在两个小文件之间来回跳，合并后认知成本更低。
- 合并后可以用 focused tests + `run_repo_audit.py` 验证，不需要真实 CAD。

## 2. 应该保留

满足任一条件就默认保留，不进入小批合并：

- `scripts/*.py` 中的用户可执行命令、兼容入口或文档中出现的一键验证命令。
- 高 fan-in 基座：schema、path safety、evidence contract、test / script bootstrap。
- CAD 写入、预览安全、created-handle readback、registry / coverage / 表 C 相关边界。
- 有明确独立测试价值的算法小模块，例如 geometry、layout check、benchmark runner。
- 旧命名空间兼容包装仍可能被外部脚本引用，尚未完成引用审计。

## 3. 应该拆分

下列情况不是“合并”，而是“拆分 / 抽公共层”：

- 文件接近或超过 450 行，且同时承担场景数据、CAD 操作、报告组装、验证判定。
- 模块 fan-out 高，作为编排层已经开始吸入多个领域。
- 一个模块跨文件 import 另一个模块的 `_private` helper。
- 新增逻辑会把既有 runner 推过 500 行维护阈值。

## 4. 允许超线例外

只在短期满足全部条件时允许贴近 500 行：

- 文件是稳定 public runner / facade，已有直接测试和历史证据。
- 本轮不新增大段逻辑，只做小修或文档同步。
- 报告中写明“下次触碰即拆分”的触发条件。

## 5. 批处理门槛

每个 `STRUCT-MERGE-xx` 小包最多处理 1-3 组高确定性候选。每包必须：

- 先写或确认 focused tests。
- 跑相关 focused tests。
- 跑 `scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings`。
- 若触碰 CAD runner，只做 no-CAD / fake-driver 验证；真实 CAD 另开 RCAD 或 VCAD，不混在结构整理包里。

## 6. 禁止项

- 不因“文件小”删除 public CLI。
- 不合并 safety / evidence / CAD driver 边界来减少文件数。
- 不用截图、dry-run、no-CAD benchmark 或结构审计结果声称真实 CAD 几何准确。
- 不在没有引用审计和过渡说明时移除 `drivers/*` 兼容命名空间。
