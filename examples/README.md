# 样例工程 (examples/)

> **created**: 2026-11-24 ｜ **last-change**: 2026-11-24 ｜ **status**: active

本目录是产物校验器 [`scripts/ta-verify`](../scripts/ta-verify) 的回归基线：**黄金样例必须通过校验，负向样例必须命中各自的预期诊断码**。技能自身的 CI 与契约测试（`tests/`）都以本目录为依据。

## 1. 黄金样例

| 样例 | 技术栈 | 业务模块 | 用例规模 | 用来覆盖的场景 |
|---|---|---|---|---|
| [`python-sample/`](python-sample/) | Python 3.8+ / pytest 8 | `wordcount`、`slugify` | 6 条单测 + 2 条基准，另有 1 条 `todo` | 多模块工程；含“文档已声明但源码未实现”的功能点（`FP-slugify-03`），对应规格标记 `todo` 且不生成测试代码 |
| [`go-sample/`](go-sample/) | Go 1.21+ / `go test` | `calc`、`textutil` | 6 条单测 + 2 条基准 | Go 测试文件命名（`u_<module>_test.go`、`b_<module>_bench_test.go`）；Go 要求缓存目录为绝对路径，运行命令以 `$(pwd)` 拼出 |

每个样例都是一个独立的最小目标工程：自己的业务源码、项目文档与一份由 `$test-anything create` / `$test-anything run` 流程产出的受管 `tests/`。

- `tests/docs/` 下的草稿、计划、用例规格与三份 `*_latest.md` 报告、`tests/.state/manifest.json` 与 `last_run.json` 均为**真实运行产物**：报告与状态文件里的退出码、计数、耗时和基准指标取自页眉 `run_id` 所标识的那一次运行器输出，未测得的数值记 `n/a` 或 `<5`，没有用模板占位 `0` 充数。
- 样例自身的 `.gitignore` 按 [目录契约](../references/state-and-backup.md) 忽略 `/_test_anything_backup/` 与 `/tests/tmp/`，因此克隆后没有 `tests/tmp/` 属正常现象。

## 2. 负向样例

[`negative/`](negative/) 下每个目录是一个只含 `tests/` 的最小目标工程，各自只注入一种违规，目录内的 `expected.json` 登记其预期结果。样例清单与维护约定见 [negative/README.md](negative/README.md)。

## 3. 本地核对

在技能包根目录执行：

```bash
# 黄金样例：三条命令均应 Exit 0
scripts/ta-verify --target examples/python-sample --scope all
scripts/ta-verify --target examples/go-sample --scope all

# 负向样例示例：应 Exit 4 并报出 CASE_WITHOUT_TEST_CODE
scripts/ta-verify --target examples/negative/orphan-case --scope create

# 契约测试：一次性覆盖黄金样例、全部负向样例、诊断码溯源与流程接入
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

`ta-verify` 对目标工程只读：以上命令不会在样例目录内写入任何文件。若手动执行样例自身的单测或基准（命令见各样例的 `tests/docs/plans/test_plan.md`），缓存会落在已被忽略的 `tests/tmp/`，同样不会污染源码树。

## 4. 维护约定

黄金产物随技能规则变更同步更新。规则改动导致黄金产物不再通过 `ta-verify` 时，必须在同一变更中重新生成并经人工审定后提交，**不得放宽校验项去迁就旧产物**；新增或调整诊断码时，同步补充对应的负向样例或契约测试，使每个诊断码都有回归覆盖。
