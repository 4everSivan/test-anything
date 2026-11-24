"""Word counting and word ranking helpers."""

import re

_WORD_RE = re.compile(r"[A-Za-z0-9']+")


def count_words(text):
    """Return the number of words in ``text``; empty or blank text counts as 0."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return len(_WORD_RE.findall(text))


def top_words(text, limit):
    """Return up to ``limit`` ``(word, count)`` pairs, most frequent first.

    Words are compared case-insensitively; ties are broken alphabetically.
    """
    if limit < 0:
        raise ValueError("limit must be >= 0")
    counts = {}
    for word in _WORD_RE.findall(text.lower()):
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:limit]
