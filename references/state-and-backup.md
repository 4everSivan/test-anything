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
4. **Create progress tracking:** At the end of Stage 0, write `tests/.state/manifest.json` with `create_status: "in_progress"` (fresh and legacy modes start with `completed_stage: 0`; incremental mode resets it to `0` and keeps existing `modules` records until Stage 4 replaces them; resume mode keeps the recorded value). After a stage completes for every module in scope, set `completed_stage` to that stage number and refresh `updated_at`. Stage 4 writes the full manifest with `create_status: "complete"` and `completed_stage: 4`. A stage stopped by a blocker or interruption leaves `completed_stage` unchanged, so the next `create` resumes at that stage.
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

### 4.2 `tests/.state/last_run.json`

Use [templates/state/last_run.json.tpl](../templates/state/last_run.json.tpl). Updated after every `run`, `run unittest`, or `run benchmark`:
- `run_id`: `"YYYYMMDD_HHMMSS"`
- `scope`: `"all" | "unittest" | "benchmark"`
- `executed_at`: ISO-8601 timestamp
- `unit`: execution summary (`status`: `passed | failed | error | not_run`, `command`, `exit_code`, `total`, `passed`, `failed`, `skipped`, `duration_ms`, `report`)
- `benchmark`: execution summary (`status`: `completed | failed | error | not_run`, `command`, `exit_code`, `total`, `duration_ms`, `metrics_summary`, `report`)
- `summary_report`: `"tests/docs/reports/all_report_latest.md"` or `null`

### 4.3 `tests/.state/config.json` (Optional)

Use [templates/state/config.json.tpl](../templates/state/config.json.tpl). Allows overriding `unit_runner`, `benchmark_runner`, `exclude_paths`, and `regression_threshold_pct` (default `15.0`). Preserve existing user values across updates.
