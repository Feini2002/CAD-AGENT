# CFIT-12：工装子场景代表对象 CAD smoke

最后更新：2026-05-27

## CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE

为 `meeting_room` / `reception` 各选定一组 **catalog 代表对象**，提供可复跑的 `draw_object` CAD smoke 清单与 runner，服务 `V-PROOF-25` 与 `RCAD-18` / `RCAD-19`。

| 子场景 | 代表对象 | `sample_id` | RCAD |
| --- | --- | --- | --- |
| `meeting_room` | `meeting_table`, `meeting_chair` | `commercial_fitout_meeting_sample` | `RCAD-18-FITOUT-MEETING` |
| `reception` | `reception_desk`, `waiting_sofa` | `commercial_fitout_reception_sample` | `RCAD-19-FITOUT-RECEPTION` |

机器入口：

- `examples/capability_proof/fitout_subscene_object_cad_smoke_manifest.json`
- `core/verification/fitout_subscene_object_cad_smoke.py`
- `scripts/run_fitout_subscene_object_cad_smoke.py`

```powershell
python scripts/run_fitout_subscene_object_cad_smoke.py --no-cad --output-dir output/validation_runs/cfit-12-subscene-smoke-no-cad
python scripts/run_fitout_subscene_object_cad_smoke.py --subscene-id meeting_room --output-dir output/validation_runs/cfit-12-meeting-real
```

## 退出条件（本包）

- manifest 覆盖 `meeting_room` + `reception` 各 ≥2 代表对象，且 `registry_capability_id` 与 catalog manifest 一致。
- fake driver 全量跑通：`2` 子场景 × `2` 对象 = `4/4` `geometry_verified`（单测）。
- `assert_fitout_subscene_object_manifest_contract()` 通过。

## 不得声称

- 不得因 fake/no-CAD smoke 通过就声称 `RCAD-18` / `RCAD-19` 项目样本已在真实 AutoCAD 会话几何证明。
- 不得将四对象 smoke 扩大为全部 14 项 catalog 或任意工装项目几何准确。
- `open_office` 代表对象仍由既有 catalog smoke / 开放办公样本路径覆盖；本包不重复登记 open_office 行。
