# 全局测试总计划 (Test Plan)

> **module**: global ｜ **type**: test_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 目标技术栈与执行环境

- **主语言与框架**：`Python 3.8+ / pytest 8`（以 `python3 -m pytest` 方式从工程根目录启动，保证 `textkit` 可被导入）
- **单元测试运行命令**：`python3 -B -m pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -vv --durations=0`
- **基准测试运行命令**：`python3 -B -m pytest tests/benchmark -o python_files="b_*_bench.py" -o cache_dir=tests/tmp/.pytest_cache -q -s`
- **运行期临时目录**：`tests/tmp/`（所有临时文件、缓存与覆盖率原始数据强制落盘于此；`-B` 禁止写入 `__pycache__`）

## 2. 模块测试覆盖总表

| 模块 (`module`) | 模块计划 | 单测规格 (`u_`) | 基准规格 (`b_`) | 单测代码 (`unit/`) | 基准代码 (`benchmark/`) | 公共夹具 (`fixtures/`) |
|---|---|---|---|---|---|---|
| `wordcount` | [wordcount_plan.md](wordcount_plan.md) | [u_wordcount_cases.md](../cases/u_wordcount_cases.md) | [b_wordcount_cases.md](../cases/b_wordcount_cases.md) | `tests/unit/u_wordcount_test.py` | `tests/benchmark/b_wordcount_bench.py` | `tests/fixtures/wordcount_fixtures.json` |

## 3. 全局夹具与隔离策略

- 外部网络、第三方服务与非受控 I/O 一律通过 `tests/fixtures/` 隔离（本工程为纯函数，实际无外部依赖）。
- 运行期产生的所有临时文件与本地沙箱数据统一输出至 `tests/tmp/`。
