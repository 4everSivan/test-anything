#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Behavioral contract of scripts/ta-verify and the examples/ regression baseline."""

import ast
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERIFY = ROOT / "scripts" / "ta-verify"
NEGATIVE = ROOT / "examples" / "negative"
GOLDEN = {name: ROOT / "examples" / name for name in ("python-sample", "go-sample")}
SCOPES = ("create", "run", "all")
SEVERITIES = ("ERROR", "WARNING", "ADVISORY")
# Tests only ever write inside this git-ignored scratch area (AGENTS.md section 3).
SCRATCH = ROOT / "local" / "tmp" / "ta-verify-tests"

# Violations the T02 card requires as committed samples: directory name -> diagnostic code.
REQUIRED_NEGATIVES = {
    "missing-case-anchor": "CODE_FUNCTION_WITHOUT_ANCHOR",
    "manifest-field-missing": "MANIFEST_FIELD_MISSING",
    "manifest-structure-invalid": "MANIFEST_MODULE_INVALID",
    "wrong-track-prefix": "DOC_TRACK_PREFIX_INVALID",
    "orphan-case": "CASE_WITHOUT_TEST_CODE",
    "hash-mismatch": "MANIFEST_HASH_MISMATCH",
}


# ---- small file helpers ----
def read(path):
    return path.read_text(encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(path, old, new):
    text = read(path)
    if old not in text:
        raise AssertionError("%s does not contain %r" % (path.name, old))
    write(path, text.replace(old, new, 1))


def replace_in_line(path, line_marker, old, new):
    """Replace old with new on the first line that starts with line_marker."""
    for line in read(path).splitlines():
        if line.startswith(line_marker):
            replace_once(path, line, line.replace(old, new))
            return
    raise AssertionError("%s has no line starting with %r" % (path.name, line_marker))


def drop_anchored_function(path, case_id):
    """Remove the test function bound to case_id together with its anchor comments."""
    lines = read(path).splitlines(True)
    anchor = next(i for i, line in enumerate(lines) if line.strip() == "# @case: %s" % case_id)
    end = anchor
    while end + 1 < len(lines) and lines[end + 1].strip():
        end += 1
    write(path, "".join(lines[:anchor] + lines[end + 1:]))


def drop_card(path, case_id):
    """Remove the H3 specification card of case_id, up to the next H3 heading."""
    text = read(path)
    start = text.index("### %s:" % case_id)
    write(path, text[:start] + text[text.index("### ", start + 1):])


def drop_line_containing(path, needle):
    write(path, "".join(line for line in read(path).splitlines(True) if needle not in line))


# ---- running the verifier ----
def run_raw(*args):
    """Run ta-verify as a subprocess, the way the skill workflow invokes it."""
    return subprocess.run([sys.executable, "-B", str(VERIFY), *args], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True, check=False)


def run_verify(target, *flags):
    return run_raw("--target", str(target), *flags)


def codes_by_severity(proc):
    """{severity: set(codes)} taken from the JSON summary."""
    found = {severity: set() for severity in SEVERITIES}
    for code, levels in json.loads(proc.stdout)["summary"]["codes"].items():
        for severity in levels:
            found[severity].add(code)
    return found


def snapshot(root):
    """(size, mtime_ns, sha256) of every file under root; tests/tmp is runtime scratch."""
    state = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts[:2] == ("tests", "tmp") or not path.is_file():
            continue
        state[str(rel)] = (path.stat().st_size, path.stat().st_mtime_ns,
                           hashlib.sha256(path.read_bytes()).hexdigest())
    return state


def load_verifier_module():
    """Import scripts/ta-verify in-process without leaving bytecode in the tree."""
    loader = importlib.machinery.SourceFileLoader("ta_verify", str(VERIFY))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader("ta_verify", loader))
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def imported_modules():
    tree = ast.parse(read(VERIFY), str(VERIFY))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module.split(".")[0])
    return names


def is_stdlib(name):
    # Python 3.8 reports no origin for built-in modules such as sys; 3.9+ says "built-in".
    if name in sys.builtin_module_names:
        return True
    spec = importlib.util.find_spec(name)
    origin = spec.origin if spec else None
    if origin in ("built-in", "frozen"):
        return True
    stdlib = sysconfig.get_paths()["stdlib"]
    return bool(origin) and "site-packages" not in origin and origin.startswith(stdlib)


