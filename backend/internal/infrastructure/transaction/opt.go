package transaction

import (
	"time"
)

// CalculateIncome 计算所有收入和转入的总金额
func (data TransactionData) CalculateIncome() float64 {
	sum := 0.0
	for _, transaction := range data {
		switch transaction.Type {
		case TransactionTypeIncome:
			sum += transaction.Amount
		case TransactionTypeTransferIn:
			sum += transaction.Amount
		}
	}
	return sum
}

// CalculateExpense 计算所有支出和转出的总金额
func (data TransactionData) CalculateExpense() float64 {
	sum := 0.0
	for _, transaction := range data {
		switch transaction.Type {
		case TransactionTypeExpense:
			sum += transaction.Amount
		case TransactionTypeTransferOut:
			sum += transaction.Amount
		}
	}
	return sum
}

func (data TransactionData) Sum() float64 {
	return data.CalculateIncome() - data.CalculateExpense()
}

// FilterByDateRange 按时间范围过滤交易数据
// startDate 和 endDate 应该只包含日期部分，时间部分会被忽略
// 返回在 [startDate, endDate] 范围内的交易（包含边界）
func (data TransactionData) FilterByDateRange(startDate, endDate time.Time) TransactionData {
	// 将日期转换为只包含日期部分，忽略时间
	startDateOnly := time.Date(startDate.Year(), startDate.Month(), startDate.Day(), 0, 0, 0, 0, startDate.Location())
	endDateOnly := time.Date(endDate.Year(), endDate.Month(), endDate.Day(), 0, 0, 0, 0, endDate.Location())

	var filtered TransactionData
	for _, t := range data {
		// 将交易日期转换为只包含日期部分
		tDate := time.Date(t.Date.Year(), t.Date.Month(), t.Date.Day(), 0, 0, 0, 0, t.Date.Location())

		// 检查日期是否在范围内（包含边界）：startDate <= tDate <= endDate
		if !tDate.Before(startDateOnly) && !tDate.After(endDateOnly) {
			filtered = append(filtered, t)
		}
	}
	return filtered
}
