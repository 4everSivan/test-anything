#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contracts of T04: module-scoped create, deprecated cases, and COV-GAP supplemental tests."""

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "scripts" / "ta-verify"
PY_SAMPLE = ROOT / "examples" / "python-sample"
NEGATIVE = ROOT / "examples" / "negative" / "deprecated-case-with-code"
WORKFLOW = "workflow.yaml"
SCRATCH = ROOT / "local" / "tmp" / "module-scope-tests"


def read(path):
    return (ROOT / path if isinstance(path, str) else path).read_text(encoding="utf-8")


def run_verify(target, *flags):
    return subprocess.run([sys.executable, "-B", str(VERIFY), "--target", str(target), *flags],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, check=False)


def codes_by_severity(proc):
    found = {}
    for code, levels in json.loads(proc.stdout)["summary"]["codes"].items():
        for severity in levels:
            found.setdefault(severity, set()).add(code)
    return found


class TestModuleScopedCreate(unittest.TestCase):
    """`create --module` is a first-class route whose scoping rules live in one protocol block."""

    def test_route_is_repeatable_and_scoped(self):
        workflow = read(WORKFLOW)
        route = workflow.split('- match: "$test-anything create --module <module>"', 1)[1].split("- match:", 1)[0]
        self.assertIn('resolved_track: "CREATE_PIPELINE"', route)
        self.assertIn('scope: "module"', route)
        self.assertIn("repeatable: true", route)
        self.assertIn("aborts the run", route)

    def test_protocol_states_every_scope_rule(self):
        block = read(WORKFLOW).split("module_scope_protocol:", 1)[1].split("\n  ", 1)[0]
        for phrase in ("record them in manifest 'module_scope'", "update only their module records",
                       "append-only", "mark its case 'deprecated'", "generate no code",
                       "来源: coverage(<run_id>)", "only gaps that map to an existing FP-",
                       "aggregate COV-GAP row with the omitted count"):
            self.assertIn(phrase, block)

    def test_stages_carry_the_rules(self):
        workflow = read(WORKFLOW)
        stage1 = workflow.split('id: "STAGE_1_DRAFT"', 1)[1].split('id: "STAGE_2_PLAN"', 1)[0]
        stage2 = workflow.split('id: "STAGE_2_PLAN"', 1)[1].split('id: "STAGE_3_CASE"', 1)[0]
        stage3 = workflow.split('id: "STAGE_3_CASE"', 1)[1].split('id: "STAGE_4_', 1)[0]
        self.assertIn("COV-GAP-<module>-<NN>", stage1)
        self.assertIn("来源: coverage(<run_id>)", stage1)
        self.assertIn("never drop gaps silently", stage1)
        self.assertIn("IDs are append-only", stage2)
        self.assertIn("'status: deprecated'", stage3)
        self.assertIn("never delete or renumber it", stage3)

    def test_manifest_template_has_module_scope(self):
        template = json.loads(read("templates/state/manifest.json.tpl"))
        self.assertEqual(template.get("module_scope"), [])

    def test_designs_and_references_own_the_rules(self):
        design01 = read("docs/devel/design/01-目录结构与状态管理.md")
        self.assertIn("`module_scope`", design01)
        self.assertIn("`deprecated` 用例保留在 `cases/` 规格中但不生成代码", design01)
        design02 = read("docs/devel/design/02-测试用例生成流水线.md")
        self.assertNotIn("待 T04 交付", design02)
        self.assertIn("[T04](../task/T04.json) | 能力交付 | 增量 create 与缺口补测落地", design02)
        scanning = read("references/doc-scanning.md")
        self.assertIn("### 4.1 Coverage gaps on incremental create (`COV-GAP`)", scanning)
        for phrase in ("来源: coverage(<run_id>)", "Only FP-backed gaps become tests",
                       "Respect the cap", "Never drop a gap silently"):
            self.assertIn(phrase, scanning)
        plan = read("references/case-and-plan-design.md")
        for phrase in ("IDs are append-only", "deprecated"):
            self.assertIn(phrase, plan)
        state = read("references/state-and-backup.md")
        self.assertIn("`module_scope` (optional)", state)
        self.assertIn("`deprecated`", state)
        gate = read("references/artifact-verification.md")
        self.assertIn("CASE_DEPRECATED_WITH_CODE", gate)


