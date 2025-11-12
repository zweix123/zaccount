package transaction

import (
	"path/filepath"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

// loadTestData 从fixture文件加载测试数据
func loadTestData(t *testing.T, fixtureFile string) TransactionData {
	fixturePath := filepath.Join("..", "..", "..", "test", "fixtures", "transaction", fixtureFile)
	filePath, err := filepath.Abs(fixturePath)
	assert.NoError(t, err)

	transactions, err := readTable(filePath)
	assert.NoError(t, err)
	assert.NotNil(t, transactions)

	return transactions
}

func TestFilterByDateRange(t *testing.T) {
	testData := loadTestData(t, "opt_test.csv")

	testCases := []struct {
		name           string
		startDate      time.Time
		endDate        time.Time
		expectedCount  int
		expectedDates  []time.Time
		validate       func(t *testing.T, filtered TransactionData)
	}{
		{
			name:          "过滤1月份数据",
			startDate:     time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 1, 31, 0, 0, 0, 0, time.UTC),
			expectedCount: 5,
			validate: func(t *testing.T, filtered TransactionData) {
				// 验证所有日期都在1月
				for _, tx := range filtered {
					assert.Equal(t, 1, int(tx.Date.Month()))
					assert.Equal(t, 2025, tx.Date.Year())
				}
			},
		},
		{
			name:          "过滤2月份数据",
			startDate:     time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC),
			expectedCount: 4,
			validate: func(t *testing.T, filtered TransactionData) {
				// 验证所有日期都在2月
				for _, tx := range filtered {
					assert.Equal(t, 2, int(tx.Date.Month()))
					assert.Equal(t, 2025, tx.Date.Year())
				}
			},
		},
		{
			name:          "过滤跨月数据",
			startDate:     time.Date(2025, 1, 15, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 2, 15, 0, 0, 0, 0, time.UTC),
			expectedCount: 5, // 1月15日、1月20日、2月1日、2月10日、2月15日
			validate: func(t *testing.T, filtered TransactionData) {
				// 验证日期范围
				for _, tx := range filtered {
					assert.True(t, !tx.Date.Before(time.Date(2025, 1, 15, 0, 0, 0, 0, time.UTC)) &&
						!tx.Date.After(time.Date(2025, 2, 15, 0, 0, 0, 0, time.UTC)))
				}
			},
		},
		{
			name:          "单日过滤",
			startDate:     time.Date(2025, 1, 10, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 1, 10, 0, 0, 0, 0, time.UTC),
			expectedCount: 1,
			validate: func(t *testing.T, filtered TransactionData) {
				assert.Equal(t, time.Date(2025, 1, 10, 0, 0, 0, 0, time.UTC), filtered[0].Date)
				assert.Equal(t, TransactionTypeTransferIn, filtered[0].Type)
			},
		},
		{
			name:          "空范围过滤",
			startDate:     time.Date(2025, 12, 1, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 12, 31, 0, 0, 0, 0, time.UTC),
			expectedCount: 0,
			validate: func(t *testing.T, filtered TransactionData) {
				assert.Empty(t, filtered)
			},
		},
		{
			name:          "包含边界日期",
			startDate:     time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			endDate:       time.Date(2025, 1, 5, 0, 0, 0, 0, time.UTC),
			expectedCount: 2,
			validate: func(t *testing.T, filtered TransactionData) {
				// 应该包含1月1日和1月5日的数据
				dates := make(map[time.Time]bool)
				for _, tx := range filtered {
					dates[tx.Date] = true
				}
				assert.True(t, dates[time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)])
				assert.True(t, dates[time.Date(2025, 1, 5, 0, 0, 0, 0, time.UTC)])
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			filtered := testData.FilterByDateRange(tc.startDate, tc.endDate)
			assert.Len(t, filtered, tc.expectedCount)
			if tc.validate != nil {
				tc.validate(t, filtered)
			}
		})
	}
}

