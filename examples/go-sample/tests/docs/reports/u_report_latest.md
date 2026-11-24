# 单元测试执行报告 (`u_report`)

> **module**: global ｜ **type**: unit_report ｜ **run_id**: 20261124_011704 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 执行概览

- **执行命令**：`GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp go test ./tests/unit -v -count=1`
- **退出码（Exit Code）**：`0`
- **执行时间**：`2026-11-24T01:17:04+08:00`（总耗时：`960 ms`，为命令墙钟耗时，含编译与链接；`go test` 自报包耗时 `0.477s`）

| 总用例数 | 通过 (Passed) | 失败 (Failed) | 跳过 (Skipped) | 通过率 |
|---|---|---|---|---|
| 6 | 6 | 0 | 0 | 100.0% |

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
