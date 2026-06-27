# CAD Agent Repository Rules

面向用户的说明、状态汇报和结论默认使用中文。代码、命令、路径、文件名、JSON key、Python / CAD / AutoCAD / Git 等专有名称保留英文。

## Current Active Scope

当前主仓是 2026-06-27 cleanroom cut 后的新主线。旧仓内容不在主仓继续维护；恢复来源是：

- tag: `legacy-pre-cleanroom-20260627`
- archive branch: `archive/legacy-pre-cleanroom-20260627`

本仓 active scope 只包括最小 CAD Agent package、Gate 0 桌面场景、compiler eval、真实 AutoCAD smoke、短文档和安全技能卡。

## Startup Route

1. 先读 `README.md` 和本文件。
2. 涉及架构、安全、状态、路线或开发验证时，按需读取：
   - `docs/ARCHITECTURE.md`
   - `docs/SAFETY.md`
   - `docs/STATUS.md`
   - `docs/ROADMAP.md`
   - `docs/DEVELOPMENT.md`
3. 涉及 CAD scene authoring 时，读取 `.agents/skills/cad-scene-authoring/SKILL.md` 及其相关 reference。

## Hard Boundaries

- 不恢复旧 orchestrator、training、workbench、coverage 控制面。
- 不把旧 `core/`、`agents/`、`projects/`、`libraries/`、`output/` 重新放回主仓。
- 新代码不得 import old-system modules，例如 `core.*` 或 `agents.pipeline.*`。
- CAD 写入只能走 `CODEX_PREVIEW`。
- 必须保留 `savedCurrentDwg=false`。
- 必须使用 created handles readback；截图只能作为 visual aid。
- 不写正式图层，不保存当前 DWG，不清空模型空间，不删除非本事务创建对象。
- 不用 exact prompt route 或 keyword shortcut 伪造 Gate 0。

## Verification Expectations

完成代码或文档治理后，优先运行：

```powershell
python -m pytest
python tools/check_import_boundaries.py
python tools/check_cleanroom.py
```

涉及 schema / eval 时追加：

```powershell
python tools/export_schemas.py --output-dir .cad_agent_schemas --check
python tools/run_compiler_eval.py --backend fake --cases evals/compiler/cases.jsonl
```

涉及真实 AutoCAD 能力时，只能运行 preview-only smoke，并明确 checked / not_checked：

```powershell
python tools/run_real_cad_backend_smoke.py --preview-only --rollback-after-check
```

## Completion Language

任何完成声明都要说明：

- 自动测试是否通过。
- cleanroom 检查是否通过。
- 真实 AutoCAD 是否实际跑过。
- 是否只写 `CODEX_PREVIEW`。
- 是否确认 `savedCurrentDwg=false`。
- 哪些能力仍未证明。
