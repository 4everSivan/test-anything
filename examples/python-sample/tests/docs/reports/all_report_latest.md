# 全量测试综合报告 (`all_report`)

> **module**: global ｜ **type**: all_report ｜ **run_id**: 20261124_102731 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 双轨执行总览

| 测试轨道 | 运行状态 | 退出码 | 用例总数 | 通过 / 完成 | 失败 / 退化 | 耗时 | 详细报告 |
|---|---|---|---|---|---|---|---|
| 单元测试 (`unittest`) | `passed` | `0` | 6 | 6 | 0 | 642 ms | [u_report_latest.md](u_report_latest.md) |
| 基准测试 (`benchmark`) | `completed` | `0` | 2 | 2 | 0 | 512 ms | [b_report_latest.md](b_report_latest.md) |

## 2. 模块健康度矩阵

“行覆盖率”取自 `tests/.state/last_run.json` 的 `unit.coverage.modules`，是本次单测运行中采集的行覆盖率；全工程行覆盖率 76.92%、分支覆盖率 60%。

| 模块 (`module`) | 单测通过率 | 基准核心吞吐 (`ops/sec`) | 行覆盖率 | 未实现/待补项 (`Gaps`) | 综合评估 |
|---|---|---|---|---|---|
| `wordcount` | 3 / 3 (100.0%) | `481.5` (`BM-wordcount-001`) | 57.14% | 0 | `healthy`；`top_words` 正常路径未被单测覆盖，见单元测试报告第 4 节 |
| `slugify` | 3 / 3 (100.0%) | `1364755` (`BM-slugify-001`) | 100% | 1 | `healthy`（`GAP-slugify-01` 停用词过滤待实现） |

覆盖率只用于呈现，不参与健康度判定，也没有阈值。

## 3. 本次运行信息

- **运行批次**：`20261124_102731`（执行时间：`2026-11-24T10:27:31+08:00`，范围：`all`）
- **单测命令**：`python3 -B -m coverage run --branch --source=textkit --data-file=tests/tmp/coverage/.coverage -m pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -vv --durations=0`
- **基准命令**：`python3 -B -m pytest tests/benchmark -o python_files="b_*_bench.py" -o cache_dir=tests/tmp/.pytest_cache -q -s`
- **状态文件**：`tests/.state/last_run.json`
