package display

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

// calculateExpenseEveryYear 计算每年支出
// 左区间向前取整到年初（1月1日），右区间向后取整到年末（12月31日）
func calculateExpenseEveryYear(transactions transaction.TransactionData, startDate, endDate time.Time) []ExpenseDataPoint {
	// 计算开始年份和结束年份
	startYear := startDate.Year()
	endYear := endDate.Year()

	// 如果开始日期不是1月1日，向前取整到年初
	yearStart := time.Date(startYear, 1, 1, 0, 0, 0, 0, startDate.Location())
	// 如果结束日期不是12月31日，向后取整到年末
	yearEnd := time.Date(endYear, 12, 31, 23, 59, 59, 999999999, endDate.Location())

	var result []ExpenseDataPoint
	for year := startYear; year <= endYear; year++ {
		// 计算该年的开始和结束日期
		yearStartDate := time.Date(year, 1, 1, 0, 0, 0, 0, startDate.Location())
		yearEndDate := time.Date(year, 12, 31, 23, 59, 59, 999999999, endDate.Location())

		// 如果是第一年，使用实际的开始日期（已取整到年初）
		if year == startYear {
			yearStartDate = yearStart
		}
		// 如果是最后一年，使用实际的结束日期（已取整到年末）
		if year == endYear {
			yearEndDate = yearEnd
		}

		// 过滤该年的交易并计算支出
		yearTransactions := transactions.FilterByDateRange(yearStartDate, yearEndDate)
		expense := yearTransactions.CalculateExpense()

		// 生成标签：年份
		label := fmt.Sprintf("%d年", year)

		result = append(result, ExpenseDataPoint{
			Label: label,
			Value: expense,
		})
	}

	return result
}

// calculateExpenseEveryMonth 计算每月支出
// 左区间向前取整到月初（1日），右区间向后取整到月末（最后一天）
func calculateExpenseEveryMonth(transactions transaction.TransactionData, startDate, endDate time.Time) []ExpenseDataPoint {
	// 计算开始月份和结束月份
	startYear, startMonth, _ := startDate.Date()
	endYear, endMonth, _ := endDate.Date()

	var result []ExpenseDataPoint
	currentDate := time.Date(startYear, startMonth, 1, 0, 0, 0, 0, startDate.Location())

	for {
		currentYear, currentMonth, _ := currentDate.Date()
		if currentYear > endYear || (currentYear == endYear && currentMonth > endMonth) {
			break
		}

		// 计算该月的开始和结束日期
		monthStartDate := time.Date(currentYear, currentMonth, 1, 0, 0, 0, 0, startDate.Location())
		// 计算该月的最后一天
		nextMonth := monthStartDate.AddDate(0, 1, 0)
		monthEndDate := nextMonth.AddDate(0, 0, -1)
		monthEndDate = time.Date(monthEndDate.Year(), monthEndDate.Month(), monthEndDate.Day(), 23, 59, 59, 999999999, endDate.Location())

		// 对于开始月份和结束月份，都使用完整的月份（从1日到月末）
		// 左区间向前取整到月初（1日），右区间向后取整到月末（最后一天）
		// 所以开始月份和结束月份都包含整个月的支出

		// 过滤该月的交易并计算支出
		monthTransactions := transactions.FilterByDateRange(monthStartDate, monthEndDate)
		expense := monthTransactions.CalculateExpense()

		// 生成标签：年月
		label := fmt.Sprintf("%d年%d月", currentYear, int(currentMonth))

		result = append(result, ExpenseDataPoint{
			Label: label,
			Value: expense,
		})

		// 移动到下一个月
		currentDate = nextMonth
	}

	return result
}

