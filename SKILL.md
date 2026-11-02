---
name: test-anything
description: >-
  Generate and execute document-driven unit tests and performance benchmarks in a
  standardized `tests/` hierarchy. Use when the user invokes `$test-anything`,
  requests `/test-anything` in a compatible host, or asks to run `$test-anything help`,
  `$test-anything create`, or `$test-anything run [unittest|benchmark]` for a target project.
metadata:
  version: "0.1.0"
---

# test-anything: Document-Driven Full-Stack Testing Skill

Build, maintain, and execute a traceable `tests/` suite (`docs/`, `unit/`, `benchmark/`, `fixtures/`, `tmp/`, `.state/`) from a target project's documentation, source code contracts, and legacy tests.

## 1. Command Routing and Entrypoints

Resolve the user's invocation into one of three strictly separated tracks:

- **`$test-anything help` / `--help` / `-h`** (including `$test-anything create --help` or `$test-anything run --help`):
  **Read-only help mode.** Print the structured Chinese command usage, `create` 4-stage pipeline overview, `run` decoupling rule, and `tests/` layout summary directly in chat. Do **not** create directories, back up files, or execute tests.
- **`$test-anything` (bare invocation)** or **`$test-anything create`**:
  Initialize `tests/` in the target project root (isolating any unmanaged legacy `tests/` into `/_test_anything_backup/original_tests/tests/` first, only after showing its impact and receiving the user's explicit confirmation; resuming instead when a previous `create` was interrupted) and execute the full **4-stage `create` pipeline** (`drafts` → `plans` → `cases` → `unit` & `benchmark` code). `create` has no `unittest|benchmark` filter subcommand; it always covers both unit tests (`u_`) and benchmarks (`b_`).
- **`$test-anything run [unittest|benchmark]`**:
  Execute generated tests and write honest reports to `tests/docs/reports/` and `tests/.state/last_run.json`. Reports keep only the latest run: each report file is overwritten in place, never accumulated per run.
  - `$test-anything run` (default): run both `tests/unit/` and `tests/benchmark/`, overwriting `u_report_latest.md`, `b_report_latest.md`, and `all_report_latest.md`.
  - `$test-anything run unittest`: run only `tests/unit/`, overwriting `u_report_latest.md`.
  - `$test-anything run benchmark`: run only `tests/benchmark/`, overwriting `b_report_latest.md`.
  - **Strict decoupling gate:** If `tests/.state/manifest.json` is absent, records `create_status: "in_progress"`, or no managed test code exists for the requested scope, **abort immediately with an error** instructing the user to run `$test-anything create` first. Never trigger `create` implicitly from `run`.

## 2. How to Run

- Follow [workflow.yaml](workflow.yaml) stage by stage using the host's native file, search, and command execution tools. Do not require external workflow engines.
- Target the project named by the user, otherwise the current working directory. If the target directory is ambiguous, ask before writing.
- Resolve all references and templates relative to this `SKILL.md` file.

## 3. Core Principles

1. **Document-driven functional points + source-calibrated call contracts.** Extract functional points (`FP-<module>-<NN>`), boundaries, error rules, and performance hotspots from project documentation (`docs/official/`, `docs/`, `README.md`, API schemas), then calibrate module imports, function signatures, and types against actual source code when generating `tests/unit/` and `tests/benchmark/`. Mark documented but unimplemented features as `unimplemented/todo` in `cases/` rather than generating fake passing tests.
2. **Draft-first 4-stage `create` pipeline.** Every `create` run progresses sequentially through Stage 1 (`tests/docs/drafts/`), Stage 2 (`tests/docs/plans/`), Stage 3 (`tests/docs/cases/`), and Stage 4 (`tests/unit/`, `tests/benchmark/`, `tests/fixtures/`, `tests/.state/manifest.json`). Progress is recorded in `tests/.state/manifest.json` (`create_status`, `completed_stage`) from the end of Stage 0, so a blocked or interrupted run resumes at the next unfinished stage instead of being mistaken for a legacy `tests/`; a damaged manifest stops the run without moving anything.
3. **Zero-destruction legacy test backup (`/_test_anything_backup/`).** Before creating any backup or `tests/tmp/`, ensure the target root `.gitignore` ignores `/_test_anything_backup/` and `/tests/tmp/`. If an unmanaged `tests/` directory exists, show the user its impact (file count, Git-tracked files that will appear deleted, config and CI references to `tests/`) and wait for explicit confirmation; then atomically move it to `_test_anything_backup/original_tests/tests/`, recreate `tests/`, and synthesize the legacy test assertions and fixtures into the new suite. Never delete or overwrite captured backups.
4. **English `u_` / `b_` filenames + Chinese document prose + single-line metadata header.** All files under `tests/docs/` and code directories use English `snake_case` names, distinguishing unit and benchmark assets via `u_` and `b_` prefixes (`all_` for combined reports) without extra `unit/` or `benchmark/` subdirectories inside `docs/`. Write `tests/docs/` prose in Chinese while keeping identifiers, signatures, commands, `FP-xxx`, `UT-xxx`, and `BM-xxx` in English. Place the single-line blockquote metadata header directly below H1 in every `tests/docs/*.md` file.
5. **Real execution, `tests/tmp/` isolation, and read-only business source in `run`.** During `run`, direct all runner caches, coverage dumps, and temporary files into `tests/tmp/`. Never modify the target project's business source code or weaken assertions to fabricate passing results. Record actual exit codes, counts, stack traces, and benchmark metrics, and derive each track's status from them: a crash, zero executed cases, or unparseable output is `error`, never a pass.
6. **Bounded local repair for generated test syntax.** In Stage 4 of `create`, if generated test files fail syntax or import prechecks due to test-code defects, repair the generated test files locally for at most 3 rounds. Stop and report if the blocker persists or stems from target business code.

## 4. Rule Owners

Each detailed rule is stated in full in one reference file. Load only the reference needed for the active stage:

| Reference | Owns |
|---|---|
| [state-and-backup](references/state-and-backup.md) | `tests/` directory topology, `.gitignore` rules, `tests/` mode classification and `create` resume progress, confirmed `/_test_anything_backup/` atomic isolation and snapshots, `.state/{manifest,last_run,config}.json` schemas, and incremental hash checks |
| [doc-scanning](references/doc-scanning.md) | Stage 1 document scanning order, functional point (`FP-xxx`) extraction, `u_` vs `b_` candidate triage, gap classification, legacy test absorption, and `drafts/<module>_draft.md` 4-section format |
| [case-and-plan-design](references/case-and-plan-design.md) | Stage 2 two-level plans (`test_plan.md`, `<module>_plan.md` traceability matrix) and Stage 3 case specifications (`u_<module>_cases.md` 6-element cards, `b_<module>_cases.md` 5-element cards) |
| [codegen-adapters](references/codegen-adapters.md) | Stage 4 source signature calibration, language runner adapters, file header metadata comments, `@case`/`@feature` function anchors, AAA structure, and `fixtures/` `_meta` contract |
| [runner-and-reporting](references/runner-and-reporting.md) | `run [unittest\|benchmark]` preflight gate, runner execution with `tests/tmp/` isolation, read-only source invariant, track status derivation (`passed`/`completed`/`failed`/`error`), and 3-part report formats (`u_report_*`, `b_report_*`, `all_report_latest.md`) |
