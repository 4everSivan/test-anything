# `calc` 模块单元测试规格 (`u_calc_cases`)

> **module**: calc ｜ **type**: unit_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 单元测试用例总表

| 用例 ID | 用例标题 | 关联功能点 | 场景类型 (`normal`/`boundary`/`exception`) | 目标源码符号 | 绑定测试函数 | 状态 |
|---|---|---|---|---|---|---|
| `UT-calc-001` | 两个正整数相加 | `FP-calc-01` | `normal` | `calc/calc.go :: Add` | `TestUT_Calc_001_AddPositiveIntegers` | `active` |
| `UT-calc-002` | 除数为 0 时返回 error | `FP-calc-02` | `exception` | `calc/calc.go :: Div` | `TestUT_Calc_002_DivideByZeroReturnsError` | `active` |
| `UT-calc-003` | 负数被除数向零截断 | `FP-calc-02` | `boundary` | `calc/calc.go :: Div` | `TestUT_Calc_003_DivideTruncatesTowardZero` | `active` |

## 2. 用例规格详情

### UT-calc-001: 两个正整数相加

- **关联功能点**：`FP-calc-01`（整数加法）
- **目标符号**：`calc/calc.go :: Add(a, b int) int`
- **场景类型**：`normal`
- **前置条件与夹具**：读取 `tests/fixtures/calc_fixtures.json` 的 `add` 字段
- **输入参数（Given / When）**：Given `a=2`、`b=3`；When 调用 `Add(a, b)`
- **预期结果与断言（Then）**：
  1. 返回值等于 `5`

### UT-calc-002: 除数为 0 时返回 error

- **关联功能点**：`FP-calc-02`（整数除法）
- **目标符号**：`calc/calc.go :: Div(a, b int) (int, error)`
- **场景类型**：`exception`
- **前置条件与夹具**：读取 `tests/fixtures/calc_fixtures.json` 的 `divide.dividend` 与 `zero_divisor` 字段
- **输入参数（Given / When）**：Given 除数为 `0`；When 调用 `Div(-7, 0)`
- **预期结果与断言（Then）**：
  1. 返回非 `nil` 的 error，且不发生 panic

### UT-calc-003: 负数被除数向零截断

- **关联功能点**：`FP-calc-02`（整数除法）
- **目标符号**：`calc/calc.go :: Div(a, b int) (int, error)`
- **场景类型**：`boundary`
- **前置条件与夹具**：读取 `tests/fixtures/calc_fixtures.json` 的 `divide` 字段
- **输入参数（Given / When）**：When 调用 `Div(-7, 2)`
- **预期结果与断言（Then）**：
  1. 返回 `(-3, nil)`，即商向零截断而非向下取整
