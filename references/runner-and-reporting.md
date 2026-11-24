# Test Execution (`run`) and Three-Part Reporting Engine

This reference owns `$test-anything run`, `$test-anything run unittest`, and `$test-anything run benchmark`.

## 1. Strict Decoupling Preflight Gate

Before executing any test runner:
1. Verify that `tests/.state/manifest.json` exists, parses as valid JSON, and records `create_status: "complete"` (an absent `create_status` counts as complete).
2. Verify that executable test files exist in `tests/unit/` (when scope is `all` or `unittest`) and/or `tests/benchmark/` (when scope is `all` or `benchmark`).
3. If either check fails, **abort immediately with an error message** instructing the user to run `$test-anything` or `$test-anything create` first. When `create_status` is `"in_progress"`, say that the previous `create` stopped after stage `completed_stage` and that running `create` again resumes it. Never invoke `create` from `run`.

## 2. Isolated Execution and Read-Only Source Invariant

1. **Runner resolution:** Use `tests/.state/config.json` (`unit_runner` / `benchmark_runner`) if non-null; otherwise use `tests/.state/manifest.json.stack`.
2. **`tests/tmp/` isolation:** Ensure `<target_root>/tests/tmp/` exists before running. Pass flags or environment variables (such as `TMPDIR=<target_root>/tests/tmp`, `-o cache_dir=tests/tmp/.pytest_cache`, `--coverageDirectory=tests/tmp/coverage`) so no temporary artifacts pollute the project root or source tree.
3. **Read-only business source:** Target project business source code is strictly read-only during `run`. When a unit test fails or a benchmark regresses, record the failure honestly. Never modify target source code, weaken assertions, or delete failing test cases.

## 3. Three-Part Report Contracts (`tests/docs/reports/`)

Generate a timestamped `run_id` (`YYYYMMDD_HHMMSS`) for each invocation.

Reports keep only the latest run: each report is a single file overwritten in place (`u_report_latest.md`, `b_report_latest.md`, `all_report_latest.md`). Never write per-run copies such as `u_report_<run_id>.md`; the `run_id` in each header identifies the run. Benchmark `Δ%` reads the previous metrics from `tests/.state/last_run.json`, not from old reports.

### 3.0 Track Status Derivation

Derive each track's status mechanically from this run's actual exit code and parsed counts, never from template defaults. Check the rows top to bottom; the first match wins:

| Status | Unit track | Benchmark track |
|---|---|---|
| `not_run` | Track outside the requested scope | Track outside the requested scope |
| `error` | Any of: non-zero exit code with no failing case parsed (crash, collection/import error, usage error, timeout, killed); no case actually executed (none collected, or all skipped); counts cannot be parsed from runner output; exit code `0` while failures were parsed | Same conditions, where "executed" means at least one benchmark produced metrics |
| `failed` | At least one case failed | At least one benchmark failed |
| `passed` / `completed` | Exit code `0`, no failure, and at least one case passed | Exit code `0`, no failure, and at least one benchmark produced metrics |

`all_report_latest.md` takes the worst executed track: `error` if any track is `error`, otherwise `failed` if any track is `failed`, otherwise `passed`. Write values that were not measured as `n/a`, never as the template's `0` placeholders.

### 3.1 Unit Test Report (`u_report_latest.md`)

Render from [templates/docs/u_report.md.tpl](../templates/docs/u_report.md.tpl) with header `> **module**: global ｜ **type**: unit_report ｜ **run_id**: <run_id> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <passed|failed|error>`:
1. `## 1. 执行概览`: Actual command executed, exit code, timestamp, total duration (ms), and summary table (`总用例数` | `通过 (Passed)` | `失败 (Failed)` | `跳过 (Skipped)` | `通过率` | `行覆盖率` | `分支覆盖率`).
2. `## 2. 模块与用例执行明细`: Per-case table mapped via `@case` anchors (`用例 ID` | `所属模块` | `场景类型` | `绑定测试函数` | `状态 (PASS/FAIL/SKIP)` | `耗时 (ms)`).
3. `## 3. 失败与异常诊断`: Write by status:
   - `passed`: `本次运行全部通过，无失败用例。` (only this status may use the sentence; mention the skipped count if non-zero).
   - `failed`: for each `FAIL`, add a subsection `### <UT-id>: <title>` with the linked `cases/u_<module>_cases.md` entry, target source symbol, assertion failure summary, verbatim stack trace block, and single-case reproduction command.
   - `error`: add a subsection `### 运行器异常 (error)` with the exit code, a verbatim excerpt of the tail of stdout/stderr, the suspected cause (such as an import error or no tests collected), and the reproduction command.
4. `## 4. 未覆盖符号`: The coverage table of Section 5 with one row per `unit.coverage.uncovered[]` entry (`模块` | `源码文件` | `符号` | `类型` | `未覆盖行`), or the reason coverage is unavailable.

### 3.2 Benchmark Report (`b_report_latest.md`)

