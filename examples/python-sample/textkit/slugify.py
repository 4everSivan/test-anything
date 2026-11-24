"""Convert free text into URL-friendly slugs."""

import re

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def slugify(text, max_len=None):
    """Return a lowercase ASCII slug for ``text``.

    Runs of non-alphanumeric characters collapse into single hyphens and
    leading or trailing hyphens are removed. When ``max_len`` is given the slug
    is cut to that length without leaving a trailing hyphen.
    """
    if max_len is not None and max_len <= 0:
        raise ValueError("max_len must be a positive integer")
    slug = _NON_ALNUM_RE.sub("-", text.lower()).strip("-")
    if max_len is not None:
        slug = slug[:max_len].rstrip("-")
    return slug
