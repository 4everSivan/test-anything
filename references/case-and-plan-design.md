# Stage 2 & Stage 3: Two-Level Test Plans and Case Specifications

This reference owns Stage 2 (`STAGE_2_PLAN`: `tests/docs/plans/`) and Stage 3 (`STAGE_3_CASE`: `tests/docs/cases/`) of the `create` pipeline.

## 1. Stage 2: Two-Level Test Plan (`tests/docs/plans/`)

### 1.1 Global Test Plan (`tests/docs/plans/test_plan.md`)

Render from [templates/docs/test_plan.md.tpl](../templates/docs/test_plan.md.tpl) with header `> **module**: global ｜ **type**: test_plan ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active` and three H2 sections:
1. `## 1. 目标技术栈与执行环境`: Primary language, unit/benchmark frameworks, exact `unit_runner` and `benchmark_runner` commands, and explicit `tests/tmp/` redirection for caches and runtime artifacts.
2. `## 2. 模块测试覆盖总表`: Table linking each `<module>` to `<module>_plan.md`, `../cases/u_<module>_cases.md`, `../cases/b_<module>_cases.md`, `tests/unit/u_<module>_test.<ext>`, `tests/benchmark/b_<module>_bench.<ext>`, and `tests/fixtures/<module>_fixtures.json`.
3. `## 3. 全局夹具与隔离策略`: Rules for isolating external network/database/IO dependencies via `tests/fixtures/` and confining temporary files to `tests/tmp/`.

### 1.2 Per-Module Test Plan (`tests/docs/plans/<module>_plan.md`)

Render from [templates/docs/module_plan.md.tpl](../templates/docs/module_plan.md.tpl) with header `> **module**: <module> ｜ **type**: module_plan ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active` and two H2 sections:
1. `## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵`:
   - Assign stable IDs: `UT-<module>-001`, `UT-<module>-002`... for unit tests (`u_`) and `BM-<module>-001`, `BM-<module>-002`... for benchmarks (`b_`).
   - Columns: `功能点 ID` | `用例 ID` | `类型 (u_/b_)` | `场景/负载分类` | `目标源码文件与函数签名` | `对应测试代码位置` | `优先级` | `状态`.
   - Set `状态` to `active` for implemented targets and `todo` for `unimplemented` gaps.
2. `## 2. 模块夹具与 Mock 策略`: Document the fixtures in `tests/fixtures/<module>_fixtures.*` and mock boundaries.

## 2. Stage 3: Structured Case Specifications (`tests/docs/cases/`)

All case specification files live flat in `tests/docs/cases/` and use `u_` or `b_` prefixes. Both follow the **Summary Table + Per-Case H3 Card** layout.

### 2.1 Unit Test Cases (`tests/docs/cases/u_<module>_cases.md`)

Render from [templates/docs/u_cases.md.tpl](../templates/docs/u_cases.md.tpl) with header `> **module**: <module> ｜ **type**: unit_cases ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active`:
- `## 1. 单元测试用例总表`: Table of all `UT-<module>-<NNN>` cases (`用例 ID` | `用例标题` | `关联功能点` | `场景类型 (normal/boundary/exception)` | `目标源码符号` | `绑定测试函数` | `状态`).
- `## 2. 用例规格详情`: Each case uses heading `### UT-<module>-<NNN>: <用例标题>` and **must contain all 6 bullet elements**:
  1. `- **关联功能点**`: `FP-<module>-<NN>` and feature name
  2. `- **目标符号**`: `<source_file> :: <function_or_method_signature>`
  3. `- **场景类型**`: `normal` | `boundary` | `exception`
  4. `- **前置条件与夹具**`: fixture keys loaded from `tests/fixtures/` or mock setup
  5. `- **输入参数（Given / When）**`: concrete argument values or payload construction
  6. `- **预期结果与断言（Then）**`: numbered list of deterministic assertions on return value, state mutation, or raised exception

### 2.2 Benchmark Cases (`tests/docs/cases/b_<module>_cases.md`)

Render from [templates/docs/b_cases.md.tpl](../templates/docs/b_cases.md.tpl) with header `> **module**: <module> ｜ **type**: benchmark_cases ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active`:
- `## 1. 基准测试用例总表`: Table of all `BM-<module>-<NNN>` cases (`用例 ID` | `基准名称` | `关联功能点` | `目标源码符号` | `负载规模` | `核心采集指标` | `绑定基准函数` | `状态`).
- `## 2. 基准规格详情`: Each case uses heading `### BM-<module>-<NNN>: <基准名称>` and **must contain all 5 bullet elements**:
  1. `- **关联功能点与热点说明**`: `FP-<module>-<NN>` and why this path is performance-critical
  2. `- **目标符号**`: `<source_file> :: <function_or_method_signature>`
  3. `- **负载规模（Workload）**`: dataset size/scale and `tests/fixtures/` source
  4. `- **预热与迭代策略**`: warmup rounds, sample iterations or duration window
  5. `- **采集指标与基线阈值**`: target metrics (`ops/sec`, `ns/op` or `us/op`, `P99 latency`, `B/op`) and SLA or regression threshold
