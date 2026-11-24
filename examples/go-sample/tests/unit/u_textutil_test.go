// @managed-by: test-anything
// @module: textutil
// @type: unit_test
// @cases_doc: tests/docs/cases/u_textutil_cases.md
package unit

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"example.com/go-sample/textutil"
)

type reverseCase struct {
	Input    string `json:"input"`
	Expected string `json:"expected"`
}

// textutilFixture 对应 tests/fixtures/textutil_fixtures.json；Go 测试的工作目录是所在包目录。
type textutilFixture struct {
	ReverseCases   []reverseCase `json:"reverse_cases"`
	BoundaryCases  []reverseCase `json:"boundary_cases"`
	Palindromes    []string      `json:"palindromes"`
	NotPalindromes []string      `json:"not_palindromes"`
}

func loadTextutilFixture(tb testing.TB) textutilFixture {
	tb.Helper()
	data, err := os.ReadFile(filepath.Join("..", "fixtures", "textutil_fixtures.json"))
	if err != nil {
		tb.Fatalf("read textutil fixture: %v", err)
	}
	var fixture textutilFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		tb.Fatalf("parse textutil fixture: %v", err)
	}
	return fixture
}

// @case: UT-textutil-001
// @feature: FP-textutil-01
// @scenario: normal
func TestUT_Textutil_001_ReversesRunes(t *testing.T) {
	// Arrange
	fixture := loadTextutilFixture(t)
	// Act + Assert
	for _, tc := range fixture.ReverseCases {
		if got := textutil.Reverse(tc.Input); got != tc.Expected {
			t.Fatalf("Reverse(%q) = %q, want %q", tc.Input, got, tc.Expected)
		}
	}
}

// @case: UT-textutil-002
// @feature: FP-textutil-01
// @scenario: boundary
func TestUT_Textutil_002_ReversesEmptyAndUnicodeText(t *testing.T) {
	// Arrange
	fixture := loadTextutilFixture(t)
	// Act + Assert
	for _, tc := range fixture.BoundaryCases {
		if got := textutil.Reverse(tc.Input); got != tc.Expected {
			t.Fatalf("Reverse(%q) = %q, want %q", tc.Input, got, tc.Expected)
		}
	}
}

// @case: UT-textutil-003
// @feature: FP-textutil-02
// @scenario: normal
func TestUT_Textutil_003_DetectsPalindromes(t *testing.T) {
	// Arrange
	fixture := loadTextutilFixture(t)
	// Act + Assert
	for _, s := range fixture.Palindromes {
		if !textutil.IsPalindrome(s) {
			t.Fatalf("IsPalindrome(%q) = false, want true", s)
		}
	}
	for _, s := range fixture.NotPalindromes {
		if textutil.IsPalindrome(s) {
			t.Fatalf("IsPalindrome(%q) = true, want false", s)
		}
	}
}
