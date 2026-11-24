# 变更日志 (CHANGELOG)

记录项目的显著变更，分类参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased] - 待发布

### Added

- [T02](docs/devel/task/T02.json)：新增只读产物校验器 `scripts/ta-verify`（单文件、仅标准库，退出码 0 / 4 / 2）。`create` 须待其 `--scope create` Exit 0 才置 `create_status: complete`，`run` 写完报告后只报告其 `--scope run` 校验结果、不改测试判定；新增规则手册 `references/artifact-verification.md`、Python 与 Go 黄金样例、六个负向样例与最小 CI。
- [T03](docs/devel/task/T03.json)：`run` 与 `run unittest` 在同一次单测运行中采集 Python（`coverage run --branch`）与 Go（`-coverprofile`）覆盖率，写入 `last_run.json.unit.coverage`，并在单元测试报告新增行/分支覆盖率列与「未覆盖符号」节、全量报告新增行覆盖率列。`ta-verify` 新增 `--coverage` 解析模式（coverage JSON / LCOV / Go coverprofile）与 `--scope run` 的覆盖率核对；未测得的值一律为 `N/A`，不设阈值、不改测试判定。

### Changed

### Fixed

- [C004](docs/devel/change/C004.json)：最小 CI 改为检出完整历史（`fetch-depth: 0`）。默认的浅克隆只有最新一个提交，使 `adflow-verify` 对已收口卡 `sync.commit` 的祖先校验误报 `COMMIT_NOT_ANCESTOR`，契约测试步骤因此失败。
<!-- 只添加真实变更并关联真实 C/T 卡，不预登记示例卡或发布版本。
真实卡片建立后的链接语法示例：
- [T01](docs/devel/task/T01.json)：交付的能力。
- [C001](docs/devel/change/C001.json)：修复的缺陷。
填写实际发布日期和批次，归档后同步卡片路由。
-->
