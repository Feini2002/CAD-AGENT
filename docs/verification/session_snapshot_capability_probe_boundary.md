# Session Snapshot Capability Probe Boundary

最后更新：2026-05-27

## LCAD-13-SESSION-SNAPSHOT-CAD

`LCAD-13-SESSION-SNAPSHOT-CAD` 把 `cad_session_guard` 的 ActiveDocument before/after snapshot 接入 `run_cad_capability_probe()`。能力探针在 preview-only 写入前后各采集一次会话快照，并把 `session_guard` 写入：

- `cad_capability_probe.json` 的 `session_guard` 字段
- 同目录 `active_document_snapshot.json`

通过 `cad_capability_verified` 时，机器可读证据必须满足：

- `session_guard.status=consistent`
- `session_guard.comparison.checks` 中 `active_document_identity_stable=pass`
- `preview_layer_entity_delta` 随 preview 写入增加（负向 runner 仍要求 delta=0）

该边界服务于 `V-PROOF-52`：guard / snapshot / audit 字段可在 capability probe 报告中断言，但不能替代 created-handle readback 或 `geometry_verified`。

## 不得声称

- 不得把 `session_guard.status=consistent` 说成任意 CAD_PLAN 或正式图层已安全通过。
- 不得用 fake driver 的 snapshot 证据替代真实 AutoCAD ActiveDocument 会话复验。
- 不得因为 snapshot JSON 存在就登记为几何通过；几何结论仍以 `created_handles` 定向回读与 `entity_evidence` 为准。
