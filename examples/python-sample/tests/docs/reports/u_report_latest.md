# 单元测试执行报告 (`u_report`)

> **module**: global ｜ **type**: unit_report ｜ **run_id**: 20261124_010147 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 执行概览

- **执行命令**：`python3 -B -m pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -vv --durations=0`
- **退出码（Exit Code）**：`0`
- **执行时间**：`2026-11-24T01:01:47+08:00`（总耗时：`263 ms`，为命令墙钟耗时，含解释器启动与用例收集；pytest 自报会话耗时 `0.02s`）

| 总用例数 | 通过 (Passed) | 失败 (Failed) | 跳过 (Skipped) | 通过率 |
|---|---|---|---|---|
| 6 | 6 | 0 | 0 | 100.0% |

## 2. 模块与用例执行明细

| 用例 ID | 所属模块 | 场景类型 | 绑定测试函数 | 状态 | 耗时 (ms) |
|---|---|---|---|---|---|
| `UT-slugify-001` | `slugify` | `normal` | `test_ut_slugify_001_converts_text_to_lowercase_slug` | PASS | `<5` |
| `UT-slugify-002` | `slugify` | `boundary` | `test_ut_slugify_002_handles_empty_text_and_length_limit` | PASS | `<5` |
| `UT-slugify-003` | `slugify` | `exception` | `test_ut_slugify_003_rejects_non_positive_max_len` | PASS | `<5` |
| `UT-wordcount-001` | `wordcount` | `normal` | `test_ut_wordcount_001_counts_words_in_sentence` | PASS | `<5` |
| `UT-wordcount-002` | `wordcount` | `boundary` | `test_ut_wordcount_002_counts_blank_text_as_zero` | PASS | `<5` |
| `UT-wordcount-003` | `wordcount` | `exception` | `test_ut_wordcount_003_rejects_negative_limit` | PASS | `<5` |

逐条用例耗时低于 pytest `--durations=0` 的输出精度（运行器原样输出为 `0.00s`），故记为 `<5` ms，不以模板占位 `0` 充数。`UT-slugify-004` 对应能力尚未实现（规格状态 `todo`），未生成测试代码，不在本次执行范围内。

## 3. 失败与异常诊断

本次运行全部通过，无失败用例。
