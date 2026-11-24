# `wordcount` 模块性能基准规格 (`b_wordcount_cases`)

> **module**: wordcount ｜ **type**: benchmark_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 基准测试用例总表

| 用例 ID | 基准名称 | 关联功能点 | 目标源码符号 | 负载规模 | 核心采集指标 | 绑定基准函数 | 状态 |
|---|---|---|---|---|---|---|---|
| `BM-wordcount-001` | 万词语料上的词频排序 | `FP-wordcount-02` | `textkit/wordcount.py :: top_words` | 10,000 词 | `ops/sec` | `test_bm_wordcount_001_top_words_on_large_corpus` | `active` |

## 2. 基准规格详情

### BM-wordcount-001: 万词语料上的词频排序

- **关联功能点与热点说明**：`FP-wordcount-02`（词频排序）；词频统计需遍历全文并对结果排序，语料规模直接决定耗时，是该模块的主要性能热点。
- **目标符号**：`textkit/wordcount.py :: top_words(text: str, limit: int) -> list`
- **负载规模（Workload）**：由 `tests/fixtures/wordcount_fixtures.json` 的 `corpus_words` 与 `corpus_repeats` 拼出 10,000 词的语料
- **预热与迭代策略**：先执行 3 轮预热，再计时 20 轮取平均
- **采集指标与基线阈值**：`ops/sec`（每轮平均耗时的倒数）；单次耗时退化超过 15% 时在报告中标记关注
