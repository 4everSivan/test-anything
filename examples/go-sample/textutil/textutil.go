// Package textutil provides small string helpers.
package textutil

import "strings"

// Reverse returns s with its runes in opposite order.
func Reverse(s string) string {
	runes := []rune(s)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}
	return string(runes)
}

// IsPalindrome reports whether s reads the same forwards and backwards,
// ignoring case and spaces.
func IsPalindrome(s string) bool {
	compact := strings.ReplaceAll(strings.ToLower(s), " ", "")
	return compact == Reverse(compact)
}
