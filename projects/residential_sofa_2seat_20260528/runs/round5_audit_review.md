# Round5 自检（语义重绘）

## 根因（回应你的判断）

**你说得对：** 左侧参考块本身就不是「严丝合缝」画法——343 段直线、156 条 L<6mm 微线、36 个开放端点，圆角靠碎线+R30 拼出来，箭头处也有不 trim 的 T 交。
我们 round1–4 做的是 **clone + 裁切 + 去杂线**，等于继承「毛躁 DNA」，再在接缝加一层毛刺，所以多轮补丁无法根治。

## 本轮做法（提高维度）

| 旧路线 | 新路线 round5 |
| --- | --- |
| 复制块内 Line/Arc | 只读参考块 **尺寸** |
| 197 实体 / 72 微线 | **46 实体 / 0 微线** |
| 碎线拼弧 | **圆角矩形 + 真弧**（R≈30） |
| 验收=像供应商逐线 | 验收=**语义同款 + 干净** |

## 机器审计（`audit_checklist_semantic.json`）

| 项 | 结果 | 门槛 |
| --- | --- | --- |
| preview_width_mm | 1866.7 | 1850–1885 |
| entity_total | 46 | ≤60 |
| micro_line_count | 0 | 0 |
| open_endpoint_count | 12 | ≤16（内部分割线 T 交，非断线） |
| arc_count | 20 | ≥16 |

`audit_pass: true`

## 视觉自检

- 右侧预览线 **连续、无出头杂毛**（对比 round3/4 截图）
- 外框 + 两格坐垫/靠背 + 中缝 + 顶底横档，**意思与左图两座同款**
- 圆角/角度为参数近似，**不追求与供应商块完全一致**

## 证据

- `runs/round5_preview.png`
- `runs/round5_geometry_audit.json`
- `runs/round5_root_cause.md`

## 请你验收

看 `round5_preview.png`：**线条是否还毛躁？两座语义是否对？** 回 pass / fail。