Render from [templates/docs/b_report.md.tpl](../templates/docs/b_report.md.tpl) with header `> **module**: global ｜ **type**: benchmark_report ｜ **run_id**: <run_id> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <completed|failed|error>`:
1. `## 1. 运行环境与执行概览`: OS, CPU/architecture, language runtime version, command executed, exit code, and total duration.
2. `## 2. 性能基准核心指标表`: Per-benchmark table mapped via `@case` (`基准 ID` | `所属模块` | `负载规模` | `采样轮次` | `平均耗时` | `P99 延迟` | `吞吐量 (ops/sec)` | `内存分配` | `较上次变化 (Δ%)`). Compute `Δ%` against the previous `tests/.state/last_run.json` when available, otherwise `baseline`.
3. `## 3. 热点分析与基线对比`: Highlight regressions exceeding `regression_threshold_pct` (default `15.0%`) or SLA targets defined in `b_<module>_cases.md`. When the status is `error`, open this section with the same `### 运行器异常 (error)` subsection as the unit report.

### 3.3 Full-Suite Summary Report (`all_report_latest.md`)

Generated when running `$test-anything run` (scope `all`) from [templates/docs/all_report.md.tpl](../templates/docs/all_report.md.tpl) with header `> **module**: global ｜ **type**: all_report ｜ **run_id**: <run_id> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <passed|failed|error>`:
1. `## 1. 双轨执行总览`: Table summarizing both `unittest` and `benchmark` tracks with links to `u_report_latest.md` and `b_report_latest.md`.
2. `## 2. 模块健康度矩阵`: Per-module unit pass rate, headline benchmark throughput, line coverage (`行覆盖率`, one cell per module taken from `unit.coverage.modules`), open gaps count, and overall health status.
3. `## 3. 本次运行信息`: `run_id`, `executed_at`, scope, the actual unit and benchmark commands, and the state file `tests/.state/last_run.json`.

## 4. State Synchronization

After writing the reports:
- Update `tests/.state/last_run.json` with the actual execution metrics and report paths.
- Refresh the `最新运行状态` column in `tests/docs/README.md`.
- Run the report-only artifact check described in [artifact-verification](artifact-verification.md) Section 6 (`scripts/ta-verify --scope run`) and copy its findings into the run summary unchanged. It reports structure and traceability; it never alters a status, count, exit code, or metric.
- If `tests/docs/reports/` still holds per-run reports written by earlier skill versions (`u_report_<YYYYMMDD_HHMMSS>.md`, `b_report_<YYYYMMDD_HHMMSS>.md`), list their count in the run summary and offer to delete them. Delete only those files, and only after the user's explicit confirmation; otherwise leave them untouched.

## 5. Coverage Collection and Reporting

Coverage shows which business source lines, branches, or statement blocks the unit tests did not execute. It is reported, never used as a gate, and it never changes a test verdict.

1. **Collect for the unit track only, inside the same run.**
   - `run` and `run unittest`: add the coverage flags of the stack to the unit test command and execute it once. Never execute the unit tests a second time for coverage.
   - `run benchmark`: do not collect; write `coverage.status: "not_run"`.
   - The first-batch stacks are Python and Go. For any other `stack.language`, write `coverage.status: "not_supported"` and name the language in `reason`.
2. **Stack commands.** Run them from the target root and put the raw data in `tests/tmp/coverage/`:
   - Python with coverage.py: run the unit tests once under `python3 -m coverage run --branch --source=<business package or source directories> --data-file=tests/tmp/coverage/.coverage -m <the unit runner's module and arguments>`, then export with `python3 -m coverage json --data-file=tests/tmp/coverage/.coverage -o tests/tmp/coverage/coverage.json`. `--source` limits measurement to business source, so `tests/` itself is never counted.
   - Go: append `-coverprofile=tests/tmp/coverage/unit.out` to the `go test` command and, for a multi-package module, `-coverpkg=./...`.
3. **Never install a coverage tool.** Probe availability read-only first, for example `python3 -m coverage --version`. When the tool is missing, run the plain unit command and write `coverage.status: "unavailable"` with the probe result in `reason`. Do not run `pip install`, `poetry add`, `go install`, or anything equivalent.
4. **Parse with the skill's own parser, never by hand.** Run `scripts/ta-verify --target <target_root> --coverage <raw file>` from the skill package. It prints the `coverage` object of the [state-and-backup](state-and-backup.md) Section 4.2 protocol; write that object verbatim into `last_run.json.unit.coverage`. It accepts coverage.py's JSON export, LCOV, and Go's native coverprofile, nothing else. When it exits non-zero, write `coverage.status: "unavailable"` and put its message in `reason`.
5. **Report honestly.**
   - `u_report_latest.md`: add the `行覆盖率` and `分支覆盖率` columns to the Section 1 statistics table and render Section 4 `未覆盖符号` from `uncovered[]`. When `uncovered_omitted` is not empty, state how many entries per module the cap left out.
   - `all_report_latest.md`: add the `行覆盖率` column to the Section 2 module health matrix, one cell per module from `coverage.modules`.
   - Whenever `status` is not `ok`, write `N/A` in every coverage cell and the `reason` in place of the coverage details. Never write `0` for a value that was not measured.
6. **No thresholds and no re-judging.** Do not fail, pass, or rank anything on coverage. A collection or parsing problem never changes a track's `passed` / `failed` / `error` status, the counts, or the exit code, and coverage plays no part in `INV_NO_PASS_WITHOUT_EVIDENCE`. If wrapping the unit command in a coverage tool would change the test result, run the plain command instead and record coverage as unavailable.
