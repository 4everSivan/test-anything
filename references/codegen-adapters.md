# Stage 4: Multi-Language Test Code Generation and Fixtures

This reference owns Stage 4 (`STAGE_4_CODEGEN_AND_MANIFEST`) of the `create` pipeline: calibrating source signatures, generating executable unit (`tests/unit/u_*`) and benchmark (`tests/benchmark/b_*`) code, embedding `@case`/`@feature` traceability anchors, structuring `tests/fixtures/`, and running bounded syntax verification.

## 1. File Naming and Language Runner Conventions

Name generated files in `tests/unit/` and `tests/benchmark/` with `u_` and `b_` prefixes while satisfying the target language's native test discovery:

| Language / Stack | Unit Test Path (`tests/unit/`) | Benchmark Path (`tests/benchmark/`) | Function Naming Pattern |
|---|---|---|---|
| Python (`pytest` / `unittest`) | `u_<module>_test.py` | `b_<module>_bench.py` | `def test_ut_<module>_<NNN>_<slug>():` / `def test_bm_<module>_<NNN>_<slug>():` |
| Go (`go test`) | `u_<module>_test.go` | `b_<module>_bench_test.go` | `func TestUT_<Module>_<NNN>_<Slug>(t *testing.T)` / `func BenchmarkBM_<Module>_<NNN>_<Slug>(b *testing.B)` |
| TypeScript / JS (`vitest` / `jest` / `node --test`) | `u_<module>.test.ts` (or `.js`) | `b_<module>.bench.ts` (or `.js`) | `test("UT-<module>-<NNN>: <slug>", ...)` / `bench("BM-<module>-<NNN>: <slug>", ...)` |
| Rust (`cargo test` / `cargo bench`) | `u_<module>_test.rs` | `b_<module>_bench.rs` | `fn test_ut_<module>_<NNN>_<slug>()` / `fn bench_bm_<module>_<NNN>_<slug>()` |

Ensure the runner command recorded in `manifest.json.stack` explicitly discovers `u_*` and `b_*` files in `tests/unit/` and `tests/benchmark/` (for example, `pytest tests/unit -o python_files="u_*_test.py" -o cache_dir=tests/tmp/.pytest_cache`).

## 2. Internal Test Code Format Contract

Every generated test code file must include:

1. **Top-of-file metadata comment block:**
   ```python
   # @managed-by: test-anything
   # @module: <module>
   # @type: unit_test | benchmark
   # @cases_doc: tests/docs/cases/u_<module>_cases.md
   ```
2. **Per-function `@case` and `@feature` anchor comments:**
   Place directly above each test/benchmark function so `run` can map execution results back to `UT-<module>-<NNN>` and `BM-<module>-<NNN>`:
   ```python
   # @case: UT-<module>-001
   # @feature: FP-<module>-01
   # @scenario: normal
   ```
3. **Arrange-Act-Assert (AAA) body:**
   - **Arrange:** Load complex inputs from `tests/fixtures/<module>_fixtures.json` and direct any temporary files/directories to `tests/tmp/`.
   - **Act:** Invoke the real calibrated target symbol from the project's source code.
   - **Assert:** Verify all expected outcomes from `u_<module>_cases.md` (or record benchmark timing/iterations for `b_<module>_cases.md`).
   - Skip or omit code generation for cases marked `status: todo` (`unimplemented`); never generate `assert True` placeholders to fake coverage.

## 3. Shared Fixture Format (`tests/fixtures/`)

Store reusable sample payloads in `tests/fixtures/<module>_fixtures.json` (or language-native helper modules). Every JSON fixture file must include a top-level `_meta` object:

```json
{
  "_meta": {
    "managed_by": "test-anything",
    "module": "<module>",
    "used_by_cases": ["UT-<module>-001", "BM-<module>-001"]
  }
}
```

## 4. Bounded Syntax and Import Precheck

After generating `tests/unit/` and `tests/benchmark/`:
- Run a static syntax or compile check (e.g., `python3 -m py_compile`, `go test -c -o tests/tmp/check.test`, `tsc --noEmit`).
- If a check fails due to a defect in the generated test file (wrong import path, typo in helper call, syntax error), repair the generated test file locally (at most **3 rounds**).
- Never modify target project business source files during `create`.
