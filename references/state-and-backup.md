# Directory Layout, State Protocols, and Backup Isolation

This reference owns the target project's `tests/` directory topology, `.gitignore` rules, `/_test_anything_backup/` atomic isolation and snapshot protection, `tests/docs/README.md` navigation contract, and `tests/.state/` JSON schemas.

## 1. Target `tests/` Directory Topology

All generated test assets reside under `<target_root>/tests/`:

- `tests/docs/`: Test documentation center (English `snake_case` filenames, Chinese prose, single-line metadata header)
  - `tests/docs/README.md`: Navigation index (overview & commands, module matrix, latest report links)
  - `tests/docs/drafts/<module>_draft.md`: Stage 1 functional point & candidate draft
  - `tests/docs/plans/test_plan.md`: Stage 2 global test plan
  - `tests/docs/plans/<module>_plan.md`: Stage 2 per-module plan & bidirectional traceability matrix
  - `tests/docs/cases/u_<module>_cases.md`: Stage 3 unit test specification (`u_` prefix)
  - `tests/docs/cases/b_<module>_cases.md`: Stage 3 benchmark specification (`b_` prefix)
  - `tests/docs/reports/u_report_latest.md`: Latest unit test report (overwritten on every run)
  - `tests/docs/reports/b_report_latest.md`: Latest benchmark report (overwritten on every run)
  - `tests/docs/reports/all_report_latest.md`: Combined full-suite report
- `tests/unit/u_<module>_test.<ext>`: Executable unit test code
- `tests/benchmark/b_<module>_bench.<ext>`: Executable performance benchmark code
- `tests/fixtures/<module>_fixtures.<ext|json>`: Shared test data, mocks, and golden samples
- `tests/tmp/`: Ephemeral runner cache, sandbox files, and raw coverage/benchmark dumps
- `tests/.state/`: Machine state and traceability records (`manifest.json`, `last_run.json`, optional `config.json`)

Never create nested `unit/` or `benchmark/` subdirectories inside `tests/docs/cases/` or `tests/docs/reports/`.

## 2. Universal Markdown Header and Language Rule

Every Markdown document under `tests/docs/` starts with an H1 heading followed immediately by a single-line blockquote metadata header (no YAML frontmatter):

```markdown
# <Chinese Document Title>

> **module**: <module|global> ｜ **type**: <index|draft|test_plan|module_plan|unit_cases|benchmark_cases|unit_report|benchmark_report|all_report> ｜ **updated_at**: YYYY-MM-DD ｜ **status**: <draft|active|passed|failed|completed|error>
```

 Report files (`u_report_latest.md`, `b_report_latest.md`, `all_report_latest.md`) include `**run_id**: <YYYYMMDD_HHMMSS>` before `**updated_at**`.

## 3. `.gitignore` and `/_test_anything_backup/` Isolation

1. **Classify `tests/` before any write:** Inspect the target read-only and pick exactly one mode:
   - `<target_root>/tests/` does not exist → **fresh**: initialize the standard `tests/` tree directly.
   - `tests/.state/manifest.json` parses and has a valid `schema_version`:
     - `create_status` is `"in_progress"` → **resume**: a previous `create` was blocked or interrupted. Do not back up or move anything; keep existing artifacts and continue at stage `completed_stage + 1`, re-reading and validating the artifacts of completed stages instead of regenerating them.
     - `create_status` is `"complete"`, or the field is absent (manifests written before this field existed were only written on completion) → **incremental**.
   - `tests/.state/manifest.json` exists but does not parse or lacks a valid `schema_version` → **stop and report**. Never treat a damaged manifest as a legacy directory and never move it; ask the user to repair or remove it.
   - `tests/` exists **without** `tests/.state/manifest.json` → **legacy**: follow item 3.
   - In **fresh** and **legacy** modes, reject `create --module` with a stop-and-report error before any write, backup, or migration: `--module` requires an existing manifest (resume or incremental), so those modes must first complete a full create.
