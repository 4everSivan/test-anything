# 全局测试总计划 (Test Plan)

> **module**: global ｜ **type**: test_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 目标技术栈与执行环境

- **主语言与框架**：`Go 1.21+ / go test`（以 `go test <包路径>` 方式从工程根目录启动）
- **单元测试运行命令**：`GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp go test ./tests/unit -v -count=1`
- **基准测试运行命令**：`GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp go test ./tests/benchmark -run '^$' -bench . -benchmem -count=1`
- **运行期临时目录**：`tests/tmp/`（所有临时文件、缓存与覆盖率原始数据强制落盘于此）。Go 要求 `GOCACHE` 与 `GOTMPDIR` 为绝对路径，故用 `$(pwd)` 拼出；`-count=1` 禁用测试结果缓存，保证每次都是真实执行

## 2. 模块测试覆盖总表

| 模块 (`module`) | 模块计划 | 单测规格 (`u_`) | 基准规格 (`b_`) | 单测代码 (`unit/`) | 基准代码 (`benchmark/`) | 公共夹具 (`fixtures/`) |
|---|---|---|---|---|---|---|
| `calc` | [calc_plan.md](calc_plan.md) | [u_calc_cases.md](../cases/u_calc_cases.md) | [b_calc_cases.md](../cases/b_calc_cases.md) | `tests/unit/u_calc_test.go` | `tests/benchmark/b_calc_bench_test.go` | `tests/fixtures/calc_fixtures.json` |
| `textutil` | [textutil_plan.md](textutil_plan.md) | [u_textutil_cases.md](../cases/u_textutil_cases.md) | [b_textutil_cases.md](../cases/b_textutil_cases.md) | `tests/unit/u_textutil_test.go` | `tests/benchmark/b_textutil_bench_test.go` | `tests/fixtures/textutil_fixtures.json` |

## 3. 全局夹具与隔离策略

- 外部网络、第三方服务与非受控 I/O 一律通过 `tests/fixtures/` 隔离（本工程为纯函数，实际无外部依赖，`go.mod` 无第三方模块）。
- 运行期产生的所有临时文件与本地沙箱数据统一输出至 `tests/tmp/`。
