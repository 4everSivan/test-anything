# `calc` 模块性能基准规格 (`b_calc_cases`)

> **module**: calc ｜ **type**: benchmark_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 基准测试用例总表

| 用例 ID | 基准名称 | 关联功能点 | 目标源码符号 | 负载规模 | 核心采集指标 | 绑定基准函数 | 状态 |
|---|---|---|---|---|---|---|---|
| `BM-calc-001` | 加法内层循环 | `FP-calc-01` | `calc/calc.go :: Add` | 每轮 1,000 次加法 | `ns/op`、`B/op` | `BenchmarkBM_Calc_001_AddLoop` | `active` |

## 2. 基准规格详情

### BM-calc-001: 加法内层循环

- **关联功能点与热点说明**：`FP-calc-01`（整数加法）；加法常处于内层循环等高频调用路径，单次开销决定整段循环的吞吐。
- **目标符号**：`calc/calc.go :: Add(a, b int) int`
- **负载规模（Workload）**：每轮固定执行 1,000 次加法，由 Go 基准框架自行决定轮数
- **预热与迭代策略**：由 `go test -bench` 框架自适配轮数（`b.N`），并以 `-count=1` 禁用结果缓存
- **采集指标与基线阈值**：`ns/op`、`B/op`、`allocs/op`；单次耗时退化超过 15% 时在报告中标记关注
