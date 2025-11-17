package handler

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/zweix123/suger/common"
	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/domain/config"
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

	// 构建domain层请求
	req := &config.GetInitDataRequest{}

	logger.Info("request_in||url=%s||req=%s", r.URL.String(), common.MustJsonMarshal(req))

	// 调用domain层业务逻辑
	resp, err := config.GetInitData(ctx, req)
	if err != nil {
		// 处理业务层错误
		logger.Error("Failed to get init data: %v", err)
		http.Error(w, fmt.Sprintf("Business logic error: %s", err.Error()), http.StatusBadRequest)
		return
	}

	logger.Info("response_out||url=%s||resp=%s", r.URL.String(), common.MustJsonMarshal(resp))

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
