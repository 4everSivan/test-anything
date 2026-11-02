# 性能基准测试报告 (`b_report`)

> **module**: global ｜ **type**: benchmark_report ｜ **run_id**: <run_id> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <completed|failed|error>

## 1. 运行环境与执行概览

- **运行环境**：`<os_cpu_runtime_info>`
- **执行命令**：`<benchmark_runner_command>`
- **退出码（Exit Code）**：`<exit_code>`（总耗时：`<duration_ms> ms`）

## 2. 性能基准核心指标表

| 基准 ID | 所属模块 | 负载规模 | 采样轮次 | 平均耗时 | P99 延迟 | 吞吐量 (`ops/sec`) | 内存分配 | 较上次变化 (`Δ%`) |
|---|---|---|---|---|---|---|---|---|
| `BM-<module>-001` | `<module>` | `<workload>` | 100 | 0.0 us/op | 0.0 us | 0 ops/s | 0 B/op | baseline |

## 3. 热点分析与基线对比

- `<hotspot_and_regression_summary>`
