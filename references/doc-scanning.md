# Stage 1: Document Scanning, Functional Point Extraction, and Drafts

This reference owns Stage 1 (`STAGE_1_DRAFT`) of the `create` pipeline: source discovery order, functional point (`FP-<module>-<NN>`) extraction, `u_` vs `b_` candidate triage, legacy test synthesis, gap classification, and the 4-section `tests/docs/drafts/<module>_draft.md` contract.

## 1. Document and Source Discovery Order

Scan the target project in the following priority order (excluding `tests/docs/`, `_test_anything_backup/snapshots/`, `_adflow_backup/`, and third-party vendor/dependency directories):

1. **Structured production documentation:** `docs/official/*.md` (such as knowledge libraries produced by `km`), `docs/devel/design/*.md`, `docs/*.md`, and API contracts (OpenAPI, Protobuf, GraphQL schemas).
2. **Root project documentation:** `<target_root>/README.md` and module-level `README.md` files.
3. **Isolated legacy tests:** `<target_root>/_test_anything_backup/original_tests/` (when present after Stage 0 atomic isolation).
4. **Target source tree:** `src/`, `lib/`, `app/`, `cmd/`, `pkg/`, `internal/`, or root source modules, used to align module boundaries and verify which documented functional points are actually implemented.

## 2. Module Identification and Functional Point (`FP-xxx`) Extraction

Group discovered capabilities by coherent business module (`<module>` in English `snake_case`, e.g., `auth`, `parser`, `matching`). For each module:

- Assign stable functional point IDs `FP-<module>-01`, `FP-<module>-02`, etc.
- Extract for every functional point:
  - **Trigger & Input Constraints:** parameter types, value ranges, required preconditions, configuration flags.
  - **Expected Behavior & Output:** return values, state transitions, emitted events, or persisted side effects.
  - **Boundary & Exception Rules:** empty/null inputs, min/max thresholds, malformed payloads, concurrency/timeout errors, and specific error types/codes.
  - **Source Location:** exact document heading and corresponding source file/line or symbol.

## 3. Triage into `u_` (Unit) and `b_` (Benchmark) Candidates

Every extracted functional point is evaluated for both tracks:

- **Unit Test Candidates (`u_`, `CAND-U-<NN>`):**
  - Cover `normal` (happy path), `boundary` (edge values, empty collections, limits), and `exception` (invalid inputs, error codes, failure recovery) dimensions.
  - When `_test_anything_backup/original_tests/` exists, map existing legacy test cases into `CAND-U-<NN>` entries (`source: legacy_tests` or `both`) so no previously tested assertion is lost.
- **Benchmark Candidates (`b_`, `CAND-B-<NN>`):**
  - Identify CPU-intensive algorithms, high-frequency parsers/serializers, batch data processing loops, and memory-sensitive operations associated with `FP-<module>-<NN>`.
  - Specify the hotspot reason, planned workload scale (e.g., 100 / 1k / 10k items), and target metrics (`ops/sec`, `ns/op` or `us/op`, `P99 latency`, `B/op`).

## 4. Gap Identification (`GAP-<module>-<NN>`)

Record discrepancies explicitly rather than inventing behavior:
- `unimplemented`: Documented in project docs, but the target module/function does not exist or is a stub in source code.
- `conflict`: Documentation and source code disagree on input/output contracts or error types.
- `missing_data`: Requires external fixtures or sample payloads not yet available.

## 5. `tests/docs/drafts/<module>_draft.md` Format Contract

Render each module draft using [templates/docs/draft.md.tpl](../templates/docs/draft.md.tpl) with the single-line blockquote header (`> **module**: <module> ｜ **type**: draft ｜ **updated_at**: YYYY-MM-DD ｜ **status**: active`) and exactly four H2 sections:
1. `## 1. 来源与模块边界`
2. `## 2. 功能点拆解清单 (Functional Points)`
3. `## 3. 候选测试点分流` (`### 3.1 单元测试候选 (u_)` and `### 3.2 性能基准候选 (b_)`)
4. `## 4. 待确认与实现差异 (Gaps)`