2. **Ensure `.gitignore` exclusion before creating backups or `tests/tmp/`:** Inspect `<target_root>/.gitignore`. Create it if absent; otherwise preserve existing lines and append `/_test_anything_backup/` and `/tests/tmp/` if not already covered. In legacy mode, do this only after the confirmation in item 3.
3. **Isolate an unmanaged legacy `tests/` only after explicit confirmation:**
   1. Check that `_test_anything_backup/original_tests/tests` does not already exist (stop and report if a collision is found).
   2. Survey read-only and present the impact to the user:
      - the number of files under `tests/`;
      - the number of Git-tracked files under `tests/` (for example `git ls-files tests`) and the consequence: once moved into the ignored backup zone, Git sees them as deleted, so the next commit that stages all changes removes them from the repository;
      - project configuration and CI files that reference `tests/` (such as `pyproject.toml`, `pytest.ini`, `setup.cfg`, `tox.ini`, `package.json`, `Makefile`, `.github/workflows/`), which will stop finding the legacy tests;
      - the backup destination `_test_anything_backup/original_tests/tests`.
   3. Wait for the user's explicit confirmation in the conversation. The invocation itself, earlier instructions, or silence never count as confirmation. Without it, stop with zero filesystem changes, `.gitignore` included.
   4. Apply item 2, then create `_test_anything_backup/README.md` from [templates/backup-README.md.tpl](../templates/backup-README.md.tpl) if absent.
   5. Atomically move `<target_root>/tests` to `<target_root>/_test_anything_backup/original_tests/tests`.
   6. Recreate the clean `<target_root>/tests/` hierarchy and record `"backup_ref": "_test_anything_backup/original_tests/tests"` in `manifest.json`. Do not alter Git's index.
4. **Create progress tracking:** At the end of Stage 0, write `tests/.state/manifest.json` with `create_status: "in_progress"` (fresh and legacy modes start with `completed_stage: 0`; incremental mode resets it to `0` and keeps existing `modules` records; resume mode keeps the recorded value). The same write records `module_scope` as the deduplicated `--module` list, or `[]` when no `--module` was given; only a resume keeps its recorded `module_scope` instead of re-inferring it (see the module-scoped rules below). After a stage completes for every module in scope, set `completed_stage` to that stage number and refresh `updated_at`. Stage 4 first writes the full module records with `create_status: "in_progress"` and `completed_stage: 3`, and sets `create_status: "complete"` and `completed_stage: 4` only after the artifact gate in [artifact-verification](artifact-verification.md) Section 5 exits `0`. A stage stopped by a blocker or interruption leaves `completed_stage` unchanged, so the next `create` resumes at that stage.
   - **Module-scoped create:** `create --module <module>` (repeatable) is accepted only with an existing manifest (resume or incremental). Stage 0 writes `module_scope` as the deduplicated list of `--module` values, or `[]` without `--module` (meaning the full project). A resume always keeps the `module_scope` recorded at interruption, even when invoked without `--module`; never re-infer it, and change scope only through an explicit new create run. A full create without `--module` leaves `module_scope` as `[]` on completion, and a bare incremental create also writes `[]` because recomputing only changed modules is runtime behavior never recorded in `module_scope`. Stages 1–4 then run for those modules only: update `modules` entries, the draft/plan/cases/code files, and the `sources` hashes only for modules in scope, and advance `completed_stage` only once every in-scope module finished the stage. Stage 4 replaces only the in-scope `modules` entries; every out-of-scope entry stays byte-for-byte unchanged. A module name that appears in none of the manifest, the project documentation, or the source tree aborts the run.
5. **Incremental modification snapshots:** On incremental `create` (and on resume when the manifest already has code records), if a managed file in `tests/unit/` or `tests/benchmark/` has a disk SHA-256 different from `manifest.json` (indicating manual user edits), copy it to `_test_anything_backup/snapshots/<run_id>/` before updating, and preserve user-added assertions where compatible.
6. **Read-only backup invariant:** Never delete, modify, or overwrite any file inside `/_test_anything_backup/`.

## 4. `tests/.state/` File Contracts

### 4.1 `tests/.state/manifest.json`

