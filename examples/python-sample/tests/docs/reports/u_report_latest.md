# 单元测试执行报告 (`u_report`)

> **module**: global ｜ **type**: unit_report ｜ **run_id**: 20261124_102731 ｜ **updated_at**: 2026-11-24 ｜ **status**: passed

## 1. 执行概览

- **执行命令**：`python3 -B -m coverage run --branch --source=textkit --data-file=tests/tmp/coverage/.coverage -m pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -vv --durations=0`
- **退出码（Exit Code）**：`0`
- **执行时间**：`2026-11-24T10:27:31+08:00`（总耗时：`642 ms`，为命令墙钟耗时，含解释器启动、用例收集与覆盖率采集；pytest 自报会话耗时 `0.04s`）

| 总用例数 | 通过 (Passed) | 失败 (Failed) | 跳过 (Skipped) | 通过率 | 行覆盖率 | 分支覆盖率 |
|---|---|---|---|---|---|---|
| 6 | 6 | 0 | 0 | 100.0% | 76.92% | 60% |

- **覆盖率来源**：在本次单测运行中由 `coverage.py` 以 `--branch` 采集，没有为覆盖率额外再跑一遍测试；`--source=textkit` 使统计只含业务源码，不含 `tests/` 自身。运行后以 `python3 -B -m coverage json --data-file=tests/tmp/coverage/.coverage -o tests/tmp/coverage/coverage.json` 导出，再由 `scripts/ta-verify --coverage` 解析后写入 `tests/.state/last_run.json` 的 `unit.coverage`。
- **逐模块覆盖率**：`slugify` 行 100% / 分支 100%；`textkit`（包的 `__init__.py`）行 100% / 分支 N/A（该文件没有分支）；`wordcount` 行 57.14% / 分支 33.33%。

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

## 4. 未覆盖符号

下表由 `tests/.state/last_run.json` 中 `unit.coverage.uncovered[]` 逐条渲染，共 6 条，全部位于 `wordcount` 模块；未触及每模块 50 条的上限，没有被省略的条目。

| 模块 | 源码文件 | 符号 | 类型 | 未覆盖行 |
|---|---|---|---|---|
| `wordcount` | `textkit/wordcount.py` | `count_words` | 未覆盖分支 | `10->11` |
| `wordcount` | `textkit/wordcount.py` | `count_words` | 未覆盖行 | `11` |
| `wordcount` | `textkit/wordcount.py` | `top_words` | 未覆盖分支 | `20->22` |
| `wordcount` | `textkit/wordcount.py` | `top_words` | 未覆盖行 | `22-26` |
| `wordcount` | `textkit/wordcount.py` | `top_words` | 未覆盖分支 | `23->24` |
| `wordcount` | `textkit/wordcount.py` | `top_words` | 未覆盖分支 | `23->25` |

“未覆盖行”一列中，单个数字或区间表示从未执行的语句行，`起->止` 表示从未走到的分支跳转。`count_words` 第 11 行是非字符串入参时抛出 `TypeError` 的分支，现有单测没有覆盖该异常场景；`top_words` 的第 22–26 行是词频统计与排序的主体，现有单测只验证了 `limit` 为负数时的异常分支，正常路径仅由基准测试 `BM-wordcount-001` 执行，而基准测试不计入覆盖率。