class TestDeprecatedBehavior(unittest.TestCase):
    """A deprecated case needs no code; a function still bound to it is a violation."""

    def test_golden_sample_keeps_a_deprecated_case_without_code(self):
        cases = read(PY_SAMPLE / "tests/docs/cases/u_slugify_cases.md")
        self.assertIn("| `UT-slugify-005` |", cases)
        self.assertIn("| `deprecated` |", cases)
        manifest = json.loads(read(PY_SAMPLE / "tests/.state/manifest.json"))
        self.assertNotIn("UT-slugify-005", manifest["modules"]["slugify"]["unit_code"]["case_ids"])
        self.assertNotIn("UT-slugify-005", read(PY_SAMPLE / "tests/unit/u_slugify_test.py"))
        for scope in ("create", "run", "all"):
            self.assertEqual(run_verify(PY_SAMPLE, "--scope", scope).returncode, 0, scope)

    def test_negative_sample_reports_only_that_violation(self):
        expected = json.loads(read(NEGATIVE / "expected.json"))
        proc = run_verify(NEGATIVE, "--scope", expected["scope"], "--json")
        self.assertEqual(proc.returncode, 4)
        self.assertEqual(codes_by_severity(proc)["ERROR"], set(expected["codes"]))
        self.assertEqual(expected["codes"], ["CASE_DEPRECATED_WITH_CODE"])

    def test_deprecated_status_is_exempt_and_todo_still_is_too(self):
        import importlib.machinery
        import importlib.util
        loader = importlib.machinery.SourceFileLoader("ta_verify_scope", str(VERIFY))
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader("ta_verify_scope", loader))
        previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        try:
            loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        self.assertFalse(module.requires_code("deprecated"))
        self.assertFalse(module.requires_code("todo"))
        self.assertFalse(module.requires_code("unimplemented"))
        self.assertTrue(module.requires_code("active"))
        self.assertTrue(module.requires_code("active/deprecated"))  # 组合写法仍要求生成代码

    def test_module_scope_field_is_validated(self):
        self.addClassCleanup(shutil.rmtree, SCRATCH, True)
        shutil.rmtree(SCRATCH, ignore_errors=True)
        base = SCRATCH / "base"
        shutil.copytree(PY_SAMPLE, base, ignore=shutil.ignore_patterns("tmp"))

        def with_scope(name, scope):
            target = SCRATCH / name
            shutil.copytree(base, target)
            path = target / "tests/.state/manifest.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["module_scope"] = scope
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return run_verify(target, "--scope", "create", "--json")

        ok = with_scope("valid", ["wordcount", "slugify"])
        self.assertEqual(ok.returncode, 0, ok.stdout)
        bad = with_scope("unknown", ["wordcount", "nope"])
        self.assertEqual(bad.returncode, 4)
        self.assertIn("MANIFEST_FIELD_INVALID", codes_by_severity(bad)["ERROR"])
        shape = with_scope("shape", "wordcount")
        self.assertEqual(shape.returncode, 4)
        self.assertIn("MANIFEST_FIELD_INVALID", codes_by_severity(shape)["ERROR"])