func TestCalculateIncome(t *testing.T) {
	testData := loadTestData(t, "opt_test.csv")

	testCases := []struct {
		name          string
		data          TransactionData
		expectedIncome float64
		description   string
	}{
		{
			name:          "计算所有收入",
			data:          testData,
			expectedIncome: 3900.00, // 1000 + 1200 + 1000 (收入) + 500 + 200 (转入)
			description:   "应该包含所有收入和转入",
		},
		{
			name:          "只计算1月份收入",
			data:          testData.FilterByDateRange(time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 1, 31, 0, 0, 0, 0, time.UTC)),
			expectedIncome: 1500.00, // 1000 (收入) + 500 (转入)
			description:   "1月份的收入和转入",
		},
		{
			name:          "只计算2月份收入",
			data:          testData.FilterByDateRange(time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)),
			expectedIncome: 1400.00, // 1200 (收入) + 200 (转入)
			description:   "2月份的收入和转入",
		},
		{
			name:          "空数据",
			data:          TransactionData{},
			expectedIncome: 0.0,
			description:   "空数据应该返回0",
		},
		{
			name:          "只有支出和转出",
			data:          testData.FilterByDateRange(time.Date(2025, 1, 5, 0, 0, 0, 0, time.UTC), time.Date(2025, 1, 5, 0, 0, 0, 0, time.UTC)),
			expectedIncome: 0.0,
			description:   "只有支出，没有收入",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			income := tc.data.CalculateIncome()
			assert.InDelta(t, tc.expectedIncome, income, 0.01, tc.description)
		})
	}
}

func TestCalculateExpense(t *testing.T) {
	testData := loadTestData(t, "opt_test.csv")

	testCases := []struct {
		name           string
		data           TransactionData
		expectedExpense float64
		description    string
	}{
		{
			name:           "计算所有支出",
			data:           testData,
			expectedExpense: 1240.00, // 50 + 200 + 80 + 150 + 60 + 300 + 400 (转出)
			description:    "应该包含所有支出和转出",
		},
		{
			name:           "只计算1月份支出",
			data:           testData.FilterByDateRange(time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 1, 31, 0, 0, 0, 0, time.UTC)),
			expectedExpense: 550.00, // 50 + 200 + 300 (转出)
			description:    "1月份的支出和转出",
		},
		{
			name:           "只计算2月份支出",
			data:           testData.FilterByDateRange(time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 2, 28, 0, 0, 0, 0, time.UTC)),
			expectedExpense: 230.00, // 80 + 150
			description:    "2月份的支出和转出",
		},
		{
			name:           "只计算3月份支出",
			data:           testData.FilterByDateRange(time.Date(2025, 3, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 3, 31, 0, 0, 0, 0, time.UTC)),
			expectedExpense: 460.00, // 60 + 400 (转出)
			description:    "3月份的支出和转出",
		},
		{
			name:           "空数据",
			data:           TransactionData{},
			expectedExpense: 0.0,
			description:    "空数据应该返回0",
		},
		{
			name:           "只有收入和转入",
			data:           testData.FilterByDateRange(time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC), time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)),
			expectedExpense: 0.0,
			description:    "只有收入，没有支出",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			expense := tc.data.CalculateExpense()
			assert.InDelta(t, tc.expectedExpense, expense, 0.01, tc.description)
		})
	}
}

func TestFilterByDateRangeAndCalculate(t *testing.T) {
	testData := loadTestData(t, "opt_test.csv")

	// 测试组合使用：先过滤再计算
	t.Run("组合测试-1月份收支", func(t *testing.T) {
		filtered := testData.FilterByDateRange(
			time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			time.Date(2025, 1, 31, 0, 0, 0, 0, time.UTC),
		)

		income := filtered.CalculateIncome()
		expense := filtered.CalculateExpense()
		balance := income - expense

		assert.InDelta(t, 1500.00, income, 0.01, "1月份收入应该是1500")
		assert.InDelta(t, 550.00, expense, 0.01, "1月份支出应该是550")
		assert.InDelta(t, 950.00, balance, 0.01, "1月份结余应该是950")
	})

	t.Run("组合测试-全年度收支", func(t *testing.T) {
		filtered := testData.FilterByDateRange(
			time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			time.Date(2025, 12, 31, 0, 0, 0, 0, time.UTC),
		)

		income := filtered.CalculateIncome()
		expense := filtered.CalculateExpense()
		balance := income - expense

		assert.InDelta(t, 3900.00, income, 0.01, "全年收入应该是3900")
		assert.InDelta(t, 1240.00, expense, 0.01, "全年支出应该是1240")
		assert.InDelta(t, 2660.00, balance, 0.01, "全年结余应该是2660")
	})
}