Use [templates/state/manifest.json.tpl](../templates/state/manifest.json.tpl). Required top-level fields:
- `schema_version`: `"1.0"`
- `skill_version`: `"0.1.0"`
- `create_status`: `"in_progress" | "complete"`; progress of the most recent `create` (see Section 3 item 4). Only `"complete"` (or an absent field) allows `run`
- `completed_stage`: integer `0`–`4`; the last `create` stage completed for every module in scope
- `created_at`, `updated_at`: ISO-8601 timestamps
- `stack`: `{ "language": "...", "unit_runner": "...", "benchmark_runner": "..." }`
- `backup_ref`: path to `_test_anything_backup/original_tests/tests` or `null`
- `sources`: map of relative document/source paths to `{ "sha256": "<hex>" }`
- `modules`: map of `<module>` to `{ "draft", "plan", "unit_cases_doc", "benchmark_cases_doc", "fixtures", "unit_code": { "path", "sha256", "case_ids" }, "benchmark_code": { "path", "sha256", "case_ids" } }`
- `module_scope` (optional): array of module names covered by the most recent `create`. An empty array or an absent field means the full project. Stage 0 writes it as the deduplicated `--module` list, or `[]` without `--module`; a resume keeps the recorded value, a full create leaves `[]` on completion, and a bare incremental create also writes `[]` because recomputing only changed modules is runtime behavior, not scope. Under `create --module`, only these modules' entries and `sources` hashes are updated, `completed_stage` advances only for them, and Stage 4 leaves every out-of-scope `modules` entry byte-for-byte unchanged. `--module` is rejected in fresh and legacy modes, which stop and report without writing or migrating anything.

`case_ids` lists only the cases that need generated test code. Cases marked `todo`, `unimplemented`, or `deprecated` keep their specification in `cases/` but generate no code, so they are excluded from `case_ids`. Case IDs are append-only: never renumber, reuse, or reorder existing IDs, and mark a case `deprecated` instead of deleting it when its capability disappears from the source.

### 4.2 `tests/.state/last_run.json`

Use [templates/state/last_run.json.tpl](../templates/state/last_run.json.tpl). Updated after every `run`, `run unittest`, or `run benchmark`:
- `run_id`: `"YYYYMMDD_HHMMSS"`
- `scope`: `"all" | "unittest" | "benchmark"`
- `executed_at`: ISO-8601 timestamp
- `unit`: execution summary (`status`: `passed | failed | error | not_run`, `command`, `exit_code`, `total`, `passed`, `failed`, `skipped`, `duration_ms`, `report`, `coverage`)
- `unit.coverage`: coverage of the unit track, written by every `run`. It is the JSON object printed by `scripts/ta-verify --coverage` (see [runner-and-reporting](runner-and-reporting.md) Section 5), copied verbatim:
  - `status`: `ok` (parsed from this run's raw file) | `unavailable` (tool missing, or collection/parsing failed) | `not_supported` (a language other than Python or Go) | `not_run` (the unit track is outside the requested scope)
  - `reason`: `null` when `status` is `ok`; otherwise a non-empty explanation
  - `tool`, `format`: the tool name and one of `coverage-json` | `lcov` | `go-coverprofile`; `null` unless `status` is `ok`
  - `line_pct`, `branch_pct`: numbers from `0` to `100` with two decimals when measured, otherwise the string `"N/A"`; never `0` as a placeholder. `branch_pct` is always `"N/A"` for `go-coverprofile`, because Go only has statement-block coverage
  - `raw`: relative paths of the raw files that were parsed, under `tests/tmp/coverage/`
  - `modules`: `{ "<module>": { "line_pct", "branch_pct", "uncovered_total" } }`. A module is a source file name without its extension; a Python package's `__init__.py` counts as its directory
  - `uncovered[]`: at most 50 entries per module, each `{ "module", "file", "symbol", "kind", "lines" }`. `kind` is `line` (a contiguous range such as `22-26`), `branch` (an arc such as `10->11`), or `block` (a Go statement-block range)
  - `uncovered_omitted`: `{ "<module>": <count> }` of uncovered entries per module beyond the 50-entry cap
  - When `status` is not `ok`, `raw`, `modules`, and `uncovered` are empty and `uncovered_omitted` is `{}`.
- `benchmark`: execution summary (`status`: `completed | failed | error | not_run`, `command`, `exit_code`, `total`, `duration_ms`, `metrics_summary`, `report`)
- `summary_report`: `"tests/docs/reports/all_report_latest.md"` or `null`

### 4.3 `tests/.state/config.json` (Optional)

Use [templates/state/config.json.tpl](../templates/state/config.json.tpl). Allows overriding `unit_runner`, `benchmark_runner`, `exclude_paths`, and `regression_threshold_pct` (default `15.0`). Preserve existing user values across updates.
