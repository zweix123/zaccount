package transaction

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/zweix123/zaccount/backend/common/logger"
)

func setup() {
	logger.InitLogger("debug")
}
func teardown() {}
func TestMain(m *testing.M) {
	setup()         // 全局初始化
	code := m.Run() // testing.M的唯一方法，执行所在包下的所有TestXxx函数
	teardown()      // 全局清理
	os.Exit(code)
}

func TestIsValidTransactionType(t *testing.T) {
	testCases := []struct {
		name     string
		tt       TransactionType
		expected bool
	}{
		{"有效-收入", TransactionTypeIncome, true},
		{"有效-支出", TransactionTypeExpense, true},
		{"有效-转入", TransactionTypeTransferIn, true},
		{"有效-转出", TransactionTypeTransferOut, true},
		{"无效-空字符串", TransactionType(""), false},
		{"无效-随机字符串", TransactionType("随机类型"), false},
		{"无效-部分匹配", TransactionType("收"), false},
		{"无效-大小写敏感", TransactionType("INCOME"), false},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := IsValidTransactionType(tc.tt)
			assert.Equal(t, tc.expected, result, "IsValidTransactionType(%q) = %v, want %v", tc.tt, result, tc.expected)
		})
	}
}
