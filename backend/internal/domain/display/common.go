package display

import (
	"context"
	"errors"
	"time"

	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

// CommonRequest 计算通用数据请求
type CommonRequest struct {
	StartDate time.Time // 开始日期
	EndDate   time.Time // 结束日期
}

// CommonResponse 计算通用数据响应
type CommonResponse struct {
	Income    float64   // 收入
	Expense   float64   // 支出
	Balance   float64   // 当前结余
	StartDate time.Time // 开始日期
	EndDate   time.Time // 结束日期
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

	return &CommonResponse{
		Income:    income,
		Expense:   expense,
		Balance:   balance,
		StartDate: startDateOnly,
		EndDate:   endDateOnly,
	}, nil
}