class TestScopeSemantics(unittest.TestCase):
    """C005: module_scope has one lifecycle rule set; COV-GAP registration is scoped, deduplicated and source-fresh."""

    OWNERS = [
        "workflow.yaml",
        "references/state-and-backup.md",
        "docs/devel/design/01-目录结构与状态管理.md",
        "docs/devel/design/02-测试用例生成流水线.md",
    ]

    MODULE_SCOPE_RULES = {
        "stage-0 write timing": (
            "as soon as Stage 0 resolves the route, write 'module_scope'",
            "The same write records `module_scope` as the deduplicated `--module` list",
            "Stage 0 路由确定后即写入 `--module` 去重后的列表",
            "`module_scope` 在 Stage 0 路由确定后即写入",
        ),
        "resume keeps the recorded scope": (
            "A resume always keeps the 'module_scope' recorded at interruption",
            "A resume always keeps the `module_scope` recorded at interruption",
            "续跑一律沿用中断时记录的 `module_scope`",
            "续跑（含裸调续跑）一律沿用中断时记录的值",
        ),
        "full create resets to []": (
            "A full create without '--module' leaves 'module_scope' as [] on completion",
            "a full create leaves `[]` on completion",
            "全量 `create` 完成后仍为 `[]`",
            "全量 `create` 完成后仍为 `[]`",
        ),
        "bare incremental writes []": (
            "a bare incremental create also writes []",
            "a bare incremental create also writes `[]`",
            "裸调增量写 `[]`",
            "裸调增量写 `[]`",
        ),
        "fresh and legacy reject --module": (
            "Fresh and legacy modes reject '--module'",
            "reject `create --module`",
            "fresh 与存量迁移（legacy）模式下禁用",
            "fresh 与存量迁移（legacy）模式下禁用",
        ),
        "stage-4 partial replace": (
            "Stage 4 replaces only the 'modules' entries of modules in scope",
            "Stage 4 replaces only the in-scope `modules` entries",
            "Stage 4 只替换在范围模块的 `modules` 条目",
            "Stage 4 只替换在范围模块的 `modules` 条目",
        ),
    }

    COV_GAP_RULES = {
        "module scope limits registration": (
            "only for modules in 'module_scope'",
            "register only gaps whose `uncovered[].module` is in the manifest's `module_scope`",
            "受限 `create` 只登记 `module_scope` 内模块的缺口",
        ),
        "same run_id replaces without new numbers": (
            "re-registering gaps of the same run_id replaces the earlier rows without allocating new numbers",
            "Re-registering gaps from the same `run_id` replaces the earlier rows in place and allocates no new numbers",
            "同一 `run_id` 的缺口重复登记时以新记录替换旧记录、不追加新编号",
        ),
        "stale sources register nothing": (
            "register only when 'last_run' matches the current sources by the manifest source hashes",
            "Register gaps only when the current source files still match the manifest's recorded source hashes",
            "仅当当前源码与 manifest 记录的源文件哈希一致",
        ),
    }

    def test_every_owner_states_all_six_module_scope_rules(self):
        texts = {rel: read(rel) for rel in self.OWNERS}
        for rule, phrases in self.MODULE_SCOPE_RULES.items():
            for rel, phrase in zip(self.OWNERS, phrases):
                self.assertIn(phrase, texts[rel], "%s does not state the %s rule" % (rel, rule))

    def test_cov_gap_constraints_are_stated_where_they_apply(self):
        owners = ["workflow.yaml", "references/doc-scanning.md",
                  "docs/devel/design/02-测试用例生成流水线.md"]
        texts = {rel: read(rel) for rel in owners}
        for rule, phrases in self.COV_GAP_RULES.items():
            for rel, phrase in zip(owners, phrases):
                self.assertIn(phrase, texts[rel], "%s does not state the %s rule" % (rel, rule))

    def test_invariants_match_the_corrected_wording(self):
        wf = read("workflow.yaml")
        pipeline = wf.split('id: "INV_DRAFT_FIRST_PIPELINE"', 1)[1].split('- id:', 1)[0]
        self.assertIn("never splits a run into separate u_/b_ tracks", pipeline)
        self.assertIn("narrows only the module set, never the set of tracks", pipeline)
        self.assertNotIn("always executes the full scope", pipeline)

        coverage = wf.split('id: "INV_COVERAGE_HONEST_AND_PASSIVE"', 1)[1].split('- id:', 1)[0]
        self.assertIn("coverage itself never triggers a second test run", coverage)
        self.assertIn("re-run the plain unit command once", coverage)
        design03 = read("docs/devel/design/03-测试执行与报告引擎.md")
        self.assertIn("覆盖率本身永不触发第二次测试运行", design03)
        self.assertIn("允许以普通命令重跑一次", design03)

    def test_overview_route_and_evolution_follow_delivery_order(self):
        overview = read("docs/devel/design/00-系统总体设计.md")
        self.assertIn("`$test-anything create --module <module>`", overview)
        self.assertIn("| [T04](../task/T04.json) |", overview)
        table = overview.split("### 4.4 规则演进", 1)[1]
        self.assertLess(table.index("| [T02](../task/T02.json) |"),
                        table.index("| [C003](../change/C003.json) |"))
        for rel in ("docs/devel/design/01-目录结构与状态管理.md",
                    "docs/devel/design/02-测试用例生成流水线.md"):
            self.assertNotIn("待后续 T 卡实现", read(rel), rel)

    def test_negative_sample_plan_and_cases_agree(self):
        plan = read(NEGATIVE / "tests/docs/plans/wordcount_plan.md")
        cases = read(NEGATIVE / "tests/docs/cases/u_wordcount_cases.md")
        plan_row = next(line for line in plan.splitlines() if "UT-wordcount-002" in line)
        case_row = next(line for line in cases.splitlines()
                        if line.startswith("|") and "`UT-wordcount-002`" in line)
        for row, source in ((plan_row, "plan"), (case_row, "cases")):
            self.assertIn("`deprecated`", row, "%s still marks UT-wordcount-002 active" % source)
        self.assertIn("不生成测试代码", plan_row)

        expected = json.loads(read(NEGATIVE / "expected.json"))
        proc = run_verify(NEGATIVE, "--scope", expected["scope"], "--json")
        self.assertEqual(proc.returncode, 4)
        self.assertEqual(codes_by_severity(proc)["ERROR"], set(expected["codes"]))


if __name__ == "__main__":
    unittest.main()
