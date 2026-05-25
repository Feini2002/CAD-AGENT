# System Hardening Audit

日期：2026-05-25

## Scope

本轮只做无 CAD 的系统安全重构、代码债排查、BUG 寻找和维护性优化。真实 CAD 落图、截图和实体回读仍归 Phase W。

## Baseline

最终基线以 2026-05-25 的系统层收尾验证为准：

- `unittest discover -s tests`：196 tests OK。
- `self_check.py`：pass。
- `render_preview.py --check`：ready。
- `blank_shell_core_benchmark`：4/4 pass。
- `run_cad_validation.py --no-cad`：pass。
- `run_repo_audit.py --max-python-lines 500 --fail-on-findings`：pass，0 findings。
- Real CAD validation：not run in this hardening round。

## Initial Findings

- `core/capabilities/registry.py` 是当前最大 Python 文件，需要拆分为 runner、metadata、validation 和 facade。
- `tests/core/*.py` 中存在重复 `sys.path.insert`，需要收敛到 `tests/bootstrap.py`。
- `scripts/*.py` 中存在重复项目根路径注入，需要收敛到 `scripts/_bootstrap.py`。
- blank-shell pipeline 已通过 4 场景 benchmark，但缺少对坏 workflow / 坏输入的可解释失败测试。
- verification 和 CAD validation 已有证据门，但仍需要边界测试保护报告落盘与失败分类。

## Completed Hardening Work

- 新增 `core/maintenance/repo_audit.py` 和 `scripts/run_repo_audit.py`，提供无 CAD repo audit；默认作为信息性报告返回 0，使用 `--fail-on-findings` 时可作为质量门禁返回 1。
- `repo_audit` 使用 AST 识别真实 `sys.path.insert(...)` 调用，避免 fixture 字符串误报；忽略 `.venv`、`venv`、`node_modules`、`.pytest_cache`、`.mypy_cache`、`.ruff_cache`、`output` 等本机或生成目录。
- 新增 `tests/bootstrap.py`，并把 `tests/core/test_*.py` 中的本地路径注入收敛到统一测试 bootstrap；fixture 字符串保留，由 AST 测试区分。
- 新增 `scripts/_bootstrap.py`，统一脚本项目根路径注入与 Windows UTF-8 stdout/stderr 配置；脚本入口兼容直接执行和包导入。
- 将 `core/capabilities/registry.py` 拆分为 `registry.py` facade、`runners.py`、`specs.py` 和 `validation.py`，保持 `list_capabilities()`、`get_capability()`、`validate_capability_registry()`、`run_capability()` 公共 API 不变。
- `validate_capability_registry()` 现在校验 `runner` 是否 callable，避免 metadata 损坏后运行时才暴露。
- `core/workflows/blank_shell_pipeline.py` 增加 workflow 输入预检，缺少 `inputs.shell_model`、路径字段类型错误或显式空 `object_types: []` 时返回结构化 `invalid`，不再抛未分类异常或静默回退。
- `core/verification/cad_validation_runner.py` 增加 `run_validation()` 兼容入口；相对 `output_dir` 会解析到指定 root 下。
- `core/verification/verification_report.py` 支持 `screenshot_path` 传入字符串；截图缺失时保持 `unverified`，不会升级几何验证状态。
- `drivers/*.py` legacy wrappers 已移除本地 `sys.path.insert(...)`，改为复用共享 bootstrap，repo audit 门禁不再留下 driver findings。
- `repo_audit` 已扩展到 `sys.path.append/extend`、`import sys as ...`、`from sys import path ...` 和 `__path__.append(...)` 等路径污染形态。
- `blank_shell_pipeline` 已在读 workflow、读输入文件和写 output artifacts 前做路径边界检查；workflow 缺文件、坏 JSON、越界输入和越界输出都会返回结构化 `invalid`，不再 traceback 或写到 repo 外。
- capability runner 的路径型入口已限制在 project root 和 `output/` 下，避免 payload 传入绝对路径或 `..` 时读写仓库外路径。
- `run_validation()` 相对 `output_dir` 会按显式 `root` 解析，避免 `root != cwd` 时报告写错位置。

## Final Verification

- Repo audit command: `& $py scripts\run_repo_audit.py --max-python-lines 500`
- Repo audit gate example: `& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings`
- Unit tests: `& $py -m unittest discover -s tests`
- Self check: `& $py scripts\self_check.py`
- Render preview check: `& $py scripts\render_preview.py --check`
- Blank-shell pipeline: `& $py scripts\run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\hardening-polish`
- Blank-shell benchmark: `& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\hardening-polish`
- No-CAD validation: `& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad`

2026-05-25 final run:

- Focused hardening tests：56 tests OK。
- Full unit tests：196 tests OK。
- `self_check.py`：pass。
- `render_preview.py --check`：ready。
- `validate_plan.py examples\plans\draw_test_cabinet.json`：`VALID CAD_PLAN`。
- `dry_run_plan.py examples\plans\draw_test_cabinet.json`：`CAD_PLAN DRY RUN`。
- `inspect_dwg.py --plan examples\plans\draw_test_cabinet.json --format json --no-cad`：`VERIFICATION_REPORT(unverified)`。
- `run_blank_shell_pipeline.py examples\workflows\blank_shell_layout_loop.json --output-dir output\test_artifacts\blank_shell_pipeline\hardening-polish`：status `ok`。
- `run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\hardening-polish`：4/4 pass。
- `run_cad_validation.py --no-cad --output-dir output\validation_runs\hardening-polish-no-cad`：status `pass`。
- `run_repo_audit.py --max-python-lines 500`：valid JSON, 0 findings.
- `run_repo_audit.py --max-python-lines 500 --fail-on-findings`：pass。

## Remaining Risks

- Real CAD geometry accuracy still requires Phase W readback.
- `repo_audit` intentionally focuses on common Python path mutation shapes; it is still not a complete static analyzer for every dynamic alias or metaprogrammed path mutation.
- `core/capabilities/specs.py` is metadata-heavy by design. Split it further only if catalog size starts to harm review or ownership.
- This round does not change scene Agent business behavior and does not implement Phase W / X acceptance.
