# `wordcount` 模块功能点与测试草稿

> **module**: wordcount ｜ **type**: draft ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 来源与模块边界

- **源文档路径**：`README.md`（Functional points 第 1、2 条）
- **目标源码路径**：`textkit/wordcount.py`
- **存量测试备份**：无
- **模块职责边界**：负责英文文本的单词计数与词频排序，均为纯函数；不含分词之外的 NLP 能力，无外部依赖。

## 2. 功能点拆解清单 (Functional Points)

| 功能点 ID | 功能名称 | 触发与输入约束 | 预期行为与输出 | 边界与异常规则 | 来源定位 |
|---|---|---|---|---|---|
| `FP-wordcount-01` | 单词计数 | 入参 `text` 为字符串 | 返回其中的单词数量（`int`） | 空串与纯空白文本返回 `0`；非字符串入参抛出 `TypeError` | `README.md` Functional points 第 1 条 |
| `FP-wordcount-02` | 词频排序 | 入参 `text` 为字符串，`limit` 为非负整数 | 返回至多 `limit` 个 `(word, count)`，按出现次数降序、同次数按字母序 | `limit` 为负抛出 `ValueError`；`limit` 为 `0` 返回空列表 | `README.md` Functional points 第 2 条 |

## 3. 候选测试点分流

### 3.1 单元测试候选 (`u_`)

| 候选编号 | 关联功能点 | 场景维度 (`normal`/`boundary`/`exception`) | 候选测试描述 | 来源类型 |
|---|---|---|---|---|
| `CAND-U-01` | `FP-wordcount-01` | `normal` | 统计句子中的单词数 | `docs` |
| `CAND-U-02` | `FP-wordcount-01` | `boundary` | 空串与纯空白文本计为 `0` | `docs` |
| `CAND-U-03` | `FP-wordcount-02` | `exception` | `limit` 为负数时抛出 `ValueError` | `docs` |

### 3.2 性能基准候选 (`b_`)

| 候选编号 | 关联功能点 | 性能热点原因 | 计划负载规模 | 关注指标 |
|---|---|---|---|---|
| `CAND-B-01` | `FP-wordcount-02` | 词频统计需遍历全文并对结果排序，语料越大越耗时 | 10,000 词 | `ops/sec` |

## 4. 待确认与实现差异 (Gaps)

| 差异编号 | 涉及功能点 | 差异类型 (`unimplemented`/`conflict`/`missing_data`) | 详细说明与处置方式 |
|---|---|---|---|
| — | — | — | 暂无：文档描述的两个功能点与源码签名一致。 |
