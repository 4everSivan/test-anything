# 变更日志 (CHANGELOG)

记录项目的显著变更，分类参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased] - 待发布

### Added

- [T02](docs/devel/task/T02.json)：新增只读产物校验器 `scripts/ta-verify`（单文件、仅标准库，退出码 0 / 4 / 2）。`create` 须待其 `--scope create` Exit 0 才置 `create_status: complete`，`run` 写完报告后只报告其 `--scope run` 校验结果、不改测试判定；新增规则手册 `references/artifact-verification.md`、Python 与 Go 黄金样例、六个负向样例与最小 CI。

### Changed

### Fixed

<!-- 只添加真实变更并关联真实 C/T 卡，不预登记示例卡或发布版本。
真实卡片建立后的链接语法示例：
- [T01](docs/devel/task/T01.json)：交付的能力。
- [C001](docs/devel/change/C001.json)：修复的缺陷。
填写实际发布日期和批次，归档后同步卡片路由。
-->
