#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contract of the ta-verify integration: the create completion gate, the run report-only check, and the CI baseline."""

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GATE_RULES = "references/artifact-verification.md"


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def yaml_block(text, marker):
    """Return the YAML block opened by `marker`, up to the next sibling list item or top-level key."""
    start = text.index(marker)
    indent = len(text[:start].rsplit("\n", 1)[-1])
    item_indent = indent - 2  # `- stage:` / `- id:` sits two columns left of its keys
    nxt = re.compile(r"\n(?: {%d}- |\S)" % item_indent).search(text, start)
    return text[start:nxt.start() if nxt else len(text)]


def quoted_actions(block):
    """The double-quoted action strings of a stage block, in file order."""
    return re.findall(r'^\s+- "([^"]*)"$', block, re.M)


def field(block, name):
    return re.search(r'%s: "([^"]*)"' % name, block).group(1)


# How the workflow spells a verifier run; the scope is asserted separately.
VERIFY_RUN = "scripts/ta-verify --target <target_root> --scope"


class TestCreateCompletionGate(unittest.TestCase):
    """Stage 4 of create may record completion only after scripts/ta-verify --scope create exits 0."""

    def setUp(self):
        self.stage = yaml_block(read("workflow.yaml"), 'id: "STAGE_4_CODEGEN_AND_MANIFEST"')
        self.actions = quoted_actions(self.stage)

    def index_of(self, needle):
        hits = [i for i, action in enumerate(self.actions) if needle in action]
        self.assertEqual(len(hits), 1, "expected exactly one Stage 4 action mentioning %r" % needle)
        return hits[0]

    def test_invariant_is_declared_as_fatal(self):
        invariant = yaml_block(read("workflow.yaml"), 'id: "INV_VERIFY_BEFORE_COMPLETE"')
        self.assertIn('severity: "FATAL"', invariant)
        for phrase in ("exits 0", "at most 3 rounds", "never changes a track status, count, exit code, "
                      "or metric", "Never copy the verifier into the target project",
                      "weaken a check", "rewrite a recorded hash"):
            self.assertIn(phrase, invariant)

    def test_complete_is_written_only_after_the_gate_passes(self):
        write = self.index_of("write 'tests/.state/manifest.json'")
        gate = self.index_of("%s create" % VERIFY_RUN)
        complete = self.index_of("set create_status 'complete'")
        self.assertLess(write, gate, "manifest records are written before the gate can check them")
        self.assertLess(gate, complete, "create_status 'complete' must follow a passing gate")
        self.assertIn("keeping create_status 'in_progress'", self.actions[write])
        self.assertIn("case_ids", self.actions[write])
        self.assertIn("without copying or installing it into the target project", self.actions[gate])
        self.assertTrue(self.actions[complete].startswith("Only on Exit 0 set create_status 'complete'"))

    def test_failed_gate_keeps_in_progress_with_bounded_repair(self):
        gate = self.index_of("%s create" % VERIFY_RUN)
        repair = self.index_of("On Exit 4")
        self.assertGreater(repair, gate, "the repair loop follows the gate run")
        self.assertIn("repair only the generated files", self.actions[repair])
        self.assertIn("at most 3 rounds", self.actions[repair])
        self.assertIn("keep create_status 'in_progress'", self.actions[repair])
        self.assertIn("never record complete without", field(self.stage, "on_blocker"))
        self.assertIn("exited 0 before create_status 'complete' was recorded",
                      field(self.stage, "completion_condition"))

    def test_stage_loads_the_reference_that_owns_the_gate(self):
        self.assertIn('"%s"' % GATE_RULES, self.stage)
        gate = read(GATE_RULES).split("## 5. `create` Stage 4 Completion Gate", 1)[1].split("## 6.", 1)[0]
        for phrase in ("--scope create --json", "keeping `create_status: \"in_progress\"`",
                       "On Exit `0`, set `create_status: \"complete\"` and `completed_stage: 4`",
                       "at most 3 rounds", "keep `create_status: \"in_progress\"`",
                       "Writing `complete` without an Exit `0` from the gate is forbidden"):
            self.assertIn(phrase, gate)


