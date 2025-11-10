package transaction

import (
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestUnmarshalRow(t *testing.T) {
	testCases := []struct {
		name        string
		record      []string
		wantErr     bool
		errContains string
		validate    func(t *testing.T, transaction *Transaction)
	}{
		{
			name:    "正常情况",
			record:  []string{"2025-01-01", "转入", "1000.50", "餐饮", "午餐", "测试描述1"},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC), transaction.Date)
				assert.Equal(t, TransactionTypeTransferIn, transaction.Type)
				assert.Equal(t, 1000.50, transaction.Amount)
				assert.Equal(t, []string{"餐饮"}, transaction.Categorys)
				assert.Equal(t, []string{"午餐"}, transaction.Tags)
				assert.Equal(t, "测试描述1", transaction.Desc)
			},
		},
		{
			name:    "多个类别",
			record:  []string{"2025-01-02", "支出", "25.99", "餐饮,晚饭", "", "测试描述2"},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, TransactionTypeExpense, transaction.Type)
				assert.Equal(t, []string{"餐饮", "晚饭"}, transaction.Categorys)
				assert.Empty(t, transaction.Tags)
			},
		},
		{
			name:    "多个标签",
			record:  []string{"2025-01-03", "转出", "500.00", "对齐", "标签1,标签2", "测试描述3"},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, TransactionTypeTransferOut, transaction.Type)
				assert.Equal(t, []string{"对齐"}, transaction.Categorys)
				assert.Equal(t, []string{"标签1", "标签2"}, transaction.Tags)
			},
		},
		{
			name:    "带空格的数据",
			record:  []string{"2025-01-01 ", " 转入 ", " 1000.50 ", "餐饮,晚饭", "标签1,标签2", " 测试描述 "},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC), transaction.Date)
				assert.Equal(t, TransactionTypeTransferIn, transaction.Type)
				assert.Equal(t, 1000.50, transaction.Amount)
				assert.Equal(t, []string{"餐饮", "晚饭"}, transaction.Categorys)
				assert.Equal(t, []string{"标签1", "标签2"}, transaction.Tags)
				assert.Equal(t, "测试描述", transaction.Desc)
			},
		},
		{
			name:    "空的类别和标签",
			record:  []string{"2025-01-01", "收入", "100.00", "", "", ""},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, TransactionTypeIncome, transaction.Type)
				assert.Empty(t, transaction.Categorys)
				assert.Empty(t, transaction.Tags)
				assert.Empty(t, transaction.Desc)
			},
		},
		{
			name:    "只有类别",
			record:  []string{"2025-01-02", "支出", "50.00", "餐饮", "", ""},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, TransactionTypeExpense, transaction.Type)
				assert.Equal(t, []string{"餐饮"}, transaction.Categorys)
				assert.Empty(t, transaction.Tags)
			},
		},
		{
			name:    "类别和标签中的空格",
			record:  []string{"2025-01-01", "支出", "100.00", " 餐饮 , 晚饭 ", " 标签1 , 标签2 ", "描述"},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, []string{"餐饮", "晚饭"}, transaction.Categorys)
				assert.Equal(t, []string{"标签1", "标签2"}, transaction.Tags)
			},
		},
		{
			name:        "无效日期",
			record:      []string{"2025-13-45", "转入", "1000.00", "测试", "", "测试"},
			wantErr:     true,
			errContains: "invalid date",
		},
		{
			name:        "无效金额",
			record:      []string{"2025-01-01", "转入", "not_a_number", "测试", "", "测试"},
			wantErr:     true,
			errContains: "invalid amount",
		},
		{
			name:        "字段不足",
			record:      []string{"2025-01-01", "转入", "1000.00"},
			wantErr:     true,
			errContains: "expected 6 fields",
		},
		{
			name:        "空记录",
			record:      []string{},
			wantErr:     true,
			errContains: "expected 6 fields",
		},
		{
			name:        "只有3个字段",
			record:      []string{"2025-01-01", "转入", "1000.00"},
			wantErr:     true,
			errContains: "expected 6 fields",
		},
	}

	// 测试所有交易类型
	transactionTypes := []struct {
		name     string
		typeStr  string
		expected TransactionType
	}{
		{"收入类型", "收入", TransactionTypeIncome},
		{"支出类型", "支出", TransactionTypeExpense},
		{"转入类型", "转入", TransactionTypeTransferIn},
		{"转出类型", "转出", TransactionTypeTransferOut},
	}

	for _, tt := range transactionTypes {
		testCases = append(testCases, struct {
			name        string
			record      []string
			wantErr     bool
			errContains string
			validate    func(t *testing.T, transaction *Transaction)
		}{
			name:    tt.name,
			record:  []string{"2025-01-01", tt.typeStr, "100.00", "测试", "", ""},
			wantErr: false,
			validate: func(t *testing.T, transaction *Transaction) {
				assert.Equal(t, tt.expected, transaction.Type)
			},
		})
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			transaction, err := unmarshalRow(tc.record)

			if tc.wantErr {
				assert.Error(t, err)
				assert.Nil(t, transaction)
				if tc.errContains != "" {
					assert.Contains(t, err.Error(), tc.errContains)
				}
			} else {
				assert.NoError(t, err)
				assert.NotNil(t, transaction)
				if tc.validate != nil {
					tc.validate(t, transaction)
				}
			}
		})
	}
}

// ========== loadTable 集成测试 ==========

func TestLoadTable(t *testing.T) {
	testCases := []struct {
		name        string
		fixtureFile string
		wantErr     bool
		errContains string
		wantLen     int
		validate    func(t *testing.T, transactions []*Transaction)
	}{
		{
			name:        "正常情况",
			fixtureFile: "normal.csv",
			wantErr:     false,
			wantLen:     3,
			validate: func(t *testing.T, transactions []*Transaction) {
				assert.NotNil(t, transactions)
			},
		},
		{
			name:        "空文件",
			fixtureFile: "empty.csv",
			wantErr:     false,
			wantLen:     0,
			validate: func(t *testing.T, transactions []*Transaction) {
				assert.NotNil(t, transactions)
			},
		},
		{
			name:        "只有表头",
			fixtureFile: "header_only.csv",
			wantErr:     false,
			wantLen:     0,
			validate: func(t *testing.T, transactions []*Transaction) {
				assert.NotNil(t, transactions)
			},
		},
		{
			name:        "文件不存在",
			fixtureFile: "nonexistent.csv",
			wantErr:     true,
			errContains: "failed to open file",
			wantLen:     0,
			validate: func(t *testing.T, transactions []*Transaction) {
				assert.Nil(t, transactions)
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			fixturePath := filepath.Join("..", "..", "..", "test", "fixtures", "transaction", "loadTable", tc.fixtureFile)
			filePath, err := filepath.Abs(fixturePath)
			assert.NoError(t, err)

			transactions, err := loadTable(filePath)

			if tc.wantErr {
				assert.Error(t, err)
				if tc.errContains != "" {
					assert.Contains(t, err.Error(), tc.errContains)
				}
			} else {
				assert.NoError(t, err)
			}

			if tc.wantLen >= 0 {
				if transactions != nil {
					assert.Len(t, transactions, tc.wantLen)
				} else {
					assert.Equal(t, tc.wantLen, 0)
				}
			}

			if tc.validate != nil {
				tc.validate(t, transactions)
			}
		})
	}
}
