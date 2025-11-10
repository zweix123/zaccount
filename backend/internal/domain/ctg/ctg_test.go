package category

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestCtg_Contains(t *testing.T) {
	ctg := GetInstance()
	assert.True(t, ctg.IsValid("收入", []string{"工资"}))
	assert.True(t, ctg.IsValid("支出", []string{"餐饮", "午饭"}))
	assert.False(t, ctg.IsValid("支出", []string{"餐饮", "早餐"}))
}
