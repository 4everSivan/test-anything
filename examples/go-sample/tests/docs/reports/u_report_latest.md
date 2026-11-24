# 单元测试执行报告 (`u_report`)

> **module**: global ｜ **type**: unit_report ｜ **run_id**: 20261124_102915 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 执行概览

- **执行命令**：`GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp go test ./tests/unit -v -count=1 -coverprofile=tests/tmp/coverage/unit.out -coverpkg=./...`
- **退出码（Exit Code）**：`0`
- **执行时间**：`2026-11-24T10:29:15+08:00`（总耗时：`2050 ms`，为命令墙钟耗时，含编译、链接与覆盖率插桩；`go test` 自报包耗时 `1.358s`）

| 总用例数 | 通过 (Passed) | 失败 (Failed) | 跳过 (Skipped) | 通过率 | 行覆盖率 | 分支覆盖率 |
|---|---|---|---|---|---|---|
| 6 | 6 | 0 | 0 | 100.0% | 100% | N/A |

- **覆盖率来源**：在同一次 `go test` 运行中通过 `-coverprofile` 采集，没有为覆盖率额外再跑一遍测试；`-coverpkg=./...` 覆盖模块内的全部业务包，原始 profile 写入 `tests/tmp/coverage/unit.out`，再由 `scripts/ta-verify --coverage` 解析后写入 `tests/.state/last_run.json` 的 `unit.coverage`。
- **分支覆盖率为 N/A 的原因**：Go 的覆盖率只有语句块一级，不提供分支维度的数据，所以“分支覆盖率”不适用，如实记 N/A 而不是 0 或 100%。
- **逐模块覆盖率**：`calc` 行 100%；`textutil` 行 100%。

## 2. 模块与用例执行明细

| 用例 ID | 所属模块 | 场景类型 | 绑定测试函数 | 状态 | 耗时 (ms) |
|---|---|---|---|---|---|
| `UT-calc-001` | `calc` | `normal` | `TestUT_Calc_001_AddPositiveIntegers` | PASS | `<5` |
| `UT-calc-002` | `calc` | `exception` | `TestUT_Calc_002_DivideByZeroReturnsError` | PASS | `<5` |
| `UT-calc-003` | `calc` | `boundary` | `TestUT_Calc_003_DivideTruncatesTowardZero` | PASS | `<5` |
| `UT-textutil-001` | `textutil` | `normal` | `TestUT_Textutil_001_ReversesRunes` | PASS | `<5` |
| `UT-textutil-002` | `textutil` | `boundary` | `TestUT_Textutil_002_ReversesEmptyAndUnicodeText` | PASS | `<5` |
| `UT-textutil-003` | `textutil` | `normal` | `TestUT_Textutil_003_DetectsPalindromes` | PASS | `<5` |

逐条用例耗时低于 `go test -v` 的输出精度（运行器原样输出为 `(0.00s)`），故记为 `<5` ms，不以模板占位 `0` 充数。未跳过任何用例（运行器输出中没有 `SKIP` 行）。

## 3. 失败与异常诊断

本次运行全部通过，无失败用例。

## 4. 未覆盖符号

本次运行覆盖了全部已统计的业务源码语句块：`calc/calc.go` 4 个语句块、`textutil/textutil.go` 4 个语句块均已执行，`unit.coverage.uncovered[]` 为空，没有未覆盖符号。
