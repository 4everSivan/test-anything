# textkit-sample

A miniature Python project that serves as the **golden sample** of the
[`test-anything`](../../README.md) skill. It contains a small business package
(`textkit`) and the `tests/` suite that `test-anything create` / `run` produce
for it.

## Functional points

### `textkit.wordcount`

1. **Word counting** — `count_words(text)` returns the number of words in
   `text`. Empty or whitespace-only text counts as `0`. A non-string argument
   raises `TypeError`.
2. **Word ranking** — `top_words(text, limit)` returns up to `limit`
   `(word, count)` pairs. Words are compared case-insensitively; ties are broken
   alphabetically. A negative `limit` raises `ValueError`; `limit=0` returns an
   empty list.

### `textkit.slugify`

3. **Slug conversion** — `slugify(text)` returns a lowercase ASCII slug: runs of
   non-alphanumeric characters (including non-ASCII letters) collapse into a
   single hyphen and leading or trailing hyphens are removed. Empty text yields
   an empty slug.
4. **Slug length limit** — `slugify(text, max_len)` cuts the slug to `max_len`
   characters without leaving a trailing hyphen. `max_len` smaller than `1`
   raises `ValueError`.
5. **Stop-word removal** *(planned)* — `slugify(text, max_len=None,
   ignore_stopwords=False)` drops the common English stop words `a`, `an`,
   `the` and `of` from the slug when `ignore_stopwords` is `True`.

## Testing

The test suite is managed by `test-anything`; see
[`tests/docs/README.md`](tests/docs/README.md) for the module matrix, the
runner commands and the latest reports.
