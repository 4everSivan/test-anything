#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automated contract and structure tests for the test-anything skill package."""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def yaml_block(text, marker):
    """Return the YAML block opened by `marker`, up to the next sibling list item or top-level key."""
    start = text.index(marker)
    indent = len(text[:start].rsplit("\n", 1)[-1])
    item_indent = indent - 2  # `- stage:` / `- id:` sits two columns left of its keys
    nxt = re.compile(r"\n(?: {%d}- |\S)" % item_indent).search(text, start)
    return text[start:nxt.start() if nxt else len(text)]


class TestSkillPackageContract(unittest.TestCase):
    """Verify SKILL.md, workflow.yaml, references/, and templates/ contracts."""

    def test_skill_md_frontmatter_and_reference_links(self):
        skill_md = ROOT / "SKILL.md"
        self.assertTrue(skill_md.is_file(), "SKILL.md must exist")
        content = skill_md.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: test-anything", content)
        self.assertIn('version: "0.1.0"', content)

        # Verify all markdown links in SKILL.md point to existing files
        links = re.findall(r"\]\(([^)#]+)\)", content)
        self.assertGreaterEqual(len(links), 6)
        for rel in links:
            target = ROOT / rel
            self.assertTrue(target.is_file(), f"Broken link in SKILL.md: {rel}")

    def test_workflow_yaml_routes_and_asset_references(self):
        wf = ROOT / "workflow.yaml"
        self.assertTrue(wf.is_file(), "workflow.yaml must exist")
        text = wf.read_text(encoding="utf-8")

        # Core invariants
        for inv in (
            "INV_CREATE_RUN_DECOUPLED",
            "INV_NO_DELETE_BACKUP",
            "INV_CONFIRM_LEGACY_MOVE",
            "INV_READONLY_BUSINESS_SOURCE_ON_RUN",
            "INV_NO_PASS_WITHOUT_EVIDENCE",
            "INV_ENGLISH_PREFIX_NAMING",
            "INV_DRAFT_FIRST_PIPELINE",
        ):
            self.assertIn(inv, text, f"Missing invariant {inv} in workflow.yaml")

        # Command routes
        for cmd in (
            '"$test-anything help"',
            '"$test-anything --help"',
            '"$test-anything -h"',
            '"$test-anything"',
            '"$test-anything create"',
            '"$test-anything run"',
            '"$test-anything run unittest"',
            '"$test-anything run benchmark"',
        ):
            self.assertIn(cmd, text, f"Missing command route {cmd} in workflow.yaml")

        # Stages in help_pipeline, create_pipeline, and run_pipeline
        for stage_id in (
            "HELP_STAGE_1_DISPLAY",
            "STAGE_0_INIT_AND_BACKUP",
            "STAGE_1_DRAFT",
            "STAGE_2_PLAN",
            "STAGE_3_CASE",
            "STAGE_4_CODEGEN_AND_MANIFEST",
            "RUN_STAGE_1_PREFLIGHT_GATE",
            "RUN_STAGE_2_EXECUTE",
            "RUN_STAGE_3_REPORT_AND_STATE",
        ):
            self.assertIn(stage_id, text, f"Missing stage {stage_id} in workflow.yaml")

        # Verify all referenced files in workflow.yaml exist on disk
        ref_paths = re.findall(r'"((?:references|templates)/[^"]+)"', text)
        self.assertGreaterEqual(len(ref_paths), 15)
        for rel in ref_paths:
            self.assertTrue((ROOT / rel).is_file(), f"Missing workflow referenced asset: {rel}")

    def test_references_completeness_and_anchor_contracts(self):
        expected_refs = [
            "references/state-and-backup.md",
            "references/doc-scanning.md",
            "references/case-and-plan-design.md",
            "references/codegen-adapters.md",
            "references/runner-and-reporting.md",
        ]
        for rel in expected_refs:
            p = ROOT / rel
            self.assertTrue(p.is_file(), f"Missing reference file: {rel}")

        codegen_txt = (ROOT / "references/codegen-adapters.md").read_text(encoding="utf-8")
        self.assertIn("@managed-by: test-anything", codegen_txt)
        self.assertIn("@case:", codegen_txt)
        self.assertIn("@feature:", codegen_txt)
        self.assertIn('"_meta"', codegen_txt)

    def test_json_state_templates_valid(self):
        state_templates = {
            "templates/state/manifest.json.tpl": [
                "schema_version",
                "skill_version",
                "stack",
                "backup_ref",
                "sources",
                "modules",
            ],
            "templates/state/last_run.json.tpl": [
                "run_id",
                "scope",
                "executed_at",
                "unit",
                "benchmark",
                "summary_report",
            ],
            "templates/state/config.json.tpl": [
                "schema_version",
                "unit_runner",
                "benchmark_runner",
                "exclude_paths",
                "regression_threshold_pct",
            ],
        }
        for rel, keys in state_templates.items():
            p = ROOT / rel
            self.assertTrue(p.is_file(), f"Missing state template: {rel}")
            data = json.loads(p.read_text(encoding="utf-8"))
            for k in keys:
                self.assertIn(k, data, f"Missing key {k} in {rel}")

    def test_markdown_templates_headers_and_sections(self):
        self.assertTrue((ROOT / "templates/backup-README.md.tpl").is_file())
        md_templates = {
            "templates/docs/README.md.tpl": [
                "**type**: index",
                "## 1. 测试体系概览与快速入口",
                "## 2. 模块测试资产矩阵",
                "## 3. 全局计划与最新报告导航",
            ],
            "templates/docs/draft.md.tpl": [
                "**type**: draft",
                "## 1. 来源与模块边界",
                "## 2. 功能点拆解清单 (Functional Points)",
                "## 3. 候选测试点分流",
                "## 4. 待确认与实现差异 (Gaps)",
            ],
            "templates/docs/test_plan.md.tpl": [
                "**type**: test_plan",
                "## 1. 目标技术栈与执行环境",
                "## 2. 模块测试覆盖总表",
                "## 3. 全局夹具与隔离策略",
            ],
            "templates/docs/module_plan.md.tpl": [
                "**type**: module_plan",
                "## 1. 功能点 ↔ 用例 ID ↔ 源码符号 双向追溯矩阵",
                "## 2. 模块夹具与 Mock 策略",
            ],
            "templates/docs/u_cases.md.tpl": [
                "**type**: unit_cases",
                "## 1. 单元测试用例总表",
                "## 2. 用例规格详情",
                "- **关联功能点**",
                "- **目标符号**",
                "- **场景类型**",
                "- **前置条件与夹具**",
                "- **输入参数（Given / When）**",
                "- **预期结果与断言（Then）**",
            ],
            "templates/docs/b_cases.md.tpl": [
                "**type**: benchmark_cases",
                "## 1. 基准测试用例总表",
                "## 2. 基准规格详情",
                "- **关联功能点与热点说明**",
                "- **目标符号**",
                "- **负载规模（Workload）**",
                "- **预热与迭代策略**",
                "- **采集指标与基线阈值**",
            ],
            "templates/docs/u_report.md.tpl": [
                "**type**: unit_report",
                "## 1. 执行概览",
                "## 2. 模块与用例执行明细",
                "## 3. 失败与异常诊断",
            ],
            "templates/docs/b_report.md.tpl": [
                "**type**: benchmark_report",
                "## 1. 运行环境与执行概览",
                "## 2. 性能基准核心指标表",
                "## 3. 热点分析与基线对比",
            ],
            "templates/docs/all_report.md.tpl": [
                "**type**: all_report",
                "## 1. 双轨执行总览",
                "## 2. 模块健康度矩阵",
                "## 3. 本次运行信息",
            ],
        }
        for rel, markers in md_templates.items():
            p = ROOT / rel
            self.assertTrue(p.is_file(), f"Missing doc template: {rel}")
            txt = p.read_text(encoding="utf-8")
            lines = txt.splitlines()
            self.assertTrue(lines[0].startswith("# "), f"{rel} must start with H1")
            self.assertTrue(
                lines[2].startswith("> **module**:"),
                f"{rel} must have single-line metadata blockquote on line 3",
            )
            for m in markers:
                self.assertIn(m, txt, f"Missing marker {m!r} in {rel}")

    # C001: an interrupted create must resume instead of being moved away as a legacy tests/.
    def test_create_progress_enables_resume(self):
        manifest = json.loads(read("templates/state/manifest.json.tpl"))
        self.assertEqual(manifest.get("create_status"), "in_progress")
        self.assertEqual(manifest.get("completed_stage"), 0)

        wf = read("workflow.yaml")
        self.assertIn("progress_protocol:", wf)
        stage0 = yaml_block(wf, 'id: "STAGE_0_INIT_AND_BACKUP"')
        self.assertIn("create_status 'in_progress' -> resume", stage0)
        self.assertIn("unparseable or without a valid schema_version -> stop and report without moving anything", stage0)
        self.assertIn("Resume only: skip the backup and move steps", stage0)
        self.assertIn("create_status 'in_progress' and completed_stage 0", stage0)
        stage4 = yaml_block(wf, 'id: "STAGE_4_CODEGEN_AND_MANIFEST"')
        self.assertIn("create_status 'complete', and completed_stage 4", stage4)
        gate = yaml_block(wf, 'id: "RUN_STAGE_1_PREFLIGHT_GATE"')
        self.assertIn("records create_status 'complete'", gate)

        state = read("references/state-and-backup.md")
        self.assertIn("→ **resume**", state)
        self.assertIn("Never treat a damaged manifest as a legacy directory and never move it", state)
        self.assertIn("- `completed_stage`: integer `0`–`4`", state)
        runner = read("references/runner-and-reporting.md")
        self.assertIn('records `create_status: "complete"`', runner)

        skill = read("SKILL.md")
        self.assertNotIn("preserve the completed draft in `drafts/` for resumption", skill)
        self.assertIn("resumes at the next unfinished stage", skill)

    # C001: an unmanaged tests/ may only be moved after an impact summary and explicit confirmation.
    def test_legacy_move_requires_explicit_confirmation(self):
        wf = read("workflow.yaml")
        inv = yaml_block(wf, 'id: "INV_CONFIRM_LEGACY_MOVE"')
        self.assertIn('severity: "FATAL"', inv)
        self.assertIn("silence never count as confirmation", inv)
        self.assertIn("appear deleted to Git", inv)

        stage0 = yaml_block(wf, 'id: "STAGE_0_INIT_AND_BACKUP"').splitlines()
        confirm = next(i for i, line in enumerate(stage0) if "wait for the user's explicit confirmation" in line)
        gitignore = next(i for i, line in enumerate(stage0) if "Ensure root '.gitignore'" in line)
        move = next(i for i, line in enumerate(stage0) if "atomically move 'tests/'" in line)
        self.assertLess(confirm, gitignore)
        self.assertLess(confirm, move)
        self.assertIn("only after confirmation", stage0[gitignore])
        self.assertIn("after confirmation", stage0[move])
        self.assertIn("the user does not confirm a legacy move", "\n".join(stage0))

        state = read("references/state-and-backup.md")
        section = state[state.index("3. **Isolate an unmanaged legacy `tests/` only after explicit confirmation:**"):]
        self.assertLess(section.index("Wait for the user's explicit confirmation"), section.index("Atomically move"))
        self.assertIn("stop with zero filesystem changes, `.gitignore` included", section)
        self.assertIn("git ls-files tests", section)

    # C001: a crashed or empty run must be reported as error, never as passed.
    def test_run_status_never_claims_pass_without_evidence(self):
        u_tpl = read("templates/docs/u_report.md.tpl")
        self.assertNotIn("本次运行全部通过", u_tpl)
        self.assertIn("<status_based_diagnosis>", u_tpl.split("## 3. 失败与异常诊断", 1)[1])
        self.assertIn("**status**: <passed|failed|error>", u_tpl)
        self.assertIn("**status**: <completed|failed|error>", read("templates/docs/b_report.md.tpl"))
        self.assertIn("**status**: <passed|failed|error>", read("templates/docs/all_report.md.tpl"))

        runner = read("references/runner-and-reporting.md")
        self.assertIn("### 3.0 Track Status Derivation", runner)
        rows = {line.split("|")[1].strip(): line for line in runner.splitlines()
                if line.startswith("| `") and "Track status" not in line}
        self.assertIn("non-zero exit code with no failing case parsed", rows["`error`"])
        self.assertIn("none collected, or all skipped", rows["`error`"])
        self.assertIn("exit code `0` while failures were parsed", rows["`error`"])
        self.assertIn("at least one case passed", rows["`passed` / `completed`"])
        order = [line.split("|")[1].strip() for line in runner.splitlines() if line.startswith("| `")]
        self.assertLess(order.index("`error`"), order.index("`passed` / `completed`"))
        pass_lines = [line for line in runner.splitlines() if "本次运行全部通过" in line]
        self.assertEqual(len(pass_lines), 1)
        self.assertTrue(pass_lines[0].lstrip().startswith("- `passed`"))

        wf = read("workflow.yaml")
        inv = yaml_block(wf, 'id: "INV_NO_PASS_WITHOUT_EVIDENCE"')
        self.assertIn('severity: "FATAL"', inv)
        report_stage = yaml_block(wf, 'id: "RUN_STAGE_3_REPORT_AND_STATE"')
        self.assertIn("INV_NO_PASS_WITHOUT_EVIDENCE", report_stage)
        state = read("references/state-and-backup.md")
        self.assertIn("`passed | failed | error | not_run`", state)
        self.assertIn("`completed | failed | error | not_run`", state)


    # C002: reports keep only the latest run; no per-run copies accumulate in tests/docs/reports/.
    def test_reports_keep_latest_run_only(self):
        rule_files = ["SKILL.md", "workflow.yaml", "README.md"]
        rule_files += [str(f.relative_to(ROOT)) for f in sorted((ROOT / "references").glob("*.md"))]
        rule_files += [str(f.relative_to(ROOT)) for f in sorted((ROOT / "templates").rglob("*.tpl"))]
        rule_files += [str(f.relative_to(ROOT)) for f in sorted((ROOT / "docs/devel/design").glob("0*.md"))]
        dated = re.compile(r"[ub]_report_\d{8}_\d{6}\.md")
        for rel in rule_files:
            for line in read(rel).splitlines():
                self.assertIsNone(dated.search(line), f"{rel} still names a dated per-run report: {line}")
                if "_report_<run_id>" in line:
                    # Only the prohibition itself and the design-history rows may mention the old pattern.
                    self.assertTrue("Never write per-run copies" in line or line.startswith("| [C002]"),
                                    f"{rel} still produces or links per-run reports: {line}")

        report_stage = yaml_block(read("workflow.yaml"), 'id: "RUN_STAGE_3_REPORT_AND_STATE"')
        self.assertIn("overwrite 'tests/docs/reports/u_report_latest.md' in place", report_stage)
        self.assertIn("overwrite 'tests/docs/reports/b_report_latest.md' in place", report_stage)
        self.assertIn("overwrite 'tests/docs/reports/all_report_latest.md'", report_stage)
        cleanup = [line for line in report_stage.splitlines() if "u_report_<YYYYMMDD_HHMMSS>.md" in line]
        self.assertEqual(len(cleanup), 1)
        self.assertIn("only after the user's explicit confirmation", cleanup[0])

        runner = read("references/runner-and-reporting.md")
        self.assertIn("Never write per-run copies", runner)
        self.assertIn("Delete only those files, and only after the user's explicit confirmation", runner)

        all_tpl = read("templates/docs/all_report.md.tpl")
        section3 = all_tpl.split("## 3. ", 1)[1]
        self.assertTrue(section3.startswith("本次运行信息"))
        self.assertNotIn("归档", all_tpl)
        self.assertIn("tests/.state/last_run.json", section3)

    def test_adflow_governance_gates_clean(self):
        for extra in (["--mode", "init", "--json"], ["--json"]):
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/adflow_verify.py"), *extra],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, f"adflow_verify failed: {proc.stdout}\n{proc.stderr}")
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["exit_code"], 0)
            self.assertEqual(payload["summary"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