def heading_exists(text, section):
    """True when `section` is a Markdown heading in `text` (exact text, any level)."""
    return any(line.lstrip("#").strip() == section
               for line in text.splitlines() if line.startswith("#"))


class TestVerifierContract(unittest.TestCase):
    """CLI shape, exit codes, output formats and the read-only boundary."""

    def test_single_file_stdlib_script_with_python_shebang(self):
        self.assertEqual([p.name for p in (ROOT / "scripts").glob("ta*verify*")], ["ta-verify"],
                         "the verifier must stay a single file next to the governance tooling")
        self.assertTrue(os.access(str(VERIFY), os.X_OK), "scripts/ta-verify must be executable")
        self.assertTrue(read(VERIFY).startswith("#!/usr/bin/env python3\n"))
        modules = imported_modules()
        self.assertTrue(modules, "the verifier must declare its imports")
        for name in sorted(modules):
            self.assertTrue(is_stdlib(name), "scripts/ta-verify imports non-stdlib module %s" % name)

    def test_usage_errors_and_unreadable_targets_exit_2(self):
        for args in (["--scope", "nope"], ["--target", str(ROOT / "no-such-dir")],
                     ["--target", str(ROOT / "README.md")]):
            with self.subTest(args=args):
                proc = run_raw(*args)
                self.assertEqual(proc.returncode, 2)
                self.assertTrue(proc.stderr.strip(), "exit 2 must explain the problem")
                self.assertEqual(proc.stdout.strip(), "", "exit 2 must not print findings or a receipt")

    def test_exit_codes_are_0_pass_and_4_violation_in_every_output_mode(self):
        cases = [(GOLDEN["python-sample"], "all", 0), (GOLDEN["go-sample"], "all", 0),
                 (NEGATIVE / "orphan-case", "create", 4)]
        for target, scope, expected in cases:
            for flags in ((), ("--json",), ("--receipt",), ("--json", "--receipt")):
                with self.subTest(sample=target.name, flags=flags):
                    self.assertEqual(run_verify(target, "--scope", scope, *flags).returncode, expected)

    def test_json_output_shape(self):
        proc = run_verify(NEGATIVE / "hash-mismatch", "--scope", "create", "--json")
        payload = json.loads(proc.stdout)
        self.assertEqual(sorted(payload),
                         ["exit_code", "findings", "scope", "summary", "target", "tool", "version"])
        self.assertEqual((payload["tool"], payload["exit_code"], payload["scope"]),
                         ("ta-verify", 0, "create"))
        self.assertEqual(sorted(payload["summary"]), ["advisories", "codes", "errors", "warnings"])
        self.assertEqual(payload["summary"]["codes"]["MANIFEST_HASH_MISMATCH"], {"WARNING": 1})
        self.assertTrue(payload["findings"])
        for finding in payload["findings"]:
            self.assertEqual(sorted(finding), ["basis", "code", "group", "hint", "line",
                                               "message", "path", "severity"])
            self.assertTrue(finding["hint"], "every finding carries a fix hint")

    def test_receipt_reports_the_verification_in_a_fixed_format(self):
        version = load_verifier_module().VERSION
        passed = run_verify(GOLDEN["go-sample"], "--scope", "all", "--receipt").stdout.splitlines()
        self.assertTrue(passed[0].startswith("### ta-verify · "), passed[0])
        self.assertEqual(passed[1],
                         "工具 ta-verify v%s · 范围 create + run · 目标只读" % version)
        self.assertEqual([line.split("：", 1)[0] for line in passed if line.startswith("- ")],
                         ["- 门禁", "- 校验项", "- 问题", "- 处置"])
        # ADVISORY 数量随环境变化：干净检出里被忽略的 tests/tmp/ 不存在，本地跑过样例后则存在。
        self.assertRegex(passed[3], r"^- 门禁：Exit 0 · ERROR 0 · WARNING 0 · ADVISORY \d+$")
        self.assertIn("run 侧可将本结果写入运行小结", passed[-1])

        failed = run_verify(NEGATIVE / "orphan-case", "--scope", "create", "--receipt").stdout
        self.assertIn("代码锚点 ✗", failed)
        self.assertIn("ERROR CASE_WITHOUT_TEST_CODE", failed)
        self.assertIn("保持 create_status: in_progress", failed)
        self.assertNotIn("问题明细见 --json", "\n".join(passed))

    def test_verifier_never_writes_into_the_target(self):
        for target in list(GOLDEN.values()) + [NEGATIVE / "orphan-case"]:
            before = snapshot(target)
            for scope in SCOPES:
                run_verify(target, "--scope", scope)
                run_verify(target, "--scope", scope, "--json", "--receipt")
            self.assertEqual(snapshot(target), before, "ta-verify modified %s" % target.name)