// calculateExpenseEveryDay 计算每日支出
// 直接从开始日期到结束日期，每天计算
func calculateExpenseEveryDay(transactions transaction.TransactionData, startDate, endDate time.Time) []ExpenseDataPoint {
	var result []ExpenseDataPoint
	currentDate := startDate

	for !currentDate.After(endDate) {
		dayStart := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 0, 0, 0, 0, startDate.Location())
		dayEnd := time.Date(currentDate.Year(), currentDate.Month(), currentDate.Day(), 23, 59, 59, 999999999, endDate.Location())

		// 过滤当天的交易并计算支出
		dayTransactions := transactions.FilterByDateRange(dayStart, dayEnd)
		expense := dayTransactions.CalculateExpense()

		// 生成标签：月/日
		label := fmt.Sprintf("%d/%d", int(currentDate.Month()), currentDate.Day())

		result = append(result, ExpenseDataPoint{
			Label: label,
			Value: expense,
		})

		// 移动到下一天
		currentDate = currentDate.AddDate(0, 0, 1)
	}

	return result
}

// CommonRequest 计算通用数据请求
type CommonRequest struct {
	StartDate time.Time // 开始日期
	EndDate   time.Time // 结束日期
}

// ExpenseDataPoint 支出数据点，包含值和标签
type ExpenseDataPoint struct {
	Label string  `json:"label"` // 时间标签
	Value float64 `json:"value"` // 支出值
}

// CommonResponse 计算通用数据响应
type CommonResponse struct {
	StartDate time.Time // 开始日期
	EndDate   time.Time // 结束日期

	Income  float64 // 收入
	Expense float64 // 支出
	Balance float64 // 当前结余

	ExpenseEveryYear  []ExpenseDataPoint `json:"expense_every_year"`  // 每年支出
	ExpenseEveryMonth []ExpenseDataPoint `json:"expense_every_month"` // 每月支出
	ExpenseEveryDay   []ExpenseDataPoint `json:"expense_every_day"`   // 每日支出
}

// Common 计算指定时间范围内的通用数据
// 遵循标准协议：funcName(ctx context.Context, req) (resp, err)
func Common(ctx context.Context, req *CommonRequest) (*CommonResponse, error) {
	// 参数验证
	if req == nil {
		return nil, errors.New("request cannot be nil")
	}

	// 验证日期范围
	if req.StartDate.After(req.EndDate) {
		return nil, errors.New("start_date must be before or equal to end_date")
	}

	transactions := transaction.GetData()
	if len(transactions) == 0 {
		return nil, errors.New("no transaction data available")
	}

	// 过滤时间范围内的交易
	filteredTransactions := transactions.FilterByDateRange(req.StartDate, req.EndDate)

	// 计算收入、支出和结余
	income := filteredTransactions.CalculateIncome()
	expense := filteredTransactions.CalculateExpense()
	balance := income - expense

	// 将日期转换为只包含日期部分，忽略时间
	startDateOnly := time.Date(req.StartDate.Year(), req.StartDate.Month(), req.StartDate.Day(), 0, 0, 0, 0, req.StartDate.Location())
	endDateOnly := time.Date(req.EndDate.Year(), req.EndDate.Month(), req.EndDate.Day(), 0, 0, 0, 0, req.EndDate.Location())

	// 计算每年支出：左区间向前取整到年初，右区间向后取整到年末
	expenseEveryYear := calculateExpenseEveryYear(transactions, startDateOnly, endDateOnly)

	// 计算每月支出：左区间向前取整到月初，右区间向后取整到月末
	expenseEveryMonth := calculateExpenseEveryMonth(transactions, startDateOnly, endDateOnly)

	// 计算每日支出：直接从开始日期到结束日期
	expenseEveryDay := calculateExpenseEveryDay(transactions, startDateOnly, endDateOnly)

	return &CommonResponse{
		Income:            income,
		Expense:           expense,
		Balance:           balance,
		StartDate:         startDateOnly,
		EndDate:           endDateOnly,
		ExpenseEveryYear:  expenseEveryYear,
		ExpenseEveryMonth: expenseEveryMonth,
		ExpenseEveryDay:   expenseEveryDay,
	}, nil
}
