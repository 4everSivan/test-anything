#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coverage parsing, the run-scope coverage checks, and the coverage contracts of T03."""

import importlib.machinery
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "scripts" / "ta-verify"
PY_SAMPLE = ROOT / "examples" / "python-sample"
GO_SAMPLE = ROOT / "examples" / "go-sample"
# Tests only ever write inside this git-ignored scratch area (AGENTS.md section 3).
SCRATCH = ROOT / "local" / "tmp" / "coverage-tests"

GO_SOURCE = """package calc

func Add(a, b int) int {
	return a + b
}

func Sub(a, b int) int {
	return a - b
}
"""

PY_SOURCE = """def alpha(x):
    if x:
        return 1
    return 0


def beta():
    return 2
"""


def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_verifier():
    loader = importlib.machinery.SourceFileLoader("ta_verify_cov", str(VERIFY))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader("ta_verify_cov", loader))
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def run_coverage(raw, target=None):
    args = [sys.executable, "-B", str(VERIFY), "--coverage", str(raw)]
    if target is not None:
        args += ["--target", str(target)]
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, check=False)


def parse(raw, target):
    proc = run_coverage(raw, target)
    if proc.returncode != 0:
        raise AssertionError("ta-verify --coverage exited %d: %s" % (proc.returncode, proc.stderr))
    return json.loads(proc.stdout)


def run_verify(target, *flags):
    return subprocess.run([sys.executable, "-B", str(VERIFY), "--target", str(target), *flags],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, check=False)


def codes_by_severity(proc):
    """{severity: set(codes)} taken from the JSON summary."""
    found = {}
    for code, levels in json.loads(proc.stdout)["summary"]["codes"].items():
        for severity in levels:
            found.setdefault(severity, set()).add(code)
    return found


def tool_available(name):
    return shutil.which(name) is not None


