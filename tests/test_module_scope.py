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


if __name__ == "__main__":
    unittest.main()
