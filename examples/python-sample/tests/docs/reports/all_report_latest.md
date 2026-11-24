# 全量测试综合报告 (`all_report`)

> **module**: global ｜ **type**: all_report ｜ **run_id**: 20261124_010147 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 双轨执行总览

| 测试轨道 | 运行状态 | 退出码 | 用例总数 | 通过 / 完成 | 失败 / 退化 | 耗时 | 详细报告 |
|---|---|---|---|---|---|---|---|
| 单元测试 (`unittest`) | `passed` | `0` | 6 | 6 | 0 | 263 ms | [u_report_latest.md](u_report_latest.md) |
| 基准测试 (`benchmark`) | `completed` | `0` | 2 | 2 | 0 | 344 ms | [b_report_latest.md](b_report_latest.md) |

## 2. 模块健康度矩阵

| 模块 (`module`) | 单测通过率 | 基准核心吞吐 (`ops/sec`) | 未实现/待补项 (`Gaps`) | 综合评估 |
|---|---|---|---|---|
| `wordcount` | 3 / 3 (100.0%) | `630.7` (`BM-wordcount-001`) | 0 | `healthy` |
| `slugify` | 3 / 3 (100.0%) | `1563626` (`BM-slugify-001`) | 1 | `healthy`（`GAP-slugify-01` 停用词过滤待实现） |

## 3. 本次运行信息

- **运行批次**：`20261124_010147`（执行时间：`2026-11-24T01:01:47+08:00`，范围：`all`）
- **单测命令**：`python3 -B -m pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -vv --durations=0`
- **基准命令**：`python3 -B -m pytest tests/benchmark -o python_files="b_*_bench.py" -o cache_dir=tests/tmp/.pytest_cache -q -s`
- **状态文件**：`tests/.state/last_run.json`
