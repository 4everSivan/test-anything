# `wordcount` 模块单元测试规格 (`u_wordcount_cases`)

> **module**: wordcount ｜ **type**: unit_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 单元测试用例总表

| 用例 ID | 用例标题 | 关联功能点 | 场景类型 (`normal`/`boundary`/`exception`) | 目标源码符号 | 绑定测试函数 | 状态 |
|---|---|---|---|---|---|---|
| `UT-wordcount-001` | 统计句子中的单词数 | `FP-wordcount-01` | `normal` | `textkit/wordcount.py :: count_words` | `test_ut_wordcount_001_counts_words_in_sentence` | `active` |
| `UT-wordcount-002` | 空白文本计为 0 | `FP-wordcount-01` | `boundary` | `textkit/wordcount.py :: count_words` | `test_ut_wordcount_002_counts_blank_text_as_zero` | `deprecated` |
| `UT-wordcount-003` | 负数 limit 抛出 ValueError | `FP-wordcount-02` | `exception` | `textkit/wordcount.py :: top_words` | `test_ut_wordcount_003_rejects_negative_limit` | `active` |

## 2. 用例规格详情

### UT-wordcount-001: 统计句子中的单词数

- **关联功能点**：`FP-wordcount-01`（单词计数）
- **目标符号**：`textkit/wordcount.py :: count_words(text: str) -> int`
- **场景类型**：`normal`
- **前置条件与夹具**：读取 `tests/fixtures/wordcount_fixtures.json` 的 `sentence` 与 `sentence_word_count` 字段
- **输入参数（Given / When）**：Given 句子含 9 个单词；When 调用 `count_words(sentence)`
- **预期结果与断言（Then）**：
  1. 返回值等于 `9`

### UT-wordcount-002: 空白文本计为 0

- **关联功能点**：`FP-wordcount-01`（单词计数）
- **目标符号**：`textkit/wordcount.py :: count_words(text: str) -> int`
- **场景类型**：`boundary`
- **前置条件与夹具**：读取 `tests/fixtures/wordcount_fixtures.json` 的 `blank_texts` 字段
- **输入参数（Given / When）**：Given 依次取空串与纯空白文本；When 调用 `count_words(text)`
- **预期结果与断言（Then）**：
  1. 每个输入的返回值都等于 `0`

### UT-wordcount-003: 负数 limit 抛出 ValueError

- **关联功能点**：`FP-wordcount-02`（词频排序）
- **目标符号**：`textkit/wordcount.py :: top_words(text: str, limit: int) -> list`
- **场景类型**：`exception`
- **前置条件与夹具**：读取 `tests/fixtures/wordcount_fixtures.json` 的 `negative_limit` 字段
- **输入参数（Given / When）**：Given `limit` 为负数；When 调用 `top_words(sentence, -1)`
- **预期结果与断言（Then）**：
  1. 抛出 `ValueError`
