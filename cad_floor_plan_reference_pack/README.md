# CAD 平面布局图参考包

创建时间：2026-05-28

> 说明：`files/` 下的第三方 DWG/DXF 只作为本机学习素材，默认被 `.gitignore` 排除；GitHub 仓库只提交来源索引、下载记录和许可边界说明。

本包用于 CAD Agent 的学习、测试、解析和样例参考。已下载文件优先选择免登录、页面明确标注 `free` 或样例用途的来源；中文设计资源站点因多含登录、会员、评论、百度网盘或授权边界不清，本包先保留索引，不直接搬运整包。

## 目录

- `files/`：已下载到本地的 DWG/DXF 样例。
- `source_pages/downloaded_sources.md`：已下载文件的来源和下载记录。
- `source_pages/chinese_resource_index.md`：中文 CAD 平面图资源页索引。
- `sources.json`：机器可读的来源清单。

## 已下载文件

| 文件 | 类型 | 来源 | 用途边界 |
| --- | --- | --- | --- |
| `files/dwgmodels_house.dwg` | DWG | DWG Models / House | 页面标注 free；用于学习和内部测试 |
| `files/dwgmodels_house_3.dwg` | DWG | DWG Models / House 3 | 页面标注 free；用于学习和内部测试 |
| `files/dwgmodels_two_story_house_plans.dwg` | DWG | DWG Models / Two story house plans | 页面标注 free；用于学习和内部测试 |
| `files/dwgvieweronline_sample_floor_plan_assets.dxf` | DXF | DWG Viewer Online sample | 页面说明 no cost for educational and testing purposes |

## 授权与使用提醒

- 这些文件适合做解析、图元识别、平面布局学习、CAD Agent 回归样例和内部验证。
- 不建议把这些第三方图纸再打包公开分发，除非逐一确认原站许可。
- 中文资源站中含“可商用”的页面仍应以站点授权、账号下载协议和付费授权说明为准。
- 若要纳入正式 benchmark，应在 `sources.json` 中补齐下载日期、许可依据、用途限制和原始 URL。
