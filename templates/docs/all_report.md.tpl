# 全量测试综合报告 (`all_report`)

> **module**: global ｜ **type**: all_report ｜ **run_id**: <run_id> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <passed|failed|error>

## 1. 双轨执行总览

| 测试轨道 | 运行状态 | 退出码 | 用例总数 | 通过 / 完成 | 失败 / 退化 | 耗时 | 详细报告 |
|---|---|---|---|---|---|---|---|
| 单元测试 (`unittest`) | `<unit_status>` | `<unit_exit_code>` | 0 | 0 | 0 | 0 ms | [u_report_latest.md](u_report_latest.md) |
| 基准测试 (`benchmark`) | `<bench_status>` | `<bench_exit_code>` | 0 | 0 | 0 | 0 ms | [b_report_latest.md](b_report_latest.md) |

## 2. 模块健康度矩阵

| 模块 (`module`) | 单测通过率 | 基准核心吞吐 (`ops/sec`) | 未实现/待补项 (`Gaps`) | 综合评估 |
|---|---|---|---|---|
| `<module>` | 0 / 0 (0.0%) | `<ops_per_sec>` (`BM-<module>-001`) | 0 | `<health_status>` |

## 3. 本次运行信息

- **运行批次**：`<run_id>`（执行时间：`<executed_at>`，范围：`all`）
- **单测命令**：`<unit_runner_command>`
- **基准命令**：`<benchmark_runner_command>`
- **状态文件**：`tests/.state/last_run.json`
