# 性能基准测试报告 (`b_report`)

> **module**: global ｜ **type**: benchmark_report ｜ **run_id**: 20261124_011704 ｜ **updated_at**: 2026-11-24 ｜ **status**: completed

## 1. 运行环境与执行概览

- **运行环境**：`darwin arm64 · cpu: Apple M1 Pro · GOMAXPROCS=8 · go1.26.4`
- **执行命令**：`GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp go test ./tests/benchmark -run '^$' -bench . -benchmem -count=1`
- **退出码（Exit Code）**：`0`（总耗时：`3554 ms`，为命令墙钟耗时，含编译与链接；`go test` 自报包耗时 `3.393s`）

## 2. 性能基准核心指标表

| 基准 ID | 所属模块 | 负载规模 | 采样轮次 | 平均耗时 | P99 延迟 | 吞吐量 (`ops/sec`) | 内存分配 | 较上次变化 (`Δ%`) |
|---|---|---|---|---|---|---|---|---|
| `BM-calc-001` | `calc` | 每轮 1,000 次加法 | 2,887,225 | 403.5 ns/op | n/a | 2,478,315 op/s | 0 B/op，0 allocs/op | baseline |
| `BM-textutil-001` | `textutil` | 4,096 字符的字符串 | 51,825 | 23507 ns/op | n/a | 42,539 op/s | 21248 B/op，2 allocs/op | baseline |

以上数值均取自本次 `go test -bench` 的 stdout：轮数、`ns/op`、`B/op` 与 `allocs/op` 为运行器原样输出，吞吐量按 `10^9 / ns/op` 换算。P99 延迟：`go test -bench` 只报告平均耗时，不采集分位延迟，如实记 `n/a`。

## 3. 热点分析与基线对比

- 首次运行，没有可对比的上次 `last_run.json`，`Δ%` 记为 `baseline`。
- `BM-textutil-001` 每轮约 23.5 us 并产生 2 次内存分配（约 21 KB），符合“rune 切片解码 + 重新编码”的预期开销，是 `textutil` 模块的主要热点；`BM-calc-001` 零分配，无内存压力。
