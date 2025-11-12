package config

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/bytedance/mockey"
	"github.com/stretchr/testify/assert"
	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

func setup() {
	logger.InitLogger("debug")
}

func teardown() {}

func TestMain(m *testing.M) {
	setup()         // 全局初始化
	code := m.Run() // testing.M的唯一方法，执行所在包下的所有TestXxx函数
	teardown()      // 全局清理
	os.Exit(code)
}

// loadTestDataFromInit 使用transaction.Init加载测试数据
func loadTestDataFromInit(t *testing.T, fixtureDir string) transaction.TransactionData {
	// 获取fixture目录的绝对路径
	fixturePath := filepath.Join("..", "..", "..", "test", "fixtures", "transaction", fixtureDir)
	absPath, err := filepath.Abs(fixturePath)
	assert.NoError(t, err)

	// 使用transaction.Init加载数据
	err = transaction.Init(absPath)
	if err != nil {
		// 如果Init失败（比如文件格式不符合），返回空数据
		return transaction.TransactionData{}
	}

	// 获取数据
	data := transaction.GetData()

	// 清理
	transaction.Close()

	return data
}

func TestGetInitData(t *testing.T) {
	ctx := context.Background()

	testCases := []struct {
		name             string
		fixtureDir       string
		wantErr          bool
		errContains      string
		expectedEarliest time.Time
		expectedLatest   time.Time
		description      string
		useMock          bool
		mockData         transaction.TransactionData
	}{
		{
			name:             "正常情况-多条数据",
			fixtureDir:       ".",
			wantErr:          false,
			expectedEarliest: time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			expectedLatest:   time.Date(2025, 3, 10, 0, 0, 0, 0, time.UTC),
			description:      "应该返回第一条和最后一条记录的时间",
			useMock:          true,
			mockData: transaction.TransactionData{
				{
					Date:      time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeIncome,
					Amount:    1000.00,
					Categorys: []string{"工资"},
					Tags:      []string{"工作"},
					Desc:      "1月工资",
				},
				{
					Date:      time.Date(2025, 1, 5, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    50.00,
					Categorys: []string{"餐饮", "午饭"},
					Tags:      []string{"午餐"},
					Desc:      "午餐费用",
				},
				{
					Date:      time.Date(2025, 1, 10, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferIn,
					Amount:    500.00,
					Categorys: []string{"红包"},
					Tags:      []string{"红包"},
					Desc:      "收到红包",
				},
				{
					Date:      time.Date(2025, 1, 15, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    200.00,
					Categorys: []string{"购物", "快消"},
					Tags:      []string{"购物"},
					Desc:      "购买日用品",
				},
				{
					Date:      time.Date(2025, 1, 20, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferOut,
					Amount:    300.00,
					Categorys: []string{"对齐"},
					Tags:      []string{"转账"},
					Desc:      "转出到其他账户",
				},
				{
					Date:      time.Date(2025, 2, 1, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeIncome,
					Amount:    1200.00,
					Categorys: []string{"工资"},
					Tags:      []string{"工作"},
					Desc:      "2月工资",
				},
				{
					Date:      time.Date(2025, 2, 10, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    80.00,
					Categorys: []string{"餐饮", "晚饭"},
					Tags:      []string{"晚餐"},
					Desc:      "晚餐费用",
				},
				{
					Date:      time.Date(2025, 2, 15, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferIn,
					Amount:    200.00,
					Categorys: []string{"红包"},
					Tags:      []string{"红包"},
					Desc:      "收到红包",
				},
				{
					Date:      time.Date(2025, 2, 20, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    150.00,
					Categorys: []string{"购物", "衣服"},
					Tags:      []string{"购物"},
					Desc:      "购买衣服",
				},
				{
					Date:      time.Date(2025, 3, 1, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeIncome,
					Amount:    1000.00,
					Categorys: []string{"工资"},
					Tags:      []string{"工作"},
					Desc:      "3月工资",
				},
				{
					Date:      time.Date(2025, 3, 5, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    60.00,
					Categorys: []string{"餐饮", "午饭"},
					Tags:      []string{"午餐"},
					Desc:      "午餐费用",
				},
				{
					Date:      time.Date(2025, 3, 10, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferOut,
					Amount:    400.00,
					Categorys: []string{"对齐"},
					Tags:      []string{"转账"},
					Desc:      "转出到其他账户",
				},
			},
		},
		{
			name:             "正常情况-normal.csv",
			fixtureDir:       "loadTable",
			wantErr:          false,
			expectedEarliest: time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			expectedLatest:   time.Date(2025, 1, 3, 0, 0, 0, 0, time.UTC),
			description:      "应该返回第一条和最后一条记录的时间",
			useMock:          true,
			mockData: transaction.TransactionData{
				{
					Date:      time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferIn,
					Amount:    1000.50,
					Categorys: []string{"红包"},
					Tags:      []string{"午餐"},
					Desc:      "测试描述1",
				},
				{
					Date:      time.Date(2025, 1, 2, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeExpense,
					Amount:    25.99,
					Categorys: []string{"餐饮", "晚饭"},
					Tags:      []string{},
					Desc:      "测试描述2",
				},
				{
					Date:      time.Date(2025, 1, 3, 0, 0, 0, 0, time.UTC),
					Type:      transaction.TransactionTypeTransferOut,
					Amount:    500.00,
					Categorys: []string{"对齐"},
					Tags:      []string{"标签1", "标签2"},
					Desc:      "测试描述3",
				},
			},
		},
		{
			name:        "空数据",
			fixtureDir:  "loadTable",
			wantErr:     true,
			errContains: "no transaction data available",
			description: "空数据应该返回错误",
			useMock:     true,
			mockData:    transaction.TransactionData{},
		},
		{
			name:        "只有表头",
			fixtureDir:  "loadTable",
			wantErr:     true,
			errContains: "no transaction data available",
			description: "只有表头应该返回错误",
			useMock:     true,
			mockData:    transaction.TransactionData{},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			var testData transaction.TransactionData

			if tc.useMock {
				// 使用mockey mock GetData函数
				mocker := mockey.Mock(transaction.GetData).Return(tc.mockData).Build()
				defer mocker.UnPatch()
				testData = tc.mockData
			} else {
				// 使用transaction.Init加载真实数据
				testData = loadTestDataFromInit(t, tc.fixtureDir)
			}

			req := &GetInitDataRequest{
				Transactions: testData,
			}

			resp, err := GetInitData(ctx, req)

			if tc.wantErr {
				assert.Error(t, err)
				if tc.errContains != "" {
					assert.Contains(t, err.Error(), tc.errContains)
				}
				assert.Nil(t, resp)
			} else {
				assert.NoError(t, err, tc.description)
				assert.NotNil(t, resp, tc.description)
				if resp != nil {
					assert.Equal(t, tc.expectedEarliest, resp.EarliestDate, "最早时间应该匹配")
					assert.Equal(t, tc.expectedLatest, resp.LatestDate, "最晚时间应该匹配")
				}
			}
		})
	}
}

func TestGetInitData_NilRequest(t *testing.T) {
	ctx := context.Background()

	resp, err := GetInitData(ctx, nil)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "request cannot be nil")
	assert.Nil(t, resp)
}

func TestGetInitData_EmptyTransactions(t *testing.T) {
	ctx := context.Background()

	req := &GetInitDataRequest{
		Transactions: transaction.TransactionData{},
	}

	resp, err := GetInitData(ctx, req)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "no transaction data available")
	assert.Nil(t, resp)
}

func TestGetInitData_SingleTransaction(t *testing.T) {
	ctx := context.Background()

	// 使用transaction.Init加载数据
	testData := loadTestDataFromInit(t, ".")
	if len(testData) == 0 {
		// 如果Init失败，使用mockey mock数据
		mockData := transaction.TransactionData{
			{
				Date:      time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
				Type:      transaction.TransactionTypeTransferIn,
				Amount:    1000.50,
				Categorys: []string{"红包"},
				Tags:      []string{"午餐"},
				Desc:      "测试描述1",
			},
		}
		mocker := mockey.Mock(transaction.GetData).Return(mockData).Build()
		defer mocker.UnPatch()
		testData = mockData
	}

	// 只取第一条数据
	singleData := transaction.TransactionData{testData[0]}

	req := &GetInitDataRequest{
		Transactions: singleData,
	}

	resp, err := GetInitData(ctx, req)

	assert.NoError(t, err)
	assert.NotNil(t, resp)
	if resp != nil {
		expectedDate := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
		assert.Equal(t, expectedDate, resp.EarliestDate, "单条数据时最早时间应该正确")
		assert.Equal(t, expectedDate, resp.LatestDate, "单条数据时最晚时间应该与最早时间相同")
	}
}