class TestRuleProvenance(unittest.TestCase):
    """Every diagnostic code names the references/ clause it is based on, and that clause still exists."""

    def test_every_code_traces_to_a_live_clause(self):
        checks = load_verifier_module().CHECKS
        self.assertGreaterEqual(len(checks), 40)
        for code, (severity, _, hint, reference, section) in sorted(checks.items()):
            with self.subTest(code=code):
                self.assertIn(severity, SEVERITIES)
                self.assertTrue(hint, "%s has no fix hint" % code)
                path = ROOT / reference
                self.assertTrue(path.is_file(), "%s cites a missing reference %s" % (code, reference))
                self.assertTrue(heading_exists(read(path), section),
                                "%s relies on a clause that was renamed or removed: %s#%s"
                                % (code, reference, section))

    def test_provenance_check_notices_a_renamed_clause(self):
        _, _, _, reference, section = load_verifier_module().CHECKS["MANIFEST_FIELD_MISSING"]
        text = read(ROOT / reference)
        self.assertTrue(heading_exists(text, section))
        self.assertFalse(heading_exists(text.replace(section, section + " (renamed)"), section))
        self.assertFalse(heading_exists("", section))

    def test_unregistered_codes_cannot_be_emitted(self):
        module = load_verifier_module()
        ctx = module.Ctx(module.Target(str(GOLDEN["python-sample"])), "all")
        with self.assertRaises(KeyError):
            ctx.add("NOT_A_REGISTERED_CODE", "tests", "must never be emitted")


class TestGoldenSamples(unittest.TestCase):
    """The committed create / run artifacts of both sample projects pass every scope."""

    def test_golden_samples_pass_every_scope(self):
        for name, target in sorted(GOLDEN.items()):
            for scope in SCOPES:
                with self.subTest(sample=name, scope=scope):
                    proc = run_verify(target, "--scope", scope, "--json")
                    self.assertEqual(proc.returncode, 0, proc.stdout)
                    summary = json.loads(proc.stdout)["summary"]
                    self.assertEqual((summary["errors"], summary["warnings"]), (0, 0))

    def test_run_scope_does_not_depend_on_create_checks(self):
        # Regression: run-only scope once reported every report case as unknown, because the
        # case index was only built while the create checks were running.
        for name, target in sorted(GOLDEN.items()):
            self.assertEqual(codes_by_severity(run_verify(target, "--scope", "run", "--json"))["ERROR"],
                             set(), name)

    def test_golden_reports_share_the_recorded_run_id(self):
        for name, target in sorted(GOLDEN.items()):
            last_run = json.loads(read(target / "tests/.state/last_run.json"))
            self.assertEqual((last_run["scope"], last_run["unit"]["status"],
                              last_run["benchmark"]["status"]), ("all", "passed", "completed"))
            for report in ("u_report_latest.md", "b_report_latest.md", "all_report_latest.md"):
                self.assertIn("**run_id**: %s" % last_run["run_id"],
                              read(target / "tests/docs/reports" / report), "%s/%s" % (name, report))


class TestNegativeSamples(unittest.TestCase):
    """Each committed negative sample yields exactly the outcome recorded in expected.json."""

    @staticmethod
    def sample_dirs():
        return sorted(p for p in NEGATIVE.iterdir() if (p / "expected.json").is_file())

    def test_card_required_violations_are_covered(self):
        found = {p.name: tuple(json.loads(read(p / "expected.json"))["codes"])
                 for p in self.sample_dirs()}
        for name, code in REQUIRED_NEGATIVES.items():
            self.assertIn(name, found, "missing negative sample %s" % name)
            self.assertEqual(found[name], (code,), name)

    def test_samples_hit_their_expected_exit_code_and_codes(self):
        samples = self.sample_dirs()
        self.assertGreaterEqual(len(samples), len(REQUIRED_NEGATIVES))
        for sample in samples:
            expected = json.loads(read(sample / "expected.json"))
            with self.subTest(sample=sample.name):
                self.assertTrue(expected["description"])
                proc = run_verify(sample, "--scope", expected["scope"], "--json")
                self.assertEqual(proc.returncode, expected["exit_code"], proc.stdout)
                codes = codes_by_severity(proc)
                if expected["exit_code"] == 4:
                    self.assertEqual(codes["ERROR"], set(expected["codes"]))
                else:
                    self.assertEqual(codes["ERROR"], set(), "a warning sample must not be blocked")
                    self.assertEqual(codes["WARNING"], set(expected["codes"]))

    def test_readme_table_matches_the_samples(self):
        table = {}
        for line in read(NEGATIVE / "README.md").splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 4 and cells[0].startswith("[`"):
                table[cells[0].split("`")[1].rstrip("/")] = (int(cells[2].strip("`")),
                                                             cells[3].split("`")[1])
        self.assertEqual(sorted(table), [p.name for p in self.sample_dirs()])
        for sample in self.sample_dirs():
            expected = json.loads(read(sample / "expected.json"))
            self.assertEqual(table[sample.name], (expected["exit_code"], expected["codes"][0]),
                             sample.name)


