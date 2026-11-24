# `textutil` 模块单元测试规格 (`u_textutil_cases`)

> **module**: textutil ｜ **type**: unit_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 单元测试用例总表

| 用例 ID | 用例标题 | 关联功能点 | 场景类型 (`normal`/`boundary`/`exception`) | 目标源码符号 | 绑定测试函数 | 状态 |
|---|---|---|---|---|---|---|
| `UT-textutil-001` | 普通字符串按 rune 反转 | `FP-textutil-01` | `normal` | `textutil/textutil.go :: Reverse` | `TestUT_Textutil_001_ReversesRunes` | `active` |
| `UT-textutil-002` | 空字符串与多字节字符的反转 | `FP-textutil-01` | `boundary` | `textutil/textutil.go :: Reverse` | `TestUT_Textutil_002_ReversesEmptyAndUnicodeText` | `active` |
| `UT-textutil-003` | 回文与非回文输入的判断 | `FP-textutil-02` | `normal` | `textutil/textutil.go :: IsPalindrome` | `TestUT_Textutil_003_DetectsPalindromes` | `active` |

## 2. 用例规格详情

### UT-textutil-001: 普通字符串按 rune 反转

- **关联功能点**：`FP-textutil-01`（字符串反转）
- **目标符号**：`textutil/textutil.go :: Reverse(s string) string`
- **场景类型**：`normal`
- **前置条件与夹具**：读取 `tests/fixtures/textutil_fixtures.json` 的 `reverse_cases` 字段
- **输入参数（Given / When）**：When 对每个 `{input, expected}` 调用 `Reverse(input)`
- **预期结果与断言（Then）**：
  1. 返回值等于对应的 `expected`

### UT-textutil-002: 空字符串与多字节字符的反转

- **关联功能点**：`FP-textutil-01`（字符串反转）
- **目标符号**：`textutil/textutil.go :: Reverse(s string) string`
- **场景类型**：`boundary`
- **前置条件与夹具**：读取 `tests/fixtures/textutil_fixtures.json` 的 `boundary_cases` 字段（含空串与带重音字母的输入）
- **输入参数（Given / When）**：When 对每个边界 `{input, expected}` 调用 `Reverse(input)`
- **预期结果与断言（Then）**：
  1. 返回值等于对应的 `expected`，多字节字符不会被按字节拆散

### UT-textutil-003: 回文与非回文输入的判断

- **关联功能点**：`FP-textutil-02`（回文判断）
- **目标符号**：`textutil/textutil.go :: IsPalindrome(s string) bool`
- **场景类型**：`normal`
- **前置条件与夹具**：读取 `tests/fixtures/textutil_fixtures.json` 的 `palindromes` 与 `not_palindromes` 字段
- **输入参数（Given / When）**：When 分别对两组输入调用 `IsPalindrome(s)`
- **预期结果与断言（Then）**：
  1. `palindromes` 中的每一项返回 `true`
  2. `not_palindromes` 中的每一项返回 `false`
