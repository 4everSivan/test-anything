# <ProjectName> 测试文档中心 (tests/docs/)

> **module**: global ｜ **type**: index ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 测试体系概览与快速入口

- **受管技能版本**：`test-anything v0.1.0`
- **技术栈与运行器**：`<language_and_framework>`
- **标准执行命令**：
  - 查看帮助：`$test-anything help`（或 `--help` / `-h`）
  - 生成/更新用例：`$test-anything create`（或裸调 `$test-anything`）
  - 全量测试：`$test-anything run`
  - 单元测试：`$test-anything run unittest`
  - 基准测试：`$test-anything run benchmark`

## 2. 模块测试资产矩阵

| 模块 (`module`) | 功能点草稿 (`drafts/`) | 测试计划 (`plans/`) | 单测规格 (`cases/u_*`) | 基准规格 (`cases/b_*`) | 单测数 / 基准数 | 最新运行状态 |
|---|---|---|---|---|---|---|
| `<module>` | [<module>_draft.md](drafts/<module>_draft.md) | [<module>_plan.md](plans/<module>_plan.md) | [u_<module>_cases.md](cases/u_<module>_cases.md) | [b_<module>_cases.md](cases/b_<module>_cases.md) | 0 / 0 | not_run |

## 3. 全局计划与最新报告导航

- **全局测试总计划**：[plans/test_plan.md](plans/test_plan.md)
- **最新全量汇总报告**：[reports/all_report_latest.md](reports/all_report_latest.md)
- **最新单元测试报告**：[reports/u_report_latest.md](reports/u_report_latest.md)
- **最新基准测试报告**：[reports/b_report_latest.md](reports/b_report_latest.md)
