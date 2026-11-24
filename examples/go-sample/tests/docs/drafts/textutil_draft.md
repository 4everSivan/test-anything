# `textutil` 模块功能点与测试草稿

> **module**: textutil ｜ **type**: draft ｜ **updated_at**: 2026-11-24 ｜ **status**: active

## 1. 来源与模块边界

- **源文档路径**：`README.md`（Functional points 第 3、4 条）
- **目标源码路径**：`textutil/textutil.go`
- **存量测试备份**：无
- **模块职责边界**：只提供按 rune 反转字符串与回文判断；不做分词、编码转换或国际化排序。

## 2. 功能点拆解清单 (Functional Points)

| 功能点 ID | 功能名称 | 触发与输入约束 | 预期行为与输出 | 边界与异常规则 | 来源定位 |
|---|---|---|---|---|---|
| `FP-textutil-01` | 字符串反转 | 入参 `s` 为字符串 | 返回 rune 顺序相反的字符串 | 空字符串返回空串；多字节字符按字符而非字节反转 | `README.md` Functional points 第 3 条 |
| `FP-textutil-02` | 回文判断 | 入参 `s` 为字符串 | 忽略大小写与空格后正读反读相同则返回 `true` | 不满足回文条件返回 `false` | `README.md` Functional points 第 4 条 |

## 3. 候选测试点分流

### 3.1 单元测试候选 (`u_`)

| 候选编号 | 关联功能点 | 场景维度 (`normal`/`boundary`/`exception`) | 候选测试描述 | 来源类型 |
|---|---|---|---|---|
| `CAND-U-01` | `FP-textutil-01` | `normal` | 普通字符串按 rune 反转 | `docs` |
| `CAND-U-02` | `FP-textutil-01` | `boundary` | 空字符串与多字节字符的反转 | `docs` |
| `CAND-U-03` | `FP-textutil-02` | `normal` | 回文与非回文输入的判断 | `docs` |

### 3.2 性能基准候选 (`b_`)

| 候选编号 | 关联功能点 | 性能热点原因 | 计划负载规模 | 关注指标 |
|---|---|---|---|---|
| `CAND-B-01` | `FP-textutil-01` | 反转需把字符串整体解码为 rune 切片再重新编码，长文本下内存与耗时同步增长 | 4,096 字符的字符串 | `ns/op`、`B/op` |

## 4. 待确认与实现差异 (Gaps)

| 差异编号 | 涉及功能点 | 差异类型 (`unimplemented`/`conflict`/`missing_data`) | 详细说明与处置方式 |
|---|---|---|---|
| — | — | — | 暂无：文档描述的两个功能点与源码签名一致。 |