class TestParsers(unittest.TestCase):
    """The three accepted raw formats normalize to the same protocol object, without any tool installed."""

    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(shutil.rmtree, SCRATCH, True)
        shutil.rmtree(SCRATCH, ignore_errors=True)
        cls.py_target = SCRATCH / "py-target"
        write(cls.py_target / "pkg/util.py", PY_SOURCE)
        write(cls.py_target / "tests/helpers.py", "def helper():\n    return 1\n")
        cls.go_target = SCRATCH / "go-target"
        write(cls.go_target / "calc/calc.go", GO_SOURCE)

    def coverage_json(self, files):
        return {"meta": {"format": 3, "version": "tests", "branch_coverage": True},
                "files": files,
                "totals": {"num_statements": 0, "covered_lines": 0, "num_branches": 0,
                           "covered_branches": 0, "percent_covered": 0.0}}

    def test_coverage_json_is_counted_by_lines_and_branches_separately(self):
        raw = SCRATCH / "coverage.json"
        write(raw, json.dumps(self.coverage_json({
            "pkg/util.py": {"summary": {"num_statements": 6, "covered_lines": 4,
                                        "num_branches": 2, "covered_branches": 1},
                            "missing_lines": [3, 4], "missing_branches": [[2, 3]]},
            "tests/helpers.py": {"summary": {"num_statements": 99, "covered_lines": 0,
                                             "num_branches": 9, "covered_branches": 0},
                                 "missing_lines": [1], "missing_branches": []},
        })))
        coverage = parse(raw, self.py_target)
        # tests/ is excluded; the totals are recomputed instead of trusting a blended summary.
        self.assertEqual(sorted(coverage["modules"]), ["util"])
        self.assertEqual((coverage["line_pct"], coverage["branch_pct"]), (66.67, 50.0))
        self.assertEqual((coverage["tool"], coverage["format"], coverage["status"]),
                         ("coverage.py", "coverage-json", "ok"))
        self.assertEqual(coverage["raw"], ["../coverage.json"])
        # 3-4 collapses into one contiguous range attributed to alpha; the arc keeps its own form.
        self.assertEqual([(entry["symbol"], entry["kind"], entry["lines"]) for entry in coverage["uncovered"]],
                         [("alpha", "branch", "2->3"), ("alpha", "line", "3-4")])
        self.assertEqual(coverage["modules"]["util"],
                         {"line_pct": 66.67, "branch_pct": 50.0, "uncovered_total": 2})

    def test_lcov_and_json_yield_the_same_result(self):
        lcov = SCRATCH / "coverage.lcov"
        write(lcov, "\n".join([
            "SF:pkg/util.py",
            "DA:1,1", "DA:2,1", "DA:3,0", "DA:4,0", "DA:7,1", "DA:8,1",
            "LF:6", "LH:4",
            "FN:1,4,alpha", "FNDA:1,alpha",
            "FN:7,8,beta", "FNDA:1,beta",
            "FNF:2", "FNH:2",
            "BRDA:2,0,jump to line 3,0",
            "BRDA:2,0,jump to line 4,1",
            "BRF:2", "BRH:1",
            "end_of_record",
        ]) + "\n")
        coverage = parse(lcov, self.py_target)
        self.assertEqual((coverage["format"], coverage["line_pct"], coverage["branch_pct"]),
                         ("lcov", 66.67, 50.0))
        self.assertEqual([(entry["symbol"], entry["kind"], entry["lines"]) for entry in coverage["uncovered"]],
                         [("alpha", "branch", "2->3"), ("alpha", "line", "3-4")])

    def test_go_coverprofile_maps_import_paths_and_has_no_branch_data(self):
        raw = SCRATCH / "unit.out"
        write(raw, "mode: set\n"
                   "example.com/gosample/calc/calc.go:3.20,5.2 2 1\n"
                   "example.com/gosample/calc/calc.go:7.20,9.2 3 0\n")
        coverage = parse(raw, self.go_target)
        self.assertEqual((coverage["format"], coverage["status"]), ("go-coverprofile", "ok"))
        self.assertEqual(coverage["line_pct"], 40.0)
        self.assertEqual(coverage["branch_pct"], "N/A")
        self.assertEqual(coverage["tool"], "go test -coverprofile")
        self.assertEqual([(entry["symbol"], entry["kind"], entry["lines"]) for entry in coverage["uncovered"]],
                         [("Sub", "block", "7-9")])
        self.assertEqual(coverage["modules"]["calc"]["uncovered_total"], 1)

    def test_per_module_cap_keeps_fifty_and_counts_the_rest(self):
        raw = SCRATCH / "cap.json"
        missing = list(range(10, 130, 2))  # 60 non-contiguous lines -> 60 entries
        write(raw, json.dumps(self.coverage_json({
            "pkg/big.py": {"summary": {"num_statements": 200, "covered_lines": 140,
                                       "num_branches": 0, "covered_branches": 0},
                           "missing_lines": missing, "missing_branches": []}})))
        coverage = parse(raw, self.py_target)
        self.assertEqual(len(coverage["uncovered"]), 50)
        self.assertEqual(coverage["uncovered_omitted"], {"big": 10})
        self.assertEqual(coverage["modules"]["big"]["uncovered_total"], 60)
        self.assertEqual(coverage["branch_pct"], "N/A")

    def test_nothing_measurable_is_unavailable_not_zero(self):
        raw = SCRATCH / "empty.json"
        write(raw, json.dumps(self.coverage_json({
            "tests/helpers.py": {"summary": {"num_statements": 9, "covered_lines": 1,
                                             "num_branches": 0, "covered_branches": 0},
                                 "missing_lines": [], "missing_branches": []}})))
        coverage = parse(raw, self.py_target)
        self.assertEqual(coverage["status"], "unavailable")
        self.assertTrue(coverage["reason"])
        self.assertEqual((coverage["line_pct"], coverage["branch_pct"]), ("N/A", "N/A"))
        self.assertEqual((coverage["modules"], coverage["uncovered"]), ({}, []))

    def test_unsupported_or_unreadable_input_exits_2(self):
        for path in (ROOT / "README.md", SCRATCH / "missing.json"):
            with self.subTest(path=path.name):
                proc = run_coverage(path, self.py_target)
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(proc.stdout.strip(), "")
                self.assertTrue(proc.stderr.strip())
        proc = subprocess.run([sys.executable, "-B", str(VERIFY), "--coverage", str(ROOT / "README.md"),
                               "--scope", "run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True, check=False)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--coverage", proc.stderr)


class TestGoldenCoverage(unittest.TestCase):
    """The committed golden coverage is real, honest and consistent with the reports."""

    def test_python_sample_coverage(self):
        coverage = json.loads(read(PY_SAMPLE / "tests/.state/last_run.json"))["unit"]["coverage"]
        self.assertEqual((coverage["status"], coverage["format"], coverage["tool"]),
                         ("ok", "coverage-json", "coverage.py"))
        self.assertEqual((coverage["line_pct"], coverage["branch_pct"]), (76.92, 60.0))
        self.assertEqual(coverage["modules"]["wordcount"]["line_pct"], 57.14)
        self.assertEqual(coverage["modules"]["slugify"]["line_pct"], 100.0)
        self.assertEqual(len(coverage["uncovered"]), 6)
        self.assertEqual({entry["module"] for entry in coverage["uncovered"]}, {"wordcount"})
        self.assertIn("count_words", {entry["symbol"] for entry in coverage["uncovered"]})

    def test_go_sample_coverage(self):
        coverage = json.loads(read(GO_SAMPLE / "tests/.state/last_run.json"))["unit"]["coverage"]
        self.assertEqual((coverage["status"], coverage["format"], coverage["tool"]),
                         ("ok", "go-coverprofile", "go test -coverprofile"))
        self.assertEqual(coverage["line_pct"], 100.0)
        self.assertEqual(coverage["branch_pct"], "N/A")
        self.assertEqual(coverage["uncovered"], [])
        self.assertEqual(sorted(coverage["modules"]), ["calc", "textutil"])

    def test_reports_carry_the_coverage_columns_and_section(self):
        unit_report = read(PY_SAMPLE / "tests/docs/reports/u_report_latest.md")
        header = next(line for line in unit_report.splitlines() if line.startswith("| 总用例数"))
        self.assertIn("行覆盖率", header)
        self.assertIn("分支覆盖率", header)
        self.assertIn("76.92%", unit_report)
        self.assertIn("## 4. 未覆盖符号", unit_report)
        all_report = read(PY_SAMPLE / "tests/docs/reports/all_report_latest.md")
        self.assertIn("| 行覆盖率 |", all_report)
        go_report = read(GO_SAMPLE / "tests/docs/reports/u_report_latest.md")
        self.assertIn("| N/A |", go_report)
        self.assertIn("## 4. 未覆盖符号", go_report)


# name -> the diagnostic code an injected violation must yield
EXPECTED = {
    "coverage-field-missing": "COVERAGE_FIELD_MISSING",
    "coverage-field-invalid": "COVERAGE_FIELD_INVALID",
    "cap-exceeded": "COVERAGE_UNCOVERED_OVER_CAP",
    "unavailable-without-reason": "COVERAGE_UNAVAILABLE_WITHOUT_REASON",
    "value-without-evidence": "COVERAGE_VALUE_WITHOUT_EVIDENCE",
    "raw-mismatch": "COVERAGE_RAW_MISMATCH",
    "report-mismatch": "COVERAGE_REPORT_MISMATCH",
    "report-section-missing": "COVERAGE_REPORT_MISMATCH",
    "report-column-missing": "COVERAGE_REPORT_MISMATCH",
}


def edit_last_run(root, mutate):
    path = root / "tests/.state/last_run.json"
    data = json.loads(read(path))
    mutate(data["unit"])
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


class TestCoverageChecks(unittest.TestCase):
    """Each coverage rule fires on an injected violation, on scratch copies that keep the raw files."""

    # A coverage.py export that reproduces the committed python-sample coverage exactly:
    # lines 20/26 = 76.92%, branches 6/10 = 60.0%, the same six uncovered entries.
    # It is written into every copy, so the checks behave the same in a fresh checkout,
    # where tests/tmp/ (git-ignored) does not exist.
    RAW_FIXTURE = {
        "meta": {"format": 3, "version": "tests", "branch_coverage": True},
        "totals": {},
        "files": {
            "textkit/wordcount.py": {"summary": {"num_statements": 14, "covered_lines": 8,
                                                 "num_branches": 6, "covered_branches": 2},
                                     "missing_lines": [11, 22, 23, 24, 25, 26],
                                     "missing_branches": [[10, 11], [20, 22], [23, 24], [23, 25]]},
            "textkit/slugify.py": {"summary": {"num_statements": 9, "covered_lines": 9,
                                               "num_branches": 4, "covered_branches": 4},
                                   "missing_lines": [], "missing_branches": []},
            "textkit/__init__.py": {"summary": {"num_statements": 3, "covered_lines": 3,
                                                "num_branches": 0, "covered_branches": 0},
                                    "missing_lines": [], "missing_branches": []},
        },
    }

    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(shutil.rmtree, SCRATCH / "checks", True)
        shutil.rmtree(SCRATCH / "checks", ignore_errors=True)
        cls.base = SCRATCH / "checks" / "base"
        shutil.copytree(PY_SAMPLE, cls.base, ignore=shutil.ignore_patterns("tmp"))
        write(cls.base / "tests/tmp/coverage/coverage.json",
              json.dumps(cls.RAW_FIXTURE, ensure_ascii=False, indent=2) + "\n")

    def copy(self, name):
        target = SCRATCH / "checks" / name
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(self.base, target)
        return target

    def assert_fires(self, target, code):
        proc = run_verify(target, "--scope", "run", "--json")
        self.assertEqual(proc.returncode, 4, proc.stdout)
        self.assertIn(code, codes_by_severity(proc)["ERROR"], proc.stdout)

    def test_baseline_copy_is_clean(self):
        self.assertEqual(run_verify(self.copy("baseline"), "--scope", "run").returncode, 0)

    def test_injected_violations_are_detected(self):
        mutations = {
            "coverage-field-missing": lambda unit: unit.pop("coverage"),
            "coverage-field-invalid": lambda unit: unit["coverage"].update(line_pct=150),
            "cap-exceeded": lambda unit: unit["coverage"].update(
                uncovered=[{"module": "wordcount", "file": "textkit/wordcount.py", "symbol": "f",
                            "kind": "line", "lines": str(n)} for n in range(51)],
                uncovered_omitted={},
                modules={"wordcount": {"line_pct": 10.0, "branch_pct": "N/A", "uncovered_total": 51}}),
            "unavailable-without-reason": lambda unit: unit["coverage"].update(
                status="unavailable", reason="", line_pct="N/A", branch_pct="N/A",
                raw=[], modules={}, uncovered=[], uncovered_omitted={}),
            "value-without-evidence": lambda unit: unit["coverage"].update(
                status="unavailable", reason="coverage.py 未安装", line_pct=0, branch_pct=0),
            "raw-mismatch": lambda unit: unit["coverage"].update(line_pct=80.0),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                target = self.copy(name)
                edit_last_run(target, mutate)
                self.assert_fires(target, EXPECTED[name])

    def test_report_violations_are_detected(self):
        cases = {
            "report-mismatch": ("76.92%", "90%"),
            "report-section-missing": ("## 4. 未覆盖符号", "## 4. 覆盖"),
            "report-column-missing": ("| 行覆盖率 | 分支覆盖率 |", ""),
        }
        for name, (old, new) in cases.items():
            with self.subTest(mutation=name):
                target = self.copy(name)
                for candidate in ("u_report_latest.md", "all_report_latest.md"):
                    path = target / "tests/docs/reports" / candidate
                    text = read(path)
                    if old in text:
                        write(path, text.replace(old, new, 1))
                self.assert_fires(target, EXPECTED[name])


class TestCoverageWorkflowContract(unittest.TestCase):
    """The rules are stated where they belong: invariant, stage actions, references, templates, SKILL."""

    def test_invariant_is_declared_as_fatal(self):
        workflow = read(ROOT / "workflow.yaml")
        block = workflow.split('id: "INV_COVERAGE_HONEST_AND_PASSIVE"', 1)[1].split("- id:", 1)[0]
        self.assertIn('severity: "FATAL"', block)
        for phrase in ("same unit test run", "coverage is never collected for benchmarks",
                       "re-run the plain unit command once", "Never install a coverage tool",
                       "never 0", "no threshold", "never changes a track status"):
            self.assertIn(phrase, block)

    def test_run_stages_collect_parse_and_render_coverage(self):
        workflow = read(ROOT / "workflow.yaml")
        stage2 = workflow.split('id: "RUN_STAGE_2_EXECUTE"', 1)[1].split('id: "RUN_STAGE_3', 1)[0]
        stage3 = workflow.split('id: "RUN_STAGE_3_REPORT_AND_STATE"', 1)[1]
        self.assertIn("inside that same unit test run", stage2)
        self.assertIn("Coverage itself never triggers a second test run", stage2)
        self.assertIn("re-run the plain unit command once", stage2)
        self.assertIn("never install it", stage2)
        self.assertIn("scripts/ta-verify --coverage <raw_file>", stage3)
        self.assertIn("verbatim into 'unit.coverage'", stage3)
        self.assertIn("An unmeasured value is N/A, never 0", stage3)
        self.assertIn("never changes a track status", stage3)

    def test_references_own_the_coverage_rules(self):
        runner = read(ROOT / "references/runner-and-reporting.md")
        section = runner.split("## 5. Coverage Collection and Reporting", 1)[1]
        for phrase in ("inside the same run", "Never install a coverage tool",
                       "ta-verify --target <target_root> --coverage <raw file>",
                       "No thresholds and no re-judging", "Never write `0`"):
            self.assertIn(phrase, section)
        state = read(ROOT / "references/state-and-backup.md")
        self.assertIn("- `unit.coverage`: coverage of the unit track", state)
        artifact = read(ROOT / "references/artifact-verification.md")
        self.assertIn("## 8. Coverage Parsing (`--coverage`)", artifact)
        self.assertIn("| Coverage | `unit.coverage` follows the protocol", artifact)

    def test_templates_carry_the_coverage_fields(self):
        template = json.loads(read(ROOT / "templates/state/last_run.json.tpl"))
        coverage = template["unit"]["coverage"]
        for key in ("status", "reason", "tool", "format", "line_pct", "branch_pct", "raw",
                    "modules", "uncovered", "uncovered_omitted"):
            self.assertIn(key, coverage)
        unit_tpl = read(ROOT / "templates/docs/u_report.md.tpl")
        self.assertIn("| 行覆盖率 | 分支覆盖率 |", unit_tpl)
        self.assertIn("## 4. 未覆盖符号", unit_tpl)
        all_tpl = read(ROOT / "templates/docs/all_report.md.tpl")
        self.assertIn("| 行覆盖率 |", all_tpl.split("## 2.", 1)[1].split("## 3.", 1)[0])

    def test_skill_states_the_coverage_principle(self):
        skill = read(ROOT / "SKILL.md")
        self.assertIn("8. **Coverage is reported, never gamed.**", skill)
        for phrase in ("never triggers a second test run", "re-run the plain unit command once",
                       "Never install a coverage tool", "never `0`", "no threshold"):
            self.assertIn(phrase, skill)


@unittest.skipUnless(importlib.util.find_spec("coverage"), "coverage.py 未安装，跳过真实采集对照")
class TestRealPythonCoverage(unittest.TestCase):
    """With coverage.py available, a real same-run collection parses to the same figures."""

    def test_same_run_collection_parses(self):
        self.addCleanup(shutil.rmtree, SCRATCH / "real-py", True)
        target = SCRATCH / "real-py"
        shutil.copytree(PY_SAMPLE, target, ignore=shutil.ignore_patterns("tmp"))
        (target / "tests/tmp/coverage").mkdir(parents=True)
        command = ('{python} -B -m coverage run --branch --source=textkit '
                   '--data-file=tests/tmp/coverage/.coverage -m pytest tests/unit '
                   '-o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache -q').format(
                       python=sys.executable)
        run = subprocess.run(command, shell=True, cwd=str(target), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True, check=False)
        # pytest may be unavailable in a minimal environment; the test then says so rather than failing.
        if "No module named" in run.stdout:
            self.skipTest("pytest 不可用: %s" % run.stdout.strip().splitlines()[-1])
        self.assertEqual(run.returncode, 0, run.stdout)
        export = subprocess.run(
            "%s -B -m coverage json --data-file=tests/tmp/coverage/.coverage "
            "-o tests/tmp/coverage/coverage.json" % sys.executable,
            shell=True, cwd=str(target), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, check=False)
        self.assertEqual(export.returncode, 0, export.stdout)
        coverage = parse(target / "tests/tmp/coverage/coverage.json", target)
        self.assertEqual((coverage["status"], coverage["format"]), ("ok", "coverage-json"))
        self.assertEqual(sorted(coverage["modules"]), ["slugify", "textkit", "wordcount"])
        self.assertLess(coverage["modules"]["wordcount"]["line_pct"], 100.0)
        self.assertTrue(coverage["uncovered"])


@unittest.skipUnless(tool_available("go"), "go 未安装，跳过真实采集对照")
class TestRealGoCoverage(unittest.TestCase):
    """With Go available, a real -coverprofile parses to statement coverage with N/A branches."""

    def test_same_run_collection_parses(self):
        self.addCleanup(shutil.rmtree, SCRATCH / "real-go", True)
        target = SCRATCH / "real-go"
        shutil.copytree(GO_SAMPLE, target, ignore=shutil.ignore_patterns("tmp"))
        (target / "tests/tmp/coverage").mkdir(parents=True)
        command = ("GOCACHE=$(pwd)/tests/tmp/go-build GOTMPDIR=$(pwd)/tests/tmp "
                   "go test ./tests/unit -count=1 -coverprofile=tests/tmp/coverage/unit.out -coverpkg=./...")
        run = subprocess.run(command, shell=True, cwd=str(target), stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True, check=False)
        self.assertEqual(run.returncode, 0, run.stdout)
        coverage = parse(target / "tests/tmp/coverage/unit.out", target)
        self.assertEqual((coverage["format"], coverage["branch_pct"]), ("go-coverprofile", "N/A"))
        self.assertGreater(coverage["line_pct"], 0)
        self.assertEqual(sorted(coverage["modules"]), ["calc", "textutil"])


if __name__ == "__main__":
    unittest.main()
