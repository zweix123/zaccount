package config

import (
	"context"
	"errors"
	"time"

	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

// GetInitDataRequest 获取初始化数据请求
type GetInitDataRequest struct{}

// GetInitDataResponse 获取初始化数据响应
type GetInitDataResponse struct {
	EarliestDate time.Time // 最早时间（第一个元素的时间）
	LatestDate   time.Time // 最晚时间（最后一个元素的时间）
}

// GetInitData 获取transaction的最早和最晚时间
// 遵循标准协议：funcName(ctx context.Context, req) (resp, err)
func GetInitData(ctx context.Context, req *GetInitDataRequest) (*GetInitDataResponse, error) {
	// 参数验证
	if req == nil {
		return nil, errors.New("request cannot be nil")
	}

	transactions := transaction.GetData()
	if len(transactions) == 0 {
		return nil, errors.New("no transaction data available")
	}

	// 获取第一个元素的时间（最早时间）
	earliestDate := transactions[0].Date

	// 获取最后一个元素的时间（最晚时间）
	latestDate := transactions[len(transactions)-1].Date

	// 将日期转换为只包含日期部分，忽略时间
	earliestDateOnly := time.Date(earliestDate.Year(), earliestDate.Month(), earliestDate.Day(), 0, 0, 0, 0, earliestDate.Location())
	latestDateOnly := time.Date(latestDate.Year(), latestDate.Month(), latestDate.Day(), 0, 0, 0, 0, latestDate.Location())

	return &GetInitDataResponse{
		EarliestDate: earliestDateOnly,
		LatestDate:   latestDateOnly,
	}, nil
}
