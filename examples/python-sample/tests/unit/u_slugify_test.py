# @managed-by: test-anything
# @module: slugify
# @type: unit_test
# @cases_doc: tests/docs/cases/u_slugify_cases.md
"""slugify 模块单元测试：规格见 tests/docs/cases/u_slugify_cases.md。"""

import json
import pathlib

import pytest

from textkit.slugify import slugify

FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


def _load(name):
    """读取 tests/fixtures/ 下的 JSON 夹具。"""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


# @case: UT-slugify-001
# @feature: FP-slugify-01
# @scenario: normal
def test_ut_slugify_001_converts_text_to_lowercase_slug():
    """UT-slugify-001: 混合大小写与非 ASCII 文本转换为小写 slug。"""
    fixture = _load("slugify_fixtures.json")            # Arrange
    result = slugify(fixture["title"])                   # Act
    assert result == fixture["expected_slug"]            # Assert
    assert result == result.lower() and result.isascii()


# @case: UT-slugify-002
# @feature: FP-slugify-02
# @scenario: boundary
def test_ut_slugify_002_handles_empty_text_and_length_limit():
    """UT-slugify-002: 空文本返回空串；截断后末尾不留连字符。"""
    fixture = _load("slugify_fixtures.json")            # Arrange
    empty = slugify("")                                  # Act
    truncated = slugify(fixture["title"], fixture["max_len"])
    assert empty == ""                                   # Assert
    assert truncated == fixture["expected_truncated_slug"]
    assert not truncated.endswith("-")


# @case: UT-slugify-003
# @feature: FP-slugify-02
# @scenario: exception
def test_ut_slugify_003_rejects_non_positive_max_len():
    """UT-slugify-003: max_len 为 0 时抛出 ValueError。"""
    fixture = _load("slugify_fixtures.json")            # Arrange
    with pytest.raises(ValueError):                     # Act + Assert
        slugify(fixture["title"], fixture["invalid_max_len"])
