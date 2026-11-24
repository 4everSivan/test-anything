// @managed-by: test-anything
// @module: calc
// @type: benchmark
// @cases_doc: tests/docs/cases/b_calc_cases.md
package benchmark

import (
	"testing"

	"example.com/go-sample/calc"
)

// @case: BM-calc-001
// @feature: FP-calc-01
// @scenario: hotspot
func BenchmarkBM_Calc_001_AddLoop(b *testing.B) {
	// Arrange
	const iterations = 1000
	// Act
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		total := 0
		for j := 0; j < iterations; j++ {
			total += calc.Add(j, j)
		}
		// Assert
		if total != iterations*(iterations-1) {
			b.Fatalf("unexpected total %d", total)
		}
	}
}
