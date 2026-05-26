# BETA-PROJECT-SAMPLE 父包验收（01–05）

最后更新：2026-05-26

## 可声称

- `projects/` 脱敏样本协议与 manifest 扫描可用（01）。
- `sample_blank_shell` fixtures + loader + 金样回归（02）。
- blank-shell workflow 产出 CAD_PLAN / dry-run valid / verification unverified（03）。
- `project_sample_benchmark` 含 pass + `blocked_expected_non_cad`（04）。
- 可选 CODEX_PREVIEW CAD check 入口（05）：fake driver 可验证 created-handle readback 逻辑；`--no-cad` 输出 deferred 证据；`--require-cad-verified` 会拒绝把 deferred 当成真实 CAD 通过。

## 不可声称

- 样本 benchmark pass **≠** 全项目 `geometry_verified`。
- 当前仓库存档的 no-CAD 样本 CAD check **≠** 真实 AutoCAD `geometry_verified`。
- blocked 过小样本 **≠** 可交付布局。
- 单一样本 CAD 验证 **≠** 任意 DWG / 块库 / 正式图层已准确。

## 证据索引

| 小包 | 文档 |
| --- | --- |
| 01 | `beta_project_sample_01_boundaries.md` |
| 02 | `beta_project_sample_02_boundaries.md` |
| 03 | `beta_project_sample_03_boundaries.md` |
| 04 | `beta_project_sample_04_boundaries.md` |
| 05 | `beta_project_sample_05_boundaries.md` |
