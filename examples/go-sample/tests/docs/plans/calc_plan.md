# `calc` 模块测试计划

> **module**: calc ｜ **type**: module_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵

| 功能点 ID | 用例 ID | 类型 (`u_`/`b_`) | 场景/负载分类 | 目标源码文件与函数签名 | 对应测试代码位置 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|
| `FP-calc-01` | `UT-calc-001` | `u_` | `normal` | `calc/calc.go :: Add(a, b int) int` | `tests/unit/u_calc_test.go :: TestUT_Calc_001_AddPositiveIntegers` | P0 | `active` |
| `FP-calc-02` | `UT-calc-002` | `u_` | `exception` | `calc/calc.go :: Div(a, b int) (int, error)` | `tests/unit/u_calc_test.go :: TestUT_Calc_002_DivideByZeroReturnsError` | P0 | `active` |
| `FP-calc-02` | `UT-calc-003` | `u_` | `boundary` | `calc/calc.go :: Div(a, b int) (int, error)` | `tests/unit/u_calc_test.go :: TestUT_Calc_003_DivideTruncatesTowardZero` | P1 | `active` |
| `FP-calc-01` | `BM-calc-001` | `b_` | `hotspot` | `calc/calc.go :: Add(a, b int) int` | `tests/benchmark/b_calc_bench_test.go :: BenchmarkBM_Calc_001_AddLoop` | P1 | `active` |

## 2. 模块夹具与 Mock 策略

- **数据夹具**：`tests/fixtures/calc_fixtures.json`（Go 测试的工作目录是所在包目录，测试代码以 `../fixtures/` 相对路径读取）
- **Mock 边界**：本模块为纯函数，无外部依赖，无需 Mock。
