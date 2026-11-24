# 性能基准测试报告 (`b_report`)

> **module**: global ｜ **type**: benchmark_report ｜ **run_id**: 20261124_010147 ｜ **updated_at**: 2026-11-24 ｜ **status**: completed

## 1. 运行环境与执行概览

- **运行环境**：`darwin 27.2.0 arm64（Apple M1 Pro）· Python 3.9.13 · pytest 8.4.2`
- **执行命令**：`python3 -B -m pytest tests/benchmark -o python_files="b_*_bench.py" -o cache_dir=tests/tmp/.pytest_cache -q -s`
- **退出码（Exit Code）**：`0`（总耗时：`344 ms`，为命令墙钟耗时，含解释器启动与收集；pytest 自报会话耗时 `0.19s`）

## 2. 性能基准核心指标表

| 基准 ID | 所属模块 | 负载规模 | 采样轮次 | 平均耗时 | P99 延迟 | 吞吐量 (`ops/sec`) | 内存分配 | 较上次变化 (`Δ%`) |
|---|---|---|---|---|---|---|---|---|
| `BM-slugify-001` | `slugify` | 10,000 条标题 | 20（另预热 3 轮） | 6.40 ms/轮 | n/a | 1,563,626 条/s | n/a | baseline |
| `BM-wordcount-001` | `wordcount` | 10,000 词 | 20（另预热 3 轮） | 1585.4 us/轮 | n/a | 630.7 轮/s | n/a | baseline |

以上数值均取自本次运行器 stdout 中基准函数自行打印的计时结果。P99 延迟与内存分配两项：本工程基准采用 `time.perf_counter` 平均计时，不采集这两项指标，如实记 `n/a`。

## 3. 热点分析与基线对比

- 首次运行，没有可对比的上次 `last_run.json`，`Δ%` 记为 `baseline`。
- `BM-wordcount-001` 单轮约 1.6 ms，明显慢于 `BM-slugify-001` 的单条处理速度：词频排序需要对 10,000 词的语料完成整表统计与排序，属于预期的热点形态，当前无退化证据。
