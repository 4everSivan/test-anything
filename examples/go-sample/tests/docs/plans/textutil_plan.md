# `textutil` 模块测试计划

> **module**: textutil ｜ **type**: module_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵

| 功能点 ID | 用例 ID | 类型 (`u_`/`b_`) | 场景/负载分类 | 目标源码文件与函数签名 | 对应测试代码位置 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|
| `FP-textutil-01` | `UT-textutil-001` | `u_` | `normal` | `textutil/textutil.go :: Reverse(s string) string` | `tests/unit/u_textutil_test.go :: TestUT_Textutil_001_ReversesRunes` | P0 | `active` |
| `FP-textutil-01` | `UT-textutil-002` | `u_` | `boundary` | `textutil/textutil.go :: Reverse(s string) string` | `tests/unit/u_textutil_test.go :: TestUT_Textutil_002_ReversesEmptyAndUnicodeText` | P0 | `active` |
| `FP-textutil-02` | `UT-textutil-003` | `u_` | `normal` | `textutil/textutil.go :: IsPalindrome(s string) bool` | `tests/unit/u_textutil_test.go :: TestUT_Textutil_003_DetectsPalindromes` | P1 | `active` |
| `FP-textutil-01` | `BM-textutil-001` | `b_` | `hotspot` | `textutil/textutil.go :: Reverse(s string) string` | `tests/benchmark/b_textutil_bench_test.go :: BenchmarkBM_Textutil_001_ReverseLongString` | P1 | `active` |

## 2. 模块夹具与 Mock 策略

- **数据夹具**：`tests/fixtures/textutil_fixtures.json`（Go 测试的工作目录是所在包目录，测试代码以 `../fixtures/` 相对路径读取）
- **Mock 边界**：本模块为纯函数，无外部依赖，无需 Mock。
