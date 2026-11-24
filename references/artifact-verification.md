# Artifact Verification (`scripts/ta-verify`)

This reference owns the read-only artifact verifier `scripts/ta-verify`: how `create` and `run` invoke it, what its diagnostic codes mean and trace back to, and the regression baseline that keeps the verifier and the rules from drifting apart.

## 1. Invocation and Boundaries

1. **Run it from the skill package, never from the target project.** Resolve `scripts/ta-verify` relative to this skill's `SKILL.md` and pass the target explicitly: `scripts/ta-verify --target <target_root> [--scope create|run|all] [--json] [--receipt]`. Never copy the script into, or install anything in, the target project.
2. **Read-only.** `ta-verify` opens target files for reading only. It never writes, repairs, moves, or deletes anything; fixing a finding stays inside the `create` / `run` generate–check–repair loop.
3. **Scope.** `create` checks the `create` artifacts (Section 3), `run` checks the `run` artifacts (Section 4), and `all` (the default) runs both.
4. **Exit codes.** `0` no violations; `4` at least one deterministic violation; `2` a usage error or an unreadable target (missing directory, unreadable or non-UTF-8 file). Any other exit code means the tool itself failed: report it as a tool failure, never as a verdict on the artifacts.
5. **Output.** Text by default: one line per finding followed by its fix hint. `--json` emits `summary.codes` plus `findings[]` entries carrying `severity`, `code`, `group`, `path`, `line`, `message`, `hint`, and `basis`. `--receipt` prints the fixed-format artifact receipt of this verification; it reports only `ta-verify`'s own result and is never the conversational receipt that closes a `run`.

`ta-verify` checks structure and traceability only. It does not judge test design quality and never replaces the real test execution of `run`.

## 2. Severity Levels and Rule Provenance

| Severity | Meaning | Effect on the exit code |
|---|---|---|
| `ERROR` | A deterministic violation of a rule in `references/` | Exit `4` |
| `WARNING` | A managed file differs from its `manifest.json` record, which indicates a manual edit | None |
| `ADVISORY` | Informational only, such as an absent empty or ignored directory, or a legacy per-run report left in `reports/` | None |

1. **Every diagnostic code is registered with the clause it is based on.** The registry at the top of `scripts/ta-verify` maps each code to the `references/` file and section heading it derives from. The contract test fails when that section is renamed or removed, so update the registry in the same change as the rule.
2. **A hash mismatch is a `WARNING`, never a violation.** Managed test code whose SHA-256 differs from `manifest.json` was probably edited by a developer. The incremental `create` snapshot flow in [state-and-backup](state-and-backup.md) handles it; the verifier must not block on it, and nobody may rewrite a recorded hash just to make a run pass.
3. **Absent optional directories are an `ADVISORY`.** `tests/tmp/` is ignored by `.gitignore`, and an empty `tests/fixtures/` is not tracked by Git, so both are legitimately missing in a fresh checkout. `tests/docs/`, `tests/unit/`, `tests/benchmark/`, and `tests/.state/` must exist.
4. **Fix locally, at most 3 rounds.** Repair only the generated files named by the findings, then re-run. Never weaken a check, edit a recorded hash, or work around the verifier to obtain Exit `0`.

## 3. Checks in `--scope create`

| Group | What is verified | Rule owner |
|---|---|---|
| Directory layout | `tests/docs/`, `tests/unit/`, `tests/benchmark/`, and `tests/.state/` exist | [state-and-backup](state-and-backup.md) Section 1 |
| Document naming | `docs/drafts`, `docs/plans`, and `docs/cases` exist and stay flat; every file follows its subdirectory's `<module>_draft.md` / `test_plan.md` / `<module>_plan.md` / `u_<module>_cases.md` / `b_<module>_cases.md` contract; `reports/` holds only the three `*_latest.md` files; code files follow the `u_` / `b_` naming table | [state-and-backup](state-and-backup.md) Section 1, [codegen-adapters](codegen-adapters.md) Section 1 |
| Case traceability | Each summary-table row in a cases document has exactly one H3 card; every `UT-` / `BM-` case appears in the module plan's traceability matrix bound to the same `FP-` feature point, and its feature points are declared in the module's draft or matrix | [case-and-plan-design](case-and-plan-design.md) Sections 1.2 and 2, [doc-scanning](doc-scanning.md) Section 2 |
| Code anchors | Every test and benchmark function carries `@case` and `@feature` directly above it; each anchor resolves to a case of the same module and track and to a declared feature point; each case that needs code is bound by exactly one function | [codegen-adapters](codegen-adapters.md) Section 2 |
| Manifest | Required fields and value types match the protocol; `modules` covers exactly the modules found in `cases/`; `case_ids` equals the set of cases that need code; every recorded file exists; recorded SHA-256 values match the files | [state-and-backup](state-and-backup.md) Section 4.1 |

