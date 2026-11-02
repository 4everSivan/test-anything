# `<module>` 模块测试计划

> **module**: <module> ｜ **type**: module_plan ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵

| 功能点 ID | 用例 ID | 类型 (`u_`/`b_`) | 场景/负载分类 | 目标源码文件与函数签名 | 对应测试代码位置 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|
| `FP-<module>-01` | `UT-<module>-001` | `u_` | `normal` | `<src_file> :: <func_signature>` | `tests/unit/u_<module>_test.<ext> :: <test_func>` | P0 | `active` |
| `FP-<module>-01` | `BM-<module>-001` | `b_` | `hotspot` | `<src_file> :: <func_signature>` | `tests/benchmark/b_<module>_bench.<ext> :: <bench_func>` | P1 | `active` |

## 2. 模块夹具与 Mock 策略

- **数据夹具**：`tests/fixtures/<module>_fixtures.json`
- **Mock 边界**：说明本模块需要 Mock 的外部依赖或存储接口。
