package config

import (
	"context"
	"errors"
	"time"

	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

// InitRequest 获取初始化数据请求
type InitRequest struct{}

// InitResponse 获取初始化数据响应
type InitResponse struct {
	EarliestDate time.Time // 最早时间（第一个元素的时间）
	LatestDate   time.Time // 最晚时间（最后一个元素的时间）
}

func Init(ctx context.Context, req *InitRequest) (*InitResponse, error) {
	if req == nil {
		return nil, errors.New("request cannot be nil")
	}

	if len(transaction.GetData()) == 0 {
		return nil, errors.New("no transaction data available")
	}

	earliestDate := transaction.GetData()[0].Date
	latestDate := transaction.GetData()[len(transaction.GetData())-1].Date

	// 日期转换
	earliestDateOnly := time.Date(earliestDate.Year(), earliestDate.Month(), earliestDate.Day(), 0, 0, 0, 0, earliestDate.Location())
	latestDateOnly := time.Date(latestDate.Year(), latestDate.Month(), latestDate.Day(), 0, 0, 0, 0, latestDate.Location())

	return &InitResponse{
		EarliestDate: earliestDateOnly,
		LatestDate:   latestDateOnly,
	}, nil
}
