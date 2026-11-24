# 负向样例 (examples/negative/)

> **created**: 2026-11-24 ｜ **last-change**: 2026-11-24 ｜ **status**: active

本目录下的每个子目录都是一个**故意违规**的最小目标工程，用于断言 [`scripts/ta-verify`](../../scripts/ta-verify) 确实会拦住对应的错误。它们都从同一份基底派生（`wordcount` 模块的 create 产物），彼此只差一处注入的违规。

## 1. 样例清单

| 目录 | 注入的违规 | 预期退出码 | 预期诊断码 |
|---|---|---|---|
| [`missing-case-anchor/`](missing-case-anchor/) | 测试函数缺少 `@case` / `@feature` 锚点注释 | `4` | `CODE_FUNCTION_WITHOUT_ANCHOR` |
| [`manifest-field-missing/`](manifest-field-missing/) | `manifest.json` 缺少协议必填字段 `stack` | `4` | `MANIFEST_FIELD_MISSING` |
| [`manifest-structure-invalid/`](manifest-structure-invalid/) | `manifest.json` 模块条目结构非法（`unit_code` 写成了字符串） | `4` | `MANIFEST_MODULE_INVALID` |
| [`wrong-track-prefix/`](wrong-track-prefix/) | `cases/` 下出现缺少 `u_` / `b_` 前缀的文件 | `4` | `DOC_TRACK_PREFIX_INVALID` |
| [`orphan-case/`](orphan-case/) | 孤立用例：规格仍在，对应的测试函数被删除 | `4` | `CASE_WITHOUT_TEST_CODE` |
| [`deprecated-case-with-code/`](deprecated-case-with-code/) | `deprecated` 用例仍绑定着测试函数（能力已移除却还生成代码） | `4` | `CASE_DEPRECATED_WITH_CODE` |
| [`hash-mismatch/`](hash-mismatch/) | **警告样例**：受管测试文件被人工修改，manifest 中的 SHA-256 未更新 | `0` | `MANIFEST_HASH_MISMATCH`（`WARNING`） |

## 2. `expected.json` 的含义

每个样例根目录下的 `expected.json` 是该样例的断言依据：

```json
{
  "description": "注入的违规说明",
  "scope": "create",
  "exit_code": 4,
  "codes": ["CASE_WITHOUT_TEST_CODE"]
}
```

- `scope`：运行 `ta-verify` 时使用的范围；
- `exit_code`：必须取得的退出码；
- `codes`：`exit_code` 为 `4` 时，是**恰好**应当出现的全部 `ERROR` 级诊断码；为 `0` 时，是恰好应当出现的全部 `WARNING` 级诊断码，且不得出现任何 `ERROR`。

`ADVISORY` 级提示不参与断言：这些最小工程不含 `reports/` 与 `tests/tmp/`，`ta-verify` 会如实给出 `DOCS_REPORTS_DIR_MISSING` 与 `TESTS_OPTIONAL_DIR_MISSING` 两条提示，它们不影响退出码。

## 3. 单一违规的隔离方式

为了让每个样例“只对应一个预期诊断码”，构造时遵守两条约定：

1. **不引入连带违规**：凡是修改了受管测试文件的样例（`missing-case-anchor`、`orphan-case`），都同步更新了 manifest 中该文件的 SHA-256，因此不会额外触发 `MANIFEST_HASH_MISMATCH`；只有 `hash-mismatch` 样例是有意保留哈希不符。
2. **避开会级联的变异**：例如把 `u_<module>_cases.md` 直接改名，会让该模块的用例全部失去规格，连带触发锚点、manifest 等多处错误；`wrong-track-prefix` 因此采用“额外多出一个无前缀文件”的形式，只保留命名违规本身。

新增负向样例时请沿用这两条约定，并同步更新上表。

## 4. 核对方式

```bash
# 单个样例：应 Exit 4 并列出违规明细
scripts/ta-verify --target examples/negative/orphan-case --scope create

# 全部样例：由契约测试逐个断言 expected.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p "test_samples.py" -v
```

这些样例只用于校验器回归，不是可运行的工程：目录里没有业务源码，请不要对其执行 `create` 或 `run`，也不要“修复”它们——违规正是它们存在的意义。
