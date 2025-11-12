package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/domain/config"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

// ConfigInitResponse HTTP响应数据结构
type ConfigInitResponse struct {
	EarliestDate string `json:"earliest_date"` // 最早时间
	LatestDate   string `json:"latest_date"`   // 最晚时间
}

func HandleConfigInit(w http.ResponseWriter, r *http.Request) {
	// 只处理GET请求
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 创建context
	var ctx context.Context = r.Context()

	// 获取所有交易数据
	allTransactions := transaction.GetData()

	// 构建domain层请求
	req := &config.GetInitDataRequest{
		Transactions: allTransactions,
	}

	// 调用domain层业务逻辑
	resp, err := config.GetInitData(ctx, req)
	if err != nil {
		// 处理业务层错误
		logger.Error("Failed to get init data: %v", err)
		http.Error(w, fmt.Sprintf("Business logic error: %s", err.Error()), http.StatusBadRequest)
		return
	}

	// 构建HTTP响应
	response := ConfigInitResponse{
		EarliestDate: resp.EarliestDate.Format(time.DateOnly),
		LatestDate:   resp.LatestDate.Format(time.DateOnly),
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
