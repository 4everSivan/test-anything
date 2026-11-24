# `calc` 模块功能点与测试草稿

> **module**: calc ｜ **type**: draft ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 来源与模块边界

- **源文档路径**：`README.md`（Functional points 第 1、2 条）
- **目标源码路径**：`calc/calc.go`
- **存量测试备份**：无
- **模块职责边界**：只提供整数加法与带零除数保护的整数除法；不处理浮点、大数与溢出检测。

## 2. 功能点拆解清单 (Functional Points)

| 功能点 ID | 功能名称 | 触发与输入约束 | 预期行为与输出 | 边界与异常规则 | 来源定位 |
|---|---|---|---|---|---|
| `FP-calc-01` | 整数加法 | 入参 `a`、`b` 为 `int` | 返回二者的和 | 负数同样适用 | `README.md` Functional points 第 1 条 |
| `FP-calc-02` | 整数除法 | 入参 `a`、`b` 为 `int` | 返回向零截断的商与 `nil` error | `b` 为 `0` 时返回非 `nil` 的 error，不得 panic | `README.md` Functional points 第 2 条 |

## 3. 候选测试点分流

### 3.1 单元测试候选 (`u_`)

| 候选编号 | 关联功能点 | 场景维度 (`normal`/`boundary`/`exception`) | 候选测试描述 | 来源类型 |
|---|---|---|---|---|
| `CAND-U-01` | `FP-calc-01` | `normal` | 两个正整数相加 | `docs` |
| `CAND-U-02` | `FP-calc-02` | `exception` | 除数为 `0` 时返回 error | `docs` |
| `CAND-U-03` | `FP-calc-02` | `boundary` | 负数被除数向零截断 | `docs` |

### 3.2 性能基准候选 (`b_`)

| 候选编号 | 关联功能点 | 性能热点原因 | 计划负载规模 | 关注指标 |
|---|---|---|---|---|
| `CAND-B-01` | `FP-calc-01` | 加法处于内层循环等高频调用路径，单次开销决定整段循环的吞吐 | 每轮 1,000 次加法 | `ns/op`、`B/op` |

## 4. 待确认与实现差异 (Gaps)

| 差异编号 | 涉及功能点 | 差异类型 (`unimplemented`/`conflict`/`missing_data`) | 详细说明与处置方式 |
|---|---|---|---|
| — | — | — | 暂无：文档描述的两个功能点与源码签名一致。 |