class TestRunReportOnlyVerification(unittest.TestCase):
    """Stage 3 of run reports the --scope run result without re-judging the test outcome."""

    def setUp(self):
        self.stage = yaml_block(read("workflow.yaml"), 'id: "RUN_STAGE_3_REPORT_AND_STATE"')
        self.actions = quoted_actions(self.stage)

    def test_verification_runs_after_the_reports_are_written(self):
        state = [i for i, action in enumerate(self.actions)
                 if action.startswith("Update 'tests/.state/last_run.json'")]
        checks = [i for i, action in enumerate(self.actions) if "%s run" % VERIFY_RUN in action]
        self.assertEqual((len(state), len(checks)), (1, 1))
        self.assertGreater(checks[0], state[0])
        self.assertIn('"%s"' % GATE_RULES, self.stage)

    def test_verification_never_changes_a_test_result(self):
        check = next(action for action in self.actions if "%s run" % VERIFY_RUN in action)
        for phrase in ("copy its findings verbatim into the run summary",
                       "never change any status, count, exit code, or metric",
                       "never let it weaken INV_NO_PASS_WITHOUT_EVIDENCE"):
            self.assertIn(phrase, check)
        # The required sentences must not be contradicted by a licence to edit the outcome.
        for forbidden in ("Correct", "correct ", "Rewrite", "rewrite", "Amend", "amend", "Adjust",
                          "adjust", "update the report", "update 'tests/docs/reports"):
            self.assertNotIn(forbidden, check)
        self.assertIn("included in the run summary unchanged", field(self.stage, "completion_condition"))

    def test_track_status_is_still_derived_from_real_execution_only(self):
        derive = [action for action in self.actions if action.startswith("Derive each track's status")]
        self.assertEqual(len(derive), 1)
        self.assertIn("actual exit code and parsed counts", derive[0])
        self.assertIn("INV_NO_PASS_WITHOUT_EVIDENCE", derive[0])
        for action in self.actions:
            if "ta-verify" in action:
                self.assertNotIn("Derive", action, "verification must not take part in status derivation")
                self.assertNotIn("overwrite 'tests/docs/reports/", action)

    def test_stage_loads_the_reference_that_owns_the_check(self):
        section = read(GATE_RULES).split("## 6. `run` Stage 3 Report-Only Verification", 1)[1].split("## 7.", 1)[0]
        for phrase in ("--scope run --json", "reported, never applied", "never weakens",
                       "never edit report numbers or the state file"):
            self.assertIn(phrase, section)


class TestRuleOwnersStayInSync(unittest.TestCase):
    """SKILL.md, the other references and the README describe the gate where it belongs."""

    def test_skill_md_routes_the_gate_rules(self):
        skill = read("SKILL.md")
        self.assertIn("[artifact-verification](%s)" % GATE_RULES, skill)
        owners = [line for line in skill.splitlines() if line.startswith("| [")]
        self.assertEqual(len(owners), 6, "one Rule Owners row per reference file")
        self.assertIn("7. **Verified before complete, reported without re-judging.**", skill)
        for phrase in ("`scripts/ta-verify --scope create` exits 0",
                       "`scripts/ta-verify --scope run` and report its findings verbatim",
                       "never copied into or installed on the target project",
                       "on exit 4 repair only the generated files named by the findings"):
            self.assertIn(phrase, skill)

    def test_other_references_point_to_the_gate_instead_of_restating_it(self):
        pointers = {
            "references/state-and-backup.md": "artifact gate in [artifact-verification](artifact-verification.md) Section 5",
            "references/runner-and-reporting.md": "[artifact-verification](artifact-verification.md) Section 6",
            "references/codegen-adapters.md": "[artifact-verification](artifact-verification.md) Section 5",
        }
        for rel, pointer in pointers.items():
            self.assertIn(pointer, read(rel), rel)

    def test_readme_describes_both_integration_points(self):
        readme = read("README.md")
        for phrase in ("scripts/ta-verify --scope create", "scripts/ta-verify --scope run",
                       "(%s)" % GATE_RULES, "(examples/README.md)", "examples/negative/"):
            self.assertIn(phrase, readme)


class TestContinuousIntegration(unittest.TestCase):
    """The GitHub Actions workflow runs exactly the regression baseline of the design."""

    WORKFLOW = ".github/workflows/ci.yml"

    def test_workflow_runs_the_baseline_on_push_and_pull_request(self):
        workflow = read(self.WORKFLOW)
        self.assertRegex(workflow, r"(?m)^on:\n  push:\n  pull_request:\n")
        self.assertIn('python3 -m unittest discover -s tests -p "test_skill_contract.py" -v', workflow)
        self.assertIn('python3 -m unittest discover -s tests -p "test_artifact_gate.py" -v', workflow)
        self.assertIn("scripts/ta-verify --target examples/python-sample --scope all", workflow)
        self.assertIn("scripts/ta-verify --target examples/go-sample --scope all", workflow)
        self.assertIn('python3 -m unittest discover -s tests -p "test_ta_verify.py" -v', workflow)

    def test_every_test_module_named_by_ci_exists(self):
        modules = re.findall(r'-p "(test_\w+\.py)"', read(self.WORKFLOW))
        self.assertEqual(len(modules), 3)
        for module in modules:
            self.assertTrue((ROOT / "tests" / module).is_file(), module)

    def test_ci_needs_no_ai_run_and_installs_no_toolchain(self):
        # The baseline only runs the contract tests and ta-verify (stdlib only) on committed samples.
        for forbidden in ("pip install", "pytest", "setup-go", "go-version", "coverage"):
            self.assertNotIn(forbidden, read(self.WORKFLOW), forbidden)

    def test_ci_commands_succeed_locally(self):
        for command in re.findall(r"^\s+(scripts/ta-verify --target \S+ --scope all)$", read(self.WORKFLOW),
                                  re.M):
            with self.subTest(command=command):
                proc = subprocess.run(command, shell=True, cwd=str(ROOT), stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, universal_newlines=True, check=False)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