# ---- injected violations on scratch copies ----
T = "tests"
UNIT = T + "/unit/u_wordcount_test.py"
MANIFEST = T + "/.state/manifest.json"
LAST_RUN = T + "/.state/last_run.json"
PLAN = T + "/docs/plans/wordcount_plan.md"
CASES = T + "/docs/cases/u_wordcount_cases.md"
REPORTS = T + "/docs/reports"


def edit_json(root, rel, mutate):
    data = json.loads(read(root / rel))
    mutate(data)
    write(root / rel, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def set_last_run(root, **changes):
    """Update last_run.json: a dict value updates that track summary, any other value that top-level key."""
    def mutate(data):
        for key, value in changes.items():
            if isinstance(value, dict):
                data[key].update(value)
            else:
                data[key] = value
    edit_json(root, LAST_RUN, mutate)


def drop_last_run_field(root, track, field):
    edit_json(root, LAST_RUN, lambda data: data[track].pop(field))


def stale_benchmark_report(root):
    """Give the benchmark report a run_id other than the one recorded in last_run.json."""
    recorded = json.loads(read(root / LAST_RUN))["run_id"]
    replace_once(root / REPORTS / "b_report_latest.md", "**run_id**: %s" % recorded,
                 "**run_id**: 20200101_000000")


def without_optional_dirs(root):
    def no_fixtures(manifest):
        for module in manifest["modules"].values():
            module["fixtures"] = None
    edit_json(root, MANIFEST, no_fixtures)
    shutil.rmtree(root / T / "fixtures")
    shutil.rmtree(root / T / "tmp", ignore_errors=True)


# (name, scope, exit code, severity, expected code, mutation applied to a copy of python-sample)
MUTATIONS = [
    ("anchor-removed", "create", 4, "ERROR", "CODE_FUNCTION_WITHOUT_ANCHOR",
     lambda r: replace_once(r / UNIT, "# @case: UT-wordcount-001\n", "")),
    ("orphan-case", "create", 4, "ERROR", "CASE_WITHOUT_TEST_CODE",
     lambda r: drop_anchored_function(r / UNIT, "UT-wordcount-001")),
    ("anchor-unknown", "create", 4, "ERROR", "CODE_CASE_ANCHOR_UNKNOWN",
     lambda r: replace_once(r / UNIT, "@case: UT-wordcount-001", "@case: UT-wordcount-999")),
    ("anchor-misplaced", "create", 4, "ERROR", "CODE_CASE_ANCHOR_MISPLACED",
     lambda r: replace_once(r / UNIT, "@case: UT-wordcount-001", "@case: UT-slugify-001")),
    ("anchor-duplicate", "create", 4, "ERROR", "CODE_CASE_ANCHOR_DUPLICATE",
     lambda r: replace_once(r / UNIT, "@case: UT-wordcount-002", "@case: UT-wordcount-001")),
    ("feature-unknown", "create", 4, "ERROR", "CODE_FEATURE_ANCHOR_UNKNOWN",
     lambda r: replace_once(r / UNIT, "@feature: FP-wordcount-01", "@feature: FP-wordcount-99")),
    ("doc-not-snake-case", "create", 4, "ERROR", "DOC_FILENAME_NOT_SNAKE_CASE",
     lambda r: (r / T / "docs/drafts/slugify_draft.md").rename(r / T / "docs/drafts/Slugify Draft.md")),
    ("doc-misplaced", "create", 4, "ERROR", "DOC_FILE_MISPLACED",
     lambda r: (r / T / "docs/cases/b_slugify_cases.md").rename(r / T / "docs/plans/b_slugify_cases.md")),
    ("docs-nested-dir", "create", 4, "ERROR", "DOCS_NESTED_DIR",
     lambda r: (r / T / "docs/cases/unit").mkdir()),
    ("unit-file-name", "create", 4, "ERROR", "UNIT_FILE_NAME_INVALID",
     lambda r: write(r / T / "unit/helpers.py", "def helper():\n    return 1\n")),
    ("bench-file-name", "create", 4, "ERROR", "BENCH_FILE_NAME_INVALID",
     lambda r: write(r / T / "benchmark/slugify_bench.py", "# stray file\n")),
    ("subdir-missing", "create", 4, "ERROR", "TESTS_SUBDIR_MISSING",
     lambda r: shutil.rmtree(r / T / "benchmark")),
    ("tests-dir-missing", "all", 4, "ERROR", "TESTS_DIR_MISSING",
     lambda r: shutil.rmtree(r / T)),
    ("manifest-field-missing", "create", 4, "ERROR", "MANIFEST_FIELD_MISSING",
     lambda r: edit_json(r, MANIFEST, lambda m: m.pop("stack"))),
    ("manifest-bad-type", "create", 4, "ERROR", "MANIFEST_FIELD_INVALID",
     lambda r: edit_json(r, MANIFEST, lambda m: m.update(modules=[]))),
    ("manifest-invalid-json", "create", 4, "ERROR", "MANIFEST_INVALID_JSON",
     lambda r: write(r / MANIFEST, "{ not json")),
    ("manifest-absent", "create", 4, "ERROR", "MANIFEST_MISSING",
     lambda r: (r / MANIFEST).unlink()),
    ("manifest-module-unregistered", "create", 4, "ERROR", "MANIFEST_MODULE_UNREGISTERED",
     lambda r: edit_json(r, MANIFEST, lambda m: m["modules"].pop("slugify"))),
    ("manifest-case-ids", "create", 4, "ERROR", "MANIFEST_CASE_IDS_MISMATCH",
     lambda r: edit_json(r, MANIFEST, lambda m: m["modules"]["wordcount"]["unit_code"].update(
         case_ids=["UT-wordcount-001"]))),
    ("manifest-file-missing", "create", 4, "ERROR", "MANIFEST_FILE_MISSING",
     lambda r: (r / T / "benchmark/b_wordcount_bench.py").unlink()),
    ("plan-missing", "create", 4, "ERROR", "MODULE_PLAN_MISSING",
     lambda r: (r / PLAN).unlink()),
    ("not-in-matrix", "create", 4, "ERROR", "CASE_NOT_IN_PLAN_MATRIX",
     lambda r: drop_line_containing(r / PLAN, "`UT-wordcount-002`")),
    ("matrix-row-mismatch", "create", 4, "ERROR", "CASE_PLAN_ROW_MISMATCH",
     lambda r: replace_in_line(r / PLAN, "| `FP-wordcount-01` | `UT-wordcount-002`",
                               "`FP-wordcount-01`", "`FP-wordcount-02`")),
    ("matrix-without-spec", "create", 4, "ERROR", "PLAN_CASE_WITHOUT_SPEC",
     lambda r: replace_once(r / T / "docs/plans/slugify_plan.md", "`UT-slugify-004`",
                            "`UT-slugify-009`")),
    ("card-missing", "create", 4, "ERROR", "CASE_TABLE_CARD_MISMATCH",
     lambda r: drop_card(r / CASES, "UT-wordcount-002")),
    ("feature-missing", "create", 4, "ERROR", "CASE_FEATURE_MISSING",
     lambda r: replace_in_line(r / CASES, "| `UT-wordcount-001` |", "`FP-wordcount-01`", "—")),
    ("feature-unknown", "create", 4, "ERROR", "CASE_FEATURE_UNKNOWN",
     lambda r: replace_in_line(r / CASES, "| `UT-wordcount-001` |", "`FP-wordcount-01`",
                               "`FP-wordcount-77`")),
    ("case-id-duplicate", "create", 4, "ERROR", "CASE_ID_DUPLICATE",
     lambda r: replace_in_line(r / CASES, "| `UT-wordcount-002` |", "`UT-wordcount-002`",
                               "`UT-wordcount-001`")),
    ("case-module-mismatch", "create", 4, "ERROR", "CASE_MODULE_MISMATCH",
     lambda r: replace_in_line(r / CASES, "| `UT-wordcount-002` |", "`UT-wordcount-002`",
                               "`UT-slugify-002`")),
    ("case-id-invalid", "create", 4, "ERROR", "CASE_ID_INVALID",
     lambda r: replace_in_line(r / CASES, "| `UT-wordcount-002` |", "`UT-wordcount-002`",
                               "`UT-wordcount-02`")),
    # Malformed data must yield a diagnostic, never a crash of the verifier itself.
    ("lone-pipe-row-in-table", "create", 4, "ERROR", "CASE_ID_INVALID",
     lambda r: replace_once(r / CASES, "| `UT-wordcount-001` |", "|\n| `UT-wordcount-001` |")),
    ("optional-dirs-absent", "create", 0, "ADVISORY", "TESTS_OPTIONAL_DIR_MISSING", without_optional_dirs),
    ("report-status-mismatch", "run", 4, "ERROR", "REPORT_STATUS_MISMATCH",
     lambda r: set_last_run(r, unit={"status": "failed"})),
    ("passed-with-nonzero-exit", "run", 4, "ERROR", "LAST_RUN_STATUS_EVIDENCE_CONFLICT",
     lambda r: set_last_run(r, unit={"exit_code": 1})),
    ("passed-with-zero-cases", "run", 4, "ERROR", "LAST_RUN_STATUS_EVIDENCE_CONFLICT",
     lambda r: set_last_run(r, unit={"total": 0, "passed": 0})),
    ("scope-report-mismatch", "run", 4, "ERROR", "RUN_SCOPE_REPORT_MISMATCH",
     lambda r: set_last_run(r, scope="unittest")),
    ("stale-report-run-id", "run", 4, "ERROR", "RUN_SCOPE_REPORT_MISMATCH", stale_benchmark_report),
    ("report-header-broken", "run", 4, "ERROR", "REPORT_HEADER_INVALID",
     lambda r: replace_once(r / REPORTS / "all_report_latest.md", "｜ **status**: passed",
                            "｜ **status**: ok")),
    ("report-unknown-case", "run", 4, "ERROR", "REPORT_CASE_UNKNOWN",
     lambda r: replace_once(r / REPORTS / "u_report_latest.md", "| `UT-wordcount-003` |",
                            "| `UT-wordcount-099` |")),
    ("last-run-field-missing", "run", 4, "ERROR", "LAST_RUN_FIELD_MISSING",
     lambda r: drop_last_run_field(r, "benchmark", "metrics_summary")),
    ("last-run-invalid-json", "run", 4, "ERROR", "LAST_RUN_INVALID_JSON",
     lambda r: write(r / LAST_RUN, "[1, 2]")),
    ("last-run-missing", "run", 4, "ERROR", "LAST_RUN_MISSING",
     lambda r: (r / LAST_RUN).unlink()),
    ("report-path-invalid", "run", 4, "ERROR", "RUN_REPORT_PATH_INVALID",
     lambda r: set_last_run(r, unit={"report": "tests/docs/reports/u_report.md"})),
    ("counts-are-not-integers", "run", 4, "ERROR", "LAST_RUN_FIELD_INVALID",
     lambda r: set_last_run(r, unit={"passed": "3"}, benchmark={"total": None})),
    ("unexpected-report-entry", "all", 4, "ERROR", "REPORT_UNEXPECTED_ENTRY",
     lambda r: write(r / REPORTS / "notes.txt", "stray file\n")),
    ("legacy-report-residue", "all", 0, "ADVISORY", "REPORT_LEGACY_BATCH_RESIDUE",
     lambda r: write(r / REPORTS / "u_report_20261101_120000.md", "# old\n")),
]


class TestDiagnosticCoverage(unittest.TestCase):
    """Injected violations on scratch copies prove that each check group actually fires."""

    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(shutil.rmtree, SCRATCH, True)
        shutil.rmtree(SCRATCH, ignore_errors=True)
        cls.base = SCRATCH / "base"
        shutil.copytree(GOLDEN["python-sample"], cls.base, ignore=shutil.ignore_patterns("tmp"))

    def test_injected_violations_are_detected(self):
        for name, scope, exit_code, severity, code, mutate in MUTATIONS:
            with self.subTest(mutation=name):
                target = SCRATCH / name
                shutil.rmtree(target, ignore_errors=True)
                shutil.copytree(self.base, target)
                mutate(target)
                proc = run_verify(target, "--scope", scope, "--json")
                self.assertEqual(proc.returncode, exit_code, proc.stdout)
                self.assertIn(code, codes_by_severity(proc)[severity])


if __name__ == "__main__":
    unittest.main()
