# `textutil` 模块性能基准规格 (`b_textutil_cases`)

> **module**: textutil ｜ **type**: benchmark_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 基准测试用例总表

| 用例 ID | 基准名称 | 关联功能点 | 目标源码符号 | 负载规模 | 核心采集指标 | 绑定基准函数 | 状态 |
|---|---|---|---|---|---|---|---|
| `BM-textutil-001` | 长字符串反转 | `FP-textutil-01` | `textutil/textutil.go :: Reverse` | 4,096 字符的字符串 | `ns/op`、`B/op` | `BenchmarkBM_Textutil_001_ReverseLongString` | `active` |

## 2. 基准规格详情

### BM-textutil-001: 长字符串反转

- **关联功能点与热点说明**：`FP-textutil-01`（字符串反转）；反转需把字符串整体解码为 rune 切片再重新编码，长文本下内存与耗时同步增长。
- **目标符号**：`textutil/textutil.go :: Reverse(s string) string`
- **负载规模（Workload）**：由 `"abcba"` 重复拼接出的 4,096 字符字符串，每轮反转一次
- **预热与迭代策略**：由 `go test -bench` 框架自适配轮数（`b.N`），并以 `-count=1` 禁用结果缓存
- **采集指标与基线阈值**：`ns/op`、`B/op`、`allocs/op`；单次耗时退化超过 15% 时在报告中标记关注
