# `slugify` 模块测试计划

> **module**: slugify ｜ **type**: module_plan ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵

| 功能点 ID | 用例 ID | 类型 (`u_`/`b_`) | 场景/负载分类 | 目标源码文件与函数签名 | 对应测试代码位置 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|
| `FP-slugify-01` | `UT-slugify-001` | `u_` | `normal` | `textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str` | `tests/unit/u_slugify_test.py :: test_ut_slugify_001_converts_text_to_lowercase_slug` | P0 | `active` |
| `FP-slugify-02` | `UT-slugify-002` | `u_` | `boundary` | `textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str` | `tests/unit/u_slugify_test.py :: test_ut_slugify_002_handles_empty_text_and_length_limit` | P0 | `active` |
| `FP-slugify-02` | `UT-slugify-003` | `u_` | `exception` | `textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str` | `tests/unit/u_slugify_test.py :: test_ut_slugify_003_rejects_non_positive_max_len` | P1 | `active` |
| `FP-slugify-03` | `UT-slugify-004` | `u_` | `normal` | `textkit/slugify.py :: slugify(text, max_len=None, ignore_stopwords=False)`（源码尚未实现 `ignore_stopwords`） | 待能力实现后生成 | P2 | `todo` |
| `FP-slugify-01` | `BM-slugify-001` | `b_` | `hotspot` | `textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str` | `tests/benchmark/b_slugify_bench.py :: test_bm_slugify_001_slugify_title_batch` | P1 | `active` |

## 2. 模块夹具与 Mock 策略

- **数据夹具**：`tests/fixtures/slugify_fixtures.json`
- **Mock 边界**：本模块为纯函数，无外部依赖，无需 Mock。
