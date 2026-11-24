# 变更日志 (CHANGELOG)

记录项目的显著变更，分类参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased] - 待发布

### Added

- [T01](docs/devel/task/T01.json)：交付 test-anything v0.1 技能包——`SKILL.md`、`workflow.yaml`、按需加载的规则手册、13 份标准模板与技能包契约测试。
- [T02](docs/devel/task/T02.json)：新增只读产物校验器 `scripts/ta-verify`（单文件、仅标准库，退出码 0 / 4 / 2）。`create` 须待其 `--scope create` Exit 0 才置 `create_status: complete`，`run` 写完报告后只报告其 `--scope run` 校验结果、不改测试判定；新增规则手册 `references/artifact-verification.md`、Python 与 Go 黄金样例、六个负向样例与最小 CI。
- [T04](docs/devel/task/T04.json)：`create --module <module>`（可重复）只对指定模块执行 Stage 1–4 并在 manifest 的 `module_scope` 记录范围，其余模块零改动；用例编号只追加、不重排，能力已从源码移除的用例标记 `deprecated` 并停止生成代码而不删除；增量 `create` 把 `uncovered[]` 登记为 `COV-GAP` 并注明来源 `run_id`，仅能映射既有 `FP-` 的缺口补测，超限部分按计数汇总。`ta-verify` 对 `deprecated` 用例豁免“须有测试代码”，但仍报告其仍绑定测试函数（`CASE_DEPRECATED_WITH_CODE`），并校验可选 `module_scope`。
- [T03](docs/devel/task/T03.json)：`run` 与 `run unittest` 在同一次单测运行中采集 Python（`coverage run --branch`）与 Go（`-coverprofile`）覆盖率，写入 `last_run.json.unit.coverage`，并在单元测试报告新增行/分支覆盖率列与「未覆盖符号」节、全量报告新增行覆盖率列。`ta-verify` 新增 `--coverage` 解析模式（coverage JSON / LCOV / Go coverprofile）与 `--scope run` 的覆盖率核对；未测得的值一律为 `N/A`，不设阈值、不改测试判定。

### Changed

- [C003](docs/devel/change/C003.json)：修正 `00-系统总体设计` 第 1 节与 4.3 中“技能执行资源尚未落地实现/待交付”的过时表述，如实记录 v0.1.0 已交付的技能资源与回归验证；业务规则不变。

### Fixed

- [C001](docs/devel/change/C001.json)：修复 `create` 中断后不可续跑（`manifest.json` 以 `create_status`/`completed_stage` 记录进度并支持续跑）、存量 `tests/` 未经用户确认即迁移，以及运行异常被误报为通过（报告新增 `error` 状态及确定性判定规则）。
- [C002](docs/devel/change/C002.json)：`run` 仅原地覆盖 `*_latest.md`，不再按批次堆积 `*_report_<run_id>.md`；`all_report` 第 3 节改为本次运行信息，旧批次报告须经用户确认后才清理。
- [C004](docs/devel/change/C004.json)：最小 CI 改为检出完整历史（`fetch-depth: 0`）。默认的浅克隆只有最新一个提交，使 `adflow-verify` 对已收口卡 `sync.commit` 的祖先校验误报 `COMMIT_NOT_ANCESTOR`，契约测试步骤因此失败。
- [C005](docs/devel/change/C005.json)：补齐 `module_scope` 语义（Stage 0 写入去重后的 `--module` 列表、续跑沿用记录值、全量完成重置为 `[]`、裸调增量写 `[]`、fresh/legacy 禁用 `--module`、Stage 4 只局部替换在范围模块）与 `COV-GAP` 三条登记约束（仅 `module_scope` 内模块、同 `run_id` 替换不增号、源码哈希不一致整批不登记）；00 补 `create --module` 路由与 T02/T04 演进行，`INV_DRAFT_FIRST_PIPELINE` 改为不按 `u_`/`b_` 拆分，`INV_COVERAGE_HONEST_AND_PASSIVE` 统一为覆盖率永不触发第二次运行（仅覆盖率包裹崩溃时允许普通命令重跑一次）；修正负向样例 plan/cases 状态不一致与 01/02 §4.3 过时表述。
<!-- 只添加真实变更并关联真实 C/T 卡，不预登记示例卡或发布版本。
真实卡片建立后的链接语法示例：
- [T01](docs/devel/task/T01.json)：交付的能力。
- [C001](docs/devel/change/C001.json)：修复的缺陷。
填写实际发布日期和批次，归档后同步卡片路由。
-->
