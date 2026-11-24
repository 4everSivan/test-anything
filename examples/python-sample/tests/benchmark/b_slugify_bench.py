# @managed-by: test-anything
# @module: slugify
# @type: benchmark
# @cases_doc: tests/docs/cases/b_slugify_cases.md
"""slugify 模块性能基准：规格见 tests/docs/cases/b_slugify_cases.md。"""

import json
import pathlib
import time

from textkit.slugify import slugify

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"
WARMUP_ROUNDS = 3
MEASURED_ROUNDS = 20


# @case: BM-slugify-001
# @feature: FP-slugify-01
# @scenario: hotspot
def test_bm_slugify_001_slugify_title_batch():
    """BM-slugify-001: 万条标题批量生成 slug。"""
    fixture = json.loads((FIXTURES / "slugify_fixtures.json").read_text(encoding="utf-8"))   # Arrange
    titles = fixture["titles"] * fixture["batch_repeats"]
    for _ in range(WARMUP_ROUNDS):
        for title in titles:
            slugify(title)
    start = time.perf_counter()                          # Act
    for _ in range(MEASURED_ROUNDS):
        slugs = [slugify(title) for title in titles]
    elapsed = (time.perf_counter() - start) / MEASURED_ROUNDS
    assert slugs[0] == "the-quick-brown-fox"             # Assert
    print("\nBM-slugify-001 titles=%d rounds=%d avg_ms_per_op=%.2f titles_per_sec=%.0f"
          % (len(titles), MEASURED_ROUNDS, elapsed * 1e3, len(titles) / elapsed))
