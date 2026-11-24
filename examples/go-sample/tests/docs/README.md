# gosample 测试文档中心 (tests/docs/)

> **module**: global ｜ **type**: index ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 测试体系概览与快速入口

- **受管技能版本**：`test-anything v0.1.0`
- **技术栈与运行器**：`Go 1.21+ / go test`
- **标准执行命令**：
  - 查看帮助：`$test-anything help`（或 `--help` / `-h`）
  - 生成/更新用例：`$test-anything create`（或裸调 `$test-anything`）
  - 全量测试：`$test-anything run`
  - 单元测试：`$test-anything run unittest`
  - 基准测试：`$test-anything run benchmark`

## 2. 模块测试资产矩阵

| 模块 (`module`) | 功能点草稿 (`drafts/`) | 测试计划 (`plans/`) | 单测规格 (`cases/u_*`) | 基准规格 (`cases/b_*`) | 单测数 / 基准数 | 最新运行状态 |
|---|---|---|---|---|---|---|
| `calc` | [calc_draft.md](drafts/calc_draft.md) | [calc_plan.md](plans/calc_plan.md) | [u_calc_cases.md](cases/u_calc_cases.md) | [b_calc_cases.md](cases/b_calc_cases.md) | 3 / 1 | passed / completed |
| `textutil` | [textutil_draft.md](drafts/textutil_draft.md) | [textutil_plan.md](plans/textutil_plan.md) | [u_textutil_cases.md](cases/u_textutil_cases.md) | [b_textutil_cases.md](cases/b_textutil_cases.md) | 3 / 1 | passed / completed |

## 3. 全局计划与最新报告导航

- **全局测试总计划**：[plans/test_plan.md](plans/test_plan.md)
- **最新全量汇总报告**：[reports/all_report_latest.md](reports/all_report_latest.md)
- **最新单元测试报告**：[reports/u_report_latest.md](reports/u_report_latest.md)
- **最新基准测试报告**：[reports/b_report_latest.md](reports/b_report_latest.md)
