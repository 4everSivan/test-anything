# @managed-by: test-anything
# @module: wordcount
# @type: benchmark
# @cases_doc: tests/docs/cases/b_wordcount_cases.md
"""wordcount 模块性能基准：规格见 tests/docs/cases/b_wordcount_cases.md。"""

import json
import pathlib
import time

from textkit.wordcount import top_words

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"
WARMUP_ROUNDS = 3
MEASURED_ROUNDS = 20


# @case: BM-wordcount-001
# @feature: FP-wordcount-02
# @scenario: hotspot
def test_bm_wordcount_001_top_words_on_large_corpus():
    """BM-wordcount-001: 万词语料上的词频排序。"""
    fixture = json.loads((FIXTURES / "wordcount_fixtures.json").read_text(encoding="utf-8"))   # Arrange
    corpus = " ".join(fixture["corpus_words"] * fixture["corpus_repeats"])
    for _ in range(WARMUP_ROUNDS):
        top_words(corpus, 10)
    start = time.perf_counter()                          # Act
    for _ in range(MEASURED_ROUNDS):
        ranked = top_words(corpus, 10)
    elapsed = (time.perf_counter() - start) / MEASURED_ROUNDS
    assert ranked[0][1] == fixture["corpus_repeats"]     # Assert
    print("\nBM-wordcount-001 corpus_words=%d rounds=%d avg_us_per_op=%.1f ops_per_sec=%.1f"
          % (len(fixture["corpus_words"]) * fixture["corpus_repeats"], MEASURED_ROUNDS,
             elapsed * 1e6, 1.0 / elapsed))