Cases marked `todo` or `unimplemented` need no test function: no code is generated for a capability that does not exist yet.

The gate of Section 5 runs while `manifest.json` still records `create_status: "in_progress"`, so `--scope create` never requires `complete`.

## 4. Checks in `--scope run`

| Group | What is verified | Rule owner |
|---|---|---|
| Run state | `last_run.json` carries every field with the right type; each track status agrees with the exit code and parsed counts; tracks outside the requested scope are `not_run` and tracks inside it are not | [state-and-backup](state-and-backup.md) Section 4.2, [runner-and-reporting](runner-and-reporting.md) Section 3.0 |
| Report set | `reports/` contains only the three `*_latest.md` files; the set of reports whose header carries the current `run_id` equals what the scope writes (`unittest` writes the unit report, `benchmark` the benchmark report, `all` all three) | [runner-and-reporting](runner-and-reporting.md) Section 3 |
| Report headers | The single-line header under H1 is well formed and matches the report type; its status equals the track status in `last_run.json`, and the full-suite report takes the worst executed track | [state-and-backup](state-and-backup.md) Section 2, [runner-and-reporting](runner-and-reporting.md) Section 3 |
| Report cases | Every `UT-` / `BM-` id mentioned in the current reports exists in `cases/` | [runner-and-reporting](runner-and-reporting.md) Section 3 |

Reports left from earlier runs carry an older `run_id` and are not compared against the current `last_run.json`.

## 5. `create` Stage 4 Completion Gate

`create` may record completion only after the artifacts pass verification:

1. Write the complete module records into `tests/.state/manifest.json` (paths, SHA-256 values, `case_ids`) while keeping `create_status: "in_progress"` and `completed_stage` at `3`.
2. Run `scripts/ta-verify --target <target_root> --scope create --json`.
3. On Exit `0`, set `create_status: "complete"` and `completed_stage: 4`.
4. On Exit `4`, repair only the generated files named by the findings and run the gate again, at most 3 rounds in total. If it still fails, keep `create_status: "in_progress"`, leave `completed_stage` unchanged, and report the findings as they are.

These rounds are separate from the syntax and import precheck rounds of [codegen-adapters](codegen-adapters.md) Section 4. Writing `complete` without an Exit `0` from the gate is forbidden, and so is changing target business source code to satisfy the gate.

## 6. `run` Stage 3 Report-Only Verification

After the reports and `tests/.state/last_run.json` are written, run `scripts/ta-verify --target <target_root> --scope run --json` and copy its findings verbatim into the run summary.

1. The result is reported, never applied: do not change any `passed` / `failed` / `error` / `completed` status, count, exit code, or metric because of it.
2. It never weakens `INV_NO_PASS_WITHOUT_EVIDENCE`. A structurally valid report can still be wrong, and a structural violation never turns a failing run into a passing one or the reverse.
3. On Exit `4`, report the violations and offer to repair the generated artifacts through `create`; never edit report numbers or the state file to silence a finding.

## 7. Regression Baseline (`examples/`)

1. **Golden samples.** `examples/python-sample` and `examples/go-sample` are real target projects whose `tests/` was produced by `create` and `run`. Both must exit `0` for `--scope all`.
2. **Negative samples.** Each directory under `examples/negative/` is a minimal target project with exactly one injected violation. Its `expected.json` records the `scope`, the required `exit_code`, and the exact set of `ERROR` codes (or, for the warning sample, the exact set of `WARNING` codes with exit `0`).
3. **Keep them in step with the rules.** When a rule change makes a golden sample fail, regenerate the artifacts in the same change and have them reviewed; never relax a check to keep old artifacts passing. Give every new diagnostic code a negative sample or a contract test.
