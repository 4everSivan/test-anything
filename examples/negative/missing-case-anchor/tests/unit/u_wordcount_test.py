# @managed-by: test-anything
# @module: wordcount
# @type: unit_test
# @cases_doc: tests/docs/cases/u_wordcount_cases.md
"""wordcount 模块单元测试：规格见 tests/docs/cases/u_wordcount_cases.md。"""

import json
import pathlib

import pytest

from textkit.wordcount import count_words, top_words

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


def _load(name):
    """读取 tests/fixtures/ 下的 JSON 夹具。"""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


# @case: UT-wordcount-001
# @feature: FP-wordcount-01
# @scenario: normal
def test_ut_wordcount_001_counts_words_in_sentence():
    """UT-wordcount-001: 统计句子中的单词数。"""
    fixture = _load("wordcount_fixtures.json")          # Arrange
    result = count_words(fixture["sentence"])            # Act
    assert result == fixture["sentence_word_count"]      # Assert


# @case: UT-wordcount-002
# @feature: FP-wordcount-01
# @scenario: boundary
def test_ut_wordcount_002_counts_blank_text_as_zero():
    """UT-wordcount-002: 空串与纯空白文本都计为 0。"""
    fixture = _load("wordcount_fixtures.json")          # Arrange
    results = [count_words(text) for text in fixture["blank_texts"]]   # Act
    assert results == [0] * len(fixture["blank_texts"])  # Assert


# @case: UT-wordcount-003
# @feature: FP-wordcount-02
# @scenario: exception
def test_ut_wordcount_003_rejects_negative_limit():
    """UT-wordcount-003: limit 为负数时抛出 ValueError。"""
    fixture = _load("wordcount_fixtures.json")          # Arrange
    with pytest.raises(ValueError):                     # Act + Assert
        top_words(fixture["sentence"], fixture["negative_limit"])


def test_extra_sanity_check():
    """临时补充的校验，未登记用例规格，也没有 @case / @feature 锚点。"""
    assert count_words("one two") == 2
