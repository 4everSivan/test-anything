# `<module>` 模块单元测试规格 (`u_<module>_cases`)

> **module**: <module> ｜ **type**: unit_cases ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 单元测试用例总表

| 用例 ID | 用例标题 | 关联功能点 | 场景类型 (`normal`/`boundary`/`exception`) | 目标源码符号 | 绑定测试函数 | 状态 |
|---|---|---|---|---|---|---|
| `UT-<module>-001` | `<case_title>` | `FP-<module>-01` | `normal` | `<src_file> :: <func_name>` | `<test_func_name>` | `active` |

## 2. 用例规格详情

### UT-<module>-001: <case_title>

- **关联功能点**：`FP-<module>-01`（`<feature_name>`）
- **目标符号**：`<src_file> :: <full_signature>`
- **场景类型**：`normal`
- **前置条件与夹具**：`<preconditions_and_fixtures>`
- **输入参数（Given / When）**：`<input_parameters>`
- **预期结果与断言（Then）**：
  1. `<assertion_1>`
  2. `<assertion_2>`
