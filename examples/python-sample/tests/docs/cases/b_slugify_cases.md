# `slugify` 模块性能基准规格 (`b_slugify_cases`)

> **module**: slugify ｜ **type**: benchmark_cases ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 基准测试用例总表

| 用例 ID | 基准名称 | 关联功能点 | 目标源码符号 | 负载规模 | 核心采集指标 | 绑定基准函数 | 状态 |
|---|---|---|---|---|---|---|---|
| `BM-slugify-001` | 万条标题批量生成 slug | `FP-slugify-01` | `textkit/slugify.py :: slugify` | 10,000 条标题 | `ops/sec` | `test_bm_slugify_001_slugify_title_batch` | `active` |

## 2. 基准规格详情

### BM-slugify-001: 万条标题批量生成 slug

- **关联功能点与热点说明**：`FP-slugify-01`（slug 转换）；正则替换与大小写转换需扫描全文，批量处理标题时构成该模块的性能热点。
- **目标符号**：`textkit/slugify.py :: slugify(text: str, max_len: int = None) -> str`
- **负载规模（Workload）**：由 `tests/fixtures/slugify_fixtures.json` 的 `titles` 与 `batch_repeats` 拼出 10,000 条标题
- **预热与迭代策略**：先执行 3 轮预热，再计时 20 轮取平均
- **采集指标与基线阈值**：`ops/sec`（以“条/秒”计，每轮平均耗时的倒数）；单次耗时退化超过 15% 时在报告中标记关注
