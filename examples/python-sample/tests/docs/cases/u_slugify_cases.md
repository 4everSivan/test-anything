# `slugify` 模块单元测试规格 (`u_slugify_cases`)

> **module**: slugify ｜ **type**: unit_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 单元测试用例总表

| 用例 ID | 用例标题 | 关联功能点 | 场景类型 (`normal`/`boundary`/`exception`) | 目标源码符号 | 绑定测试函数 | 状态 |
|---|---|---|---|---|---|---|
| `UT-slugify-001` | 文本转换为小写 slug | `FP-slugify-01` | `normal` | `textkit/slugify.py :: slugify` | `test_ut_slugify_001_converts_text_to_lowercase_slug` | `active` |
| `UT-slugify-002` | 空文本与长度限制边界 | `FP-slugify-02` | `boundary` | `textkit/slugify.py :: slugify` | `test_ut_slugify_002_handles_empty_text_and_length_limit` | `active` |
| `UT-slugify-003` | 非正 max_len 抛出 ValueError | `FP-slugify-02` | `exception` | `textkit/slugify.py :: slugify` | `test_ut_slugify_003_rejects_non_positive_max_len` | `active` |
| `UT-slugify-004` | 忽略停用词后生成 slug | `FP-slugify-03` | `normal` | `textkit/slugify.py :: slugify(..., ignore_stopwords=True)` | —（能力未实现，不生成测试代码） | `todo` |
| `UT-slugify-005` | 标题首字母大写转换（能力已从源码移除） | `FP-slugify-01` | `normal` | `textkit/slugify.py :: title_case`（0.1 已移除） | —（`deprecated`，不生成测试代码） | `deprecated` |

## 2. 用例规格详情

### UT-slugify-001: 文本转换为小写 slug

- **关联功能点**：`FP-slugify-01`（slug 转换）
- **目标符号**：`textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str`
- **场景类型**：`normal`
- **前置条件与夹具**：读取 `tests/fixtures/slugify_fixtures.json` 的 `title` 与 `expected_slug` 字段
- **输入参数（Given / When）**：Given 混合大小写并含非 ASCII 字符与标点的标题；When 调用 `slugify(title)`
- **预期结果与断言（Then）**：
  1. 返回值等于 `expected_slug`，且只含小写字母、数字与连字符

### UT-slugify-002: 空文本与长度限制边界

- **关联功能点**：`FP-slugify-02`（slug 长度限制）
- **目标符号**：`textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str`
- **场景类型**：`boundary`
- **前置条件与夹具**：读取 `tests/fixtures/slugify_fixtures.json` 的 `max_len` 与 `expected_truncated_slug` 字段
- **输入参数（Given / When）**：When 分别调用 `slugify("")` 与 `slugify(title, max_len)`
- **预期结果与断言（Then）**：
  1. 空文本返回空串
  2. 截断结果等于 `expected_truncated_slug`，且不以连字符结尾

### UT-slugify-003: 非正 max_len 抛出 ValueError

- **关联功能点**：`FP-slugify-02`（slug 长度限制）
- **目标符号**：`textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str`
- **场景类型**：`exception`
- **前置条件与夹具**：读取 `tests/fixtures/slugify_fixtures.json` 的 `title` 与 `invalid_max_len` 字段
- **输入参数（Given / When）**：Given `max_len` 为 `0`；When 调用 `slugify(title, 0)`
- **预期结果与断言（Then）**：
  1. 抛出 `ValueError`

### UT-slugify-004: 忽略停用词后生成 slug

- **关联功能点**：`FP-slugify-03`（停用词过滤）
- **目标符号**：`textkit/slugify.py :: slugify(text, max_len=None, ignore_stopwords=False)`（源码尚未实现 `ignore_stopwords` 参数）
- **场景类型**：`normal`
- **前置条件与夹具**：待能力实现后在 `tests/fixtures/slugify_fixtures.json` 补充 `title_with_stopwords` 与 `expected_slug_without_stopwords` 字段
- **输入参数（Given / When）**：Given `ignore_stopwords=True`；When 调用 `slugify(title_with_stopwords, ignore_stopwords=True)`
- **预期结果与断言（Then）**：
  1. 返回值中不含停用词 `the`、`of`

### UT-slugify-005: 标题首字母大写转换（能力已从源码移除）

- **关联功能点**：`FP-slugify-01`（slug 转换）；该用例源自早期版本提供的标题大小写转换能力，0.1 起该能力已从源码移除
- **目标符号**：`textkit/slugify.py :: title_case`（源码中已不存在）
- **场景类型**：`normal`
- **前置条件与夹具**：无；能力已移除，不再需要夹具
- **输入参数（Given / When）**：不再执行
- **预期结果与断言（Then）**：
  1. 不生成测试代码；保留本条规格用于追溯历史用例编号
