# 远期特性与技术债池 (future.md)

> **性质**: 跨版本远期池 ｜ **发版约定**: 每次版本发版前必须联合评审本表事项（立项/推迟/废弃）

---

## 1. 远期特性规划 (Future Features)

| 规划编号 | 业务领域 | 方向概述 | 期望版本 | 状态 |
|---|---|---|---|---|
| F-001 | 测试执行 | 变异测试（mutation testing）评估用例有效性 | 待评审 | 远期 |
| F-002 | 测试执行 | run 固定基线（baseline）对比 | 待评审 | 远期 |
| F-003 | 命令路由 | 只读 status 子命令 | 待评审 | 远期 |
| F-004 | 用例生成 | plans 阶段用户确认点 | 待评审 | 远期 |
| F-005 | 测试执行 | run 结束后的固定对话回执 | 待评审 | 远期 |
| F-006 | 多语言 | Python、Go 之外的语言扩展 | 待评审 | 远期 |

---

## 2. 技术债务排查 (Technical Debts)

| 债务编号 | 模块 | 债务风险说明 | 发现日期 | 建议处置方案 |
|---|---|---|---|---|
| D-001 | ad-flow 治理总账 | 升级 1.8.1 后 docs/devel/index.json 设计登记仍在根级 designs（新版为 subsystems[design].designs），变更总账主题成员旧键 topics.*.cards 与新键 topics.*.changes 并存 | 2026-11-23 | 以后单独开卡统一迁移，本批不迁移 |
| D-002 | COV-GAP / run | COV-GAP 源码匹配用 manifest 源文件哈希与当前源码比对，但 `last_run` 未记录本次运行所对应的源码版本；create→run→改源码→create→create 序列可能把 v1 的缺口登记到 v2 上（K2 于 2026-11-24 module_scope 合并后评审提出） | 2026-11-24 | run 将源文件哈希写入 `last_run`，COV-GAP 以 `last_run` 记录的哈希判定源码匹配；Bella 2026-11-24 定为放入 future 后续修复 |
| D-003 | module_scope / resume | resume 收到与已记录范围不同的 `--module` 时静默沿用旧 module_scope，不提示（K2 于 2026-11-24 module_scope 合并后评审提出） | 2026-11-24 | resume 传入的 `--module` 与记录范围不一致时停止并报告，不做任何写入；Bella 2026-11-24 定为放入 future 后续修复 |
| D-004 | module_scope / 测试 | 新增的 `tests/test_module_scope.py` 只校验文档中是否写明规则，未验证 module_scope 实际行为（K2 于 2026-11-24 module_scope 合并后评审提出） | 2026-11-24 | 为 module_scope 补行为级测试；Bella 2026-11-24 定为放入 future 后续修复 |
