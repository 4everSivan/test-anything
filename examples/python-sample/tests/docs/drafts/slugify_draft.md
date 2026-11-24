# `slugify` 模块功能点与测试草稿

> **module**: slugify ｜ **type**: draft ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 来源与模块边界

- **源文档路径**：`README.md`（Functional points 第 3、4、5 条）
- **目标源码路径**：`textkit/slugify.py`
- **存量测试备份**：无
- **模块职责边界**：负责把自由文本转换为 URL 友好的小写 ASCII slug，并可限制长度；纯函数，无 I/O 与外部依赖。

## 2. 功能点拆解清单 (Functional Points)

| 功能点 ID | 功能名称 | 触发与输入约束 | 预期行为与输出 | 边界与异常规则 | 来源定位 |
|---|---|---|---|---|---|
| `FP-slugify-01` | slug 转换 | 入参 `text` 为字符串 | 返回小写 ASCII slug：非字母数字的连续字符折叠为单个连字符 | 空文本返回空串；首尾不留连字符 | `README.md` Functional points 第 3 条 |
| `FP-slugify-02` | slug 长度限制 | 可选入参 `max_len` 为正整数 | slug 截断到 `max_len` 个字符 | `max_len` 小于 `1` 抛出 `ValueError`；截断后末尾不留连字符 | `README.md` Functional points 第 4 条 |
| `FP-slugify-03` | 停用词过滤 | 可选入参 `ignore_stopwords` 为布尔值 | 为 `True` 时从 slug 中去掉英文停用词 | 文档已声明，源码尚未实现该参数 | `README.md` Functional points 第 5 条 |

## 3. 候选测试点分流

### 3.1 单元测试候选 (`u_`)

| 候选编号 | 关联功能点 | 场景维度 (`normal`/`boundary`/`exception`) | 候选测试描述 | 来源类型 |
|---|---|---|---|---|
| `CAND-U-01` | `FP-slugify-01` | `normal` | 混合大小写与非 ASCII 文本转换为小写 slug | `docs` |
| `CAND-U-02` | `FP-slugify-02` | `boundary` | 空文本返回空串；截断后末尾不留连字符 | `docs` |
| `CAND-U-03` | `FP-slugify-02` | `exception` | `max_len` 为 `0` 时抛出 `ValueError` | `docs` |
| `CAND-U-04` | `FP-slugify-03` | `normal` | `ignore_stopwords=True` 时去掉停用词（待实现） | `docs` |

### 3.2 性能基准候选 (`b_`)

| 候选编号 | 关联功能点 | 性能热点原因 | 计划负载规模 | 关注指标 |
|---|---|---|---|---|
| `CAND-B-01` | `FP-slugify-01` | 正则替换与大小写转换需扫描全文，批量处理标题时构成热点 | 10,000 条标题 | `ops/sec` |

## 4. 待确认与实现差异 (Gaps)

| 差异编号 | 涉及功能点 | 差异类型 (`unimplemented`/`conflict`/`missing_data`) | 详细说明与处置方式 |
|---|---|---|---|
| `GAP-slugify-01` | `FP-slugify-03` | `unimplemented` | `README.md` 声明了 `ignore_stopwords` 参数，但 `textkit/slugify.py` 的 `slugify()` 尚无该参数；对应规格标记 `todo`，不生成测试代码，待源码实现后补测。 |
