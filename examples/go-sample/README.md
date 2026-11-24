# gosample

A miniature Go project that serves as the **golden sample** of the
[`test-anything`](../../README.md) skill. It contains two small business
packages (`calc`, `textutil`) and the `tests/` suite that
`test-anything create` / `run` produce for them.

## Functional points

### `calc`

1. **Integer addition** — `calc.Add(a, b)` returns the sum of two integers.
2. **Integer division** — `calc.Div(a, b)` divides `a` by `b`, truncating
   toward zero. A zero divisor returns a non-nil error instead of panicking.

### `textutil`

3. **Text reversal** — `textutil.Reverse(s)` returns the string with its runes
   in opposite order. It handles empty strings and multi-byte characters.
4. **Palindrome detection** — `textutil.IsPalindrome(s)` reports whether `s`
   reads the same forwards and backwards, ignoring case and spaces.

## Testing

The test suite is managed by `test-anything`; see
[`tests/docs/README.md`](tests/docs/README.md) for the module matrix, the
runner commands and the latest reports.
