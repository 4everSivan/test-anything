# `<module>` 模块性能基准规格 (`b_<module>_cases`)

> **module**: <module> ｜ **type**: benchmark_cases ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active

## 1. 基准测试用例总表

| 用例 ID | 基准名称 | 关联功能点 | 目标源码符号 | 负载规模 | 核心采集指标 | 绑定基准函数 | 状态 |
|---|---|---|---|---|---|---|---|
| `BM-<module>-001` | `<bench_title>` | `FP-<module>-01` | `<src_file> :: <func_name>` | `<workload_scale>` | `ops/sec`, `ns/op`, `B/op` | `<bench_func_name>` | `active` |

## 2. 基准规格详情

### BM-<module>-001: <bench_title>

- **关联功能点与热点说明**：`FP-<module>-01`；`<hotspot_reason>`
- **目标符号**：`<src_file> :: <full_signature>`
- **负载规模（Workload）**：`<workload_dataset_and_size>`
- **预热与迭代策略**：`<warmup_and_iterations>`
- **采集指标与基线阈值**：`<metrics_and_threshold>`
