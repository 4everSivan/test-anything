# 性能基准测试报告 (`b_report`)

> **module**: global ｜ **type**: benchmark_report ｜ **run_id**: 20261124_102731 ｜ **updated_at**: 2026-11-24 ｜ **status**: completed

## 1. 运行环境与执行概览

- **运行环境**：`darwin 27.2.0 arm64（Apple M1 Pro）· Python 3.9.13 · pytest 8.4.2`
- **执行命令**：`python3 -B -m pytest tests/benchmark -o python_files="b_*_bench.py" -o cache_dir=tests/tmp/.pytest_cache -q -s`
- **退出码（Exit Code）**：`0`（总耗时：`512 ms`，为命令墙钟耗时，含解释器启动与收集；pytest 自报会话耗时 `0.23s`）
- 基准测试不采集覆盖率；本报告的数值全部取自本次运行器 stdout 中基准函数自行打印的计时结果。

## 2. 性能基准核心指标表

| 基准 ID | 所属模块 | 负载规模 | 采样轮次 | 平均耗时 | P99 延迟 | 吞吐量 (`ops/sec`) | 内存分配 | 较上次变化 (`Δ%`) |
|---|---|---|---|---|---|---|---|---|
| `BM-slugify-001` | `slugify` | 10,000 条标题 | 20（另预热 3 轮） | 7.33 ms/轮 | n/a | 1,364,755 条/s | n/a | -12.7% |
| `BM-wordcount-001` | `wordcount` | 10,000 词 | 20（另预热 3 轮） | 2076.7 us/轮 | n/a | 481.5 轮/s | n/a | -23.7% |

P99 延迟与内存分配两项：本工程基准采用 `time.perf_counter` 平均计时，不采集这两项指标，如实记 `n/a`。`Δ%` 为吞吐量相对上一次 `last_run.json`（`run_id` 20261124_010147）的变化。

## 3. 热点分析与基线对比

- 与上次记录相比，两条基准的吞吐量分别下降 12.7% 与 23.7%，其中 `BM-wordcount-001` 的降幅超过 `regression_threshold_pct`（默认 15%），按规则列为关注项；基准测试没有通过与否的门槛，轨道状态为 `completed`。
- 两次运行之间业务源码与基准代码均未改动（`manifest.json` 中的哈希一致），差异来自同一台机器在不同时刻的负载波动：单次平均耗时从 1585.4 us 升到 2076.7 us。判定是否为真实退化，需要在空闲机器上重复运行后再比较，不应仅凭这一次结果下结论。
- `BM-wordcount-001` 单轮约 2 ms，明显慢于 `BM-slugify-001` 的单条处理速度：词频排序需要对 10,000 词的语料完成整表统计与排序，属于预期的热点形态。
