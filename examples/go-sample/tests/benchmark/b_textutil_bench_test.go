// @managed-by: test-anything
// @module: textutil
// @type: benchmark
// @cases_doc: tests/docs/cases/b_textutil_cases.md
package benchmark

import (
	"strings"
	"testing"

	"example.com/go-sample/textutil"
)

// @case: BM-textutil-001
// @feature: FP-textutil-01
// @scenario: hotspot
func BenchmarkBM_Textutil_001_ReverseLongString(b *testing.B) {
	// Arrange
	const benchLength = 4096
	text := strings.Repeat("abcba", benchLength/5)
	// Act
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		got := textutil.Reverse(text)
		// Assert
		if len(got) != len(text) || got[0] != text[len(text)-1] {
			b.Fatalf("unexpected reverse result")
		}
	}
}
