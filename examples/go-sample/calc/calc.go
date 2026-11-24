// Package calc provides small integer arithmetic helpers.
package calc

import "errors"

// Add returns the sum of a and b.
func Add(a, b int) int {
	return a + b
}

// Div divides a by b, truncating toward zero, and returns an error when b is zero.
func Div(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}
