# 通用 CAD Agent 开发包

这里是一个可迁移的“Codex 控制 CAD / CAD Agent”通用开发包。它不绑定当前家装图纸，也不绑定当前电脑；当前目录只是第一个测试现场。

## 仓库简介

CAD-AGENT 是一个面向 Codex 的通用 CAD Agent 开发包，用结构化 `CAD_PLAN` 把自然语言 CAD 需求转换成可校验、可预演、可执行的绘图流程。目标是在安装好 Codex、CAD 软件、CAD-MCP/Python 环境的电脑上，复用同一套规则、Schema、脚本和行业对象库，支持住宅、工装、店铺、办公、餐饮、展陈等多场景 CAD 自动化开发。

这个文件夹应该可以复制到任何新的 CAD 项目目录中继续使用。新电脑只要准备好 Codex、CAD 软件、CAD-MCP 或 AutoCAD COM、Python 运行环境，就可以读取这套规则、Schema、示例和脚本，恢复同一套开发状态。

```text
本文件夹 = CAD Agent 的方法、规则、Schema、脚本和开发记录
运行环境 = Codex、CAD、CAD-MCP、Python、依赖和权限
项目图纸 = 当前要处理的 DWG/PDF/现场 CAD 文件
```

三者配合起来，才是完整的 CAD Agent 能力。

## 每次回来怎么恢复

先看本 `README.md`，再看这 4 个项目管理文件：

1. `CAD_AGENT_STATUS.md`：当前开发到哪一步。
2. `CAD_AGENT_RULES.md`：长期规则，约束 Codex 后续行为。
3. `CAD_AGENT_CHANGELOG.md`：每次改了什么，为什么改。
4. `CAD_AGENT_ISSUES.md`：测试失败、错误、修复经验。

## 当前核心路线

```text
白话或语音
-> Codex 生成 CAD_PLAN
-> validate_plan.py 校验
-> dry_run_plan.py 预演
-> execute_plan.py 调用 CAD 绘制
-> 先画到 CODEX_PREVIEW
-> 回读验证
-> 用户确认后再正式落图
```

这条路线适用于住宅家装、商业工装、零售店铺、办公空间、餐饮空间、展厅展陈，以及其他可用 CAD 平面表达的场景。

## 文件夹说明

```text
cad_agent/       通用 CAD Agent 设计说明，不绑定具体项目
docs/            路线图、历史文档、开发说明
skills/          将来给 Codex 使用的 CAD Skill 草稿
schemas/         CAD_PLAN、CAD_CONTEXT 等 JSON Schema
examples/        通用示例 CAD_PLAN 和示例上下文
scripts/         校验、预演、执行、回读脚本
drivers/         AutoCAD / ZWCAD / DXF 等底层驱动
libraries/       通用对象库和行业包
tests/           测试计划和测试样例
output/          预览、截图、临时输出
```

## 防跑偏原则

任何新能力都必须能回答：

```text
1. 用户会怎么用白话说？
2. 对应的 CAD_PLAN 是什么？
3. 哪个脚本负责校验？
4. 哪个脚本负责执行？
5. 画完后怎么验证？
```

如果回答不了，就先不要进入 CAD 绘制。

## 迁移到新电脑时

复制本文件夹后，先检查：

```text
1. 新电脑是否已安装 CAD 软件。
2. Codex 是否能读取本文件夹。
3. CAD-MCP 或 AutoCAD COM 是否可用。
4. Python 运行环境是否可用。
5. 是否能运行 examples/plans/draw_test_cabinet.json 的 validate 和 dry-run。
```

通过这些检查后，再接入具体项目图纸。
