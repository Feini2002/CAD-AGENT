# CAD Agent 卡壳自查与自我迭代方法论

这个文件是横向机制，不属于某一个固定阶段。无论当前在阶段 4 预览绘制、阶段 5 回读验证，还是以后对象库和行业包开发，只要出现“画不出来、画不准、验证不了、截图缺失、环境不通”，都先按这里处理。

## 什么时候触发

出现下面任一情况，就进入卡壳自查流程：

- 用户说“画不准”“画不出来”“这里不对”“继续修一下”。
- `CAD_PLAN` 生成后无法通过校验。
- dry-run 和用户白话不一致。
- 执行脚本报错，或没有产生预期 CAD 实体。
- 预览图层里画了内容，但位置、尺寸、图层、文字或标注不对。
- 需要视觉判断，但当前没有截图、预览图或回读报告。
- 我无法明确回答“错在白话理解、CAD_PLAN、脚本、驱动、CAD 环境、还是验证工具”。

## 基本原则

1. 先停住正式落图，只允许在 `CODEX_PREVIEW` 或测试输出里排查。
2. 不重复盲画。每次重试前必须说明上一轮失败证据和本轮假设。
3. 先保留证据，再修改代码或规则。
4. 用最小复现定位问题，不直接扩大到复杂项目图纸。
5. 能自动检查的先自动检查，不能自动检查的先补检查入口。
6. 修复后必须更新状态、变更记录；如果是错误或失败，还要更新问题记录。

## 自查闭环

```text
1. 读取状态
   -> README.md
   -> CAD_AGENT_STATUS.md
   -> CAD_AGENT_RULES.md
   -> CAD_AGENT_ISSUES.md
   -> 本文件

2. 分类卡点
   -> 白话理解
   -> CAD_PLAN 结构
   -> Schema 校验
   -> dry-run 预演
   -> CAD 执行
   -> 截图/视觉检查
   -> 回读验证
   -> 运行环境

3. 建最小复现
   -> 优先使用 examples/plans/draw_test_cabinet.json
   -> 复杂问题再新增 tests/plans/ 下的专用样例
   -> 不直接在正式 DWG 上试错

4. 收集证据
   -> python scripts/self_check.py
   -> python scripts/validate_plan.py <plan>
   -> python scripts/dry_run_plan.py <plan>
   -> python scripts/render_preview.py --check
   -> 如已绘制，优先使用 render_preview.py --capture-autocad-window 保存 AutoCAD 客户区视觉检查点

5. 定位原因
   -> 对比用户白话和 CAD_PLAN
   -> 对比 CAD_PLAN 和 dry-run 输出
   -> 对比 dry-run 和实际绘制/截图/回读结果
   -> 分清是规则问题、数据问题、脚本问题、驱动问题还是环境问题

6. 最小修复
   -> 先补测试或复现样例
   -> 只改直接相关文件
   -> 不借机做大重构

7. 复验与记录
   -> 重新运行相关验证命令
   -> 视觉问题必须留下截图或明确说明无法截图的原因
   -> 更新 CAD_AGENT_STATUS.md
   -> 更新 CAD_AGENT_CHANGELOG.md
   -> 如果是失败修复，更新 CAD_AGENT_ISSUES.md
```

## 画不准时的专门处理

如果用户用白话要求画某个东西，但结果位置、尺寸或形状不准，按下面顺序排查：

1. 把用户白话改写成明确的 CAD 意图：对象、尺寸、基点、图层、文字、标注。
2. 检查 `CAD_PLAN` 是否真的表达了这几个要素。
3. 检查 dry-run 输出的尺寸和坐标是否符合预期。
4. 检查执行结果是否只落在 `CODEX_PREVIEW`。
5. 截图或导出预览，确认肉眼看到的结果。
6. 如果截图能力不可用，先补截图或记录替代证据，再继续修绘图逻辑。
7. 如果截图和回读冲突，以 CAD 实体回读为准，截图作为视觉辅助。

## 什么时候问用户

只有下面情况才把问题交回用户确认：

- 用户意图本身有多种合理解释，且继续猜会影响正式图纸。
- 需要修改正式图层、保存 DWG、覆盖原图或删除实体。
- 需要安装新依赖、启用新权限或操作当前 CAD 窗口。
- 已经完成最小复现，但证据显示缺少用户侧项目信息。

## 当前工具入口

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py 'scripts\self_check.py'
& $py 'scripts\render_preview.py' --check
& $py 'scripts\render_preview.py' --capture-autocad-window --output 'output\previews\manual-check.png'
```

截图命令只在用户允许或确实需要视觉证据时运行；它会优先截取 AutoCAD 客户区，保存到 `output/previews/`。截图仍只作为视觉辅助，几何准确以 created handles 回读为准。
