# `<module>` 模块功能点与测试草稿

> **module**: <module> ｜ **type**: draft ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 来源与模块边界

- **源文档路径**：`<doc_paths>`
- **目标源码路径**：`<source_paths>`
- **存量测试备份**：`<legacy_test_backup_paths_or_none>`
- **模块职责边界**：说明本模块的核心职责、对外接口与依赖边界。

## 2. 功能点拆解清单 (Functional Points)

| 功能点 ID | 功能名称 | 触发与输入约束 | 预期行为与输出 | 边界与异常规则 | 来源定位 |
|---|---|---|---|---|---|
| `FP-<module>-01` | `<feature_name>` | `<input_constraints>` | `<expected_output>` | `<boundary_and_errors>` | `<doc_section_and_source_line>` |

## 3. 候选测试点分流

### 3.1 单元测试候选 (`u_`)

| 候选编号 | 关联功能点 | 场景维度 (`normal`/`boundary`/`exception`) | 候选测试描述 | 来源类型 |
|---|---|---|---|---|
| `CAND-U-01` | `FP-<module>-01` | `normal` | `<candidate_unit_test_desc>` | `<docs|legacy_tests|both>` |

### 3.2 性能基准候选 (`b_`)

| 候选编号 | 关联功能点 | 性能热点原因 | 计划负载规模 | 关注指标 |
|---|---|---|---|---|
| `CAND-B-01` | `FP-<module>-01` | `<hotspot_reason>` | `<workload_scale>` | `ops/sec`, `ns/op`, `B/op` |

## 4. 待确认与实现差异 (Gaps)

| 差异编号 | 涉及功能点 | 差异类型 (`unimplemented`/`conflict`/`missing_data`) | 详细说明与处置方式 |
|---|---|---|---|
| `GAP-<module>-01` | `FP-<module>-01` | `unimplemented` | `<gap_detail_and_handling>` |
