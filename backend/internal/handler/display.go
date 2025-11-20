package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/zweix123/suger/common"
	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/domain/display"
)

// DisplayCommonResponse HTTP响应数据结构
type DisplayCommonResponse struct {
	Income            float64                    `json:"income"`              // 收入
	Expense           float64                    `json:"expense"`             // 支出
	Balance           float64                    `json:"balance"`             // 当前结余
	StartDate         string                     `json:"start_date"`          // 开始日期
	EndDate           string                     `json:"end_date"`            // 结束日期
	ExpenseEveryYear  []display.ExpenseDataPoint `json:"expense_every_year"`  // 每年支出
	ExpenseEveryMonth []display.ExpenseDataPoint `json:"expense_every_month"` // 每月支出
	ExpenseEveryDay   []display.ExpenseDataPoint `json:"expense_every_day"`   // 每日支出
}

func HandleDisplayCommonData(w http.ResponseWriter, r *http.Request) {
	// 只处理GET请求
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 创建context
	var ctx context.Context = r.Context()

	// 解析HTTP请求参数
	startDateStr := r.URL.Query().Get("start_date")
	endDateStr := r.URL.Query().Get("end_date")

	if startDateStr == "" || endDateStr == "" {
		http.Error(w, "Missing required parameters: start_date and end_date", http.StatusBadRequest)
		return
	}

	// 解析日期
	startDate, err := time.Parse(time.DateOnly, startDateStr)
	if err != nil {
		http.Error(w, fmt.Sprintf("Invalid start_date format: %s, expected YYYY-MM-DD", err.Error()), http.StatusBadRequest)
		return
	}

	endDate, err := time.Parse(time.DateOnly, endDateStr)
	if err != nil {
		http.Error(w, fmt.Sprintf("Invalid end_date format: %s, expected YYYY-MM-DD", err.Error()), http.StatusBadRequest)
		return
	}

	// 构建domain层请求
	req := &display.CommonRequest{
		StartDate: startDate,
		EndDate:   endDate,
	}

	logger.Info("request_in||url=%s||req=%s", r.URL.String(), common.MustJsonMarshal(req))

	// 调用domain层业务逻辑
	resp, err := display.Common(ctx, req)
	if err != nil {
		// 处理业务层错误
		logger.Error("Failed to calculate common data: %v", err)
		http.Error(w, fmt.Sprintf("Business logic error: %s", err.Error()), http.StatusBadRequest)
		return
	}

	logger.Info("response_out||url=%s||resp=%s", r.URL.String(), common.MustJsonMarshal(resp))

	// 构建HTTP响应
	response := DisplayCommonResponse{
		Income:            resp.Income,
		Expense:           resp.Expense,
		Balance:           resp.Balance,
		StartDate:         startDateStr,
		EndDate:           endDateStr,
		ExpenseEveryYear:  resp.ExpenseEveryYear,
		ExpenseEveryMonth: resp.ExpenseEveryMonth,
		ExpenseEveryDay:   resp.ExpenseEveryDay,
	}

	// 设置响应头为JSON格式
	w.Header().Set("Content-Type", "application/json; charset=utf-8")

	// 序列化为JSON并返回
	if err := json.NewEncoder(w).Encode(response); err != nil {
		logger.Error("Failed to encode JSON response: %v", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
}
