# `wordcount` 模块测试计划

> **module**: wordcount ｜ **type**: module_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵

| 功能点 ID | 用例 ID | 类型 (`u_`/`b_`) | 场景/负载分类 | 目标源码文件与函数签名 | 对应测试代码位置 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|
| `FP-wordcount-01` | `UT-wordcount-001` | `u_` | `normal` | `textkit/wordcount.py :: count_words(text: str) -> int` | `tests/unit/u_wordcount_test.py :: test_ut_wordcount_001_counts_words_in_sentence` | P0 | `active` |
| `FP-wordcount-01` | `UT-wordcount-002` | `u_` | `boundary` | `textkit/wordcount.py :: count_words(text: str) -> int` | —（`deprecated`，不生成测试代码） | P0 | `deprecated` |
| `FP-wordcount-02` | `UT-wordcount-003` | `u_` | `exception` | `textkit/wordcount.py :: top_words(text: str, limit: int) -> list` | `tests/unit/u_wordcount_test.py :: test_ut_wordcount_003_rejects_negative_limit` | P1 | `active` |
| `FP-wordcount-02` | `BM-wordcount-001` | `b_` | `hotspot` | `textkit/wordcount.py :: top_words(text: str, limit: int) -> list` | `tests/benchmark/b_wordcount_bench.py :: test_bm_wordcount_001_top_words_on_large_corpus` | P1 | `active` |

## 2. 模块夹具与 Mock 策略

- **数据夹具**：`tests/fixtures/wordcount_fixtures.json`
- **Mock 边界**：本模块为纯函数，无外部依赖，无需 Mock。
