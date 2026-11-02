# 全局测试总计划 (Test Plan)

> **module**: global ｜ **type**: test_plan ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 目标技术栈与执行环境

- **主语言与框架**：`<language_and_framework>`
- **单元测试运行命令**：`<unit_runner_command>`
- **基准测试运行命令**：`<benchmark_runner_command>`
- **运行期临时目录**：`tests/tmp/`（所有临时文件、缓存与覆盖率原始数据强制落盘于此）

## 2. 模块测试覆盖总表

| 模块 (`module`) | 模块计划 | 单测规格 (`u_`) | 基准规格 (`b_`) | 单测代码 (`unit/`) | 基准代码 (`benchmark/`) | 公共夹具 (`fixtures/`) |
|---|---|---|---|---|---|---|
| `<module>` | [<module>_plan.md](<module>_plan.md) | [u_<module>_cases.md](../cases/u_<module>_cases.md) | [b_<module>_cases.md](../cases/b_<module>_cases.md) | `tests/unit/u_<module>_test.<ext>` | `tests/benchmark/b_<module>_bench.<ext>` | `tests/fixtures/<module>_fixtures.json` |

## 3. 全局夹具与隔离策略

- 外部网络、第三方服务与非受控 I/O 一律通过 `tests/fixtures/` 隔离。
- 运行期产生的所有临时文件与本地沙箱数据统一输出至 `tests/tmp/`。
