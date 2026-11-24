// @managed-by: test-anything
// @module: calc
// @type: unit_test
// @cases_doc: tests/docs/cases/u_calc_cases.md
package unit

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"example.com/go-sample/calc"
)

// calcFixture 对应 tests/fixtures/calc_fixtures.json；Go 测试的工作目录是所在包目录。
type calcFixture struct {
	Add         struct{ A, B, Expected int }              `json:"add"`
	Divide      struct{ Dividend, Divisor, Expected int } `json:"divide"`
	ZeroDivisor int                                       `json:"zero_divisor"`
}

func loadCalcFixture(tb testing.TB) calcFixture {
	tb.Helper()
	data, err := os.ReadFile(filepath.Join("..", "fixtures", "calc_fixtures.json"))
	if err != nil {
		tb.Fatalf("read calc fixture: %v", err)
	}
	var fixture calcFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		tb.Fatalf("parse calc fixture: %v", err)
	}
	return fixture
}

// @case: UT-calc-001
// @feature: FP-calc-01
// @scenario: normal
func TestUT_Calc_001_AddPositiveIntegers(t *testing.T) {
	// Arrange
	fixture := loadCalcFixture(t)
	// Act
	got := calc.Add(fixture.Add.A, fixture.Add.B)
	// Assert
	if got != fixture.Add.Expected {
		t.Fatalf("Add(%d, %d) = %d, want %d", fixture.Add.A, fixture.Add.B, got, fixture.Add.Expected)
	}
}

// @case: UT-calc-002
// @feature: FP-calc-02
// @scenario: exception
func TestUT_Calc_002_DivideByZeroReturnsError(t *testing.T) {
	// Arrange
	fixture := loadCalcFixture(t)
	// Act
	_, err := calc.Div(fixture.Divide.Dividend, fixture.ZeroDivisor)
	// Assert
	if err == nil {
		t.Fatalf("Div(%d, %d) returned nil error, want error", fixture.Divide.Dividend, fixture.ZeroDivisor)
	}
}

// @case: UT-calc-003
// @feature: FP-calc-02
// @scenario: boundary
func TestUT_Calc_003_DivideTruncatesTowardZero(t *testing.T) {
	// Arrange
	fixture := loadCalcFixture(t)
	// Act
	got, err := calc.Div(fixture.Divide.Dividend, fixture.Divide.Divisor)
	// Assert
	if err != nil || got != fixture.Divide.Expected {
		t.Fatalf("Div(%d, %d) = %d, %v; want %d, <nil>", fixture.Divide.Dividend, fixture.Divide.Divisor, got, err, fixture.Divide.Expected)
	}
}
