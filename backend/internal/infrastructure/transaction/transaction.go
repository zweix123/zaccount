package transaction

import (
	"fmt"
	"time"

	"github.com/zweix123/zaccount/backend/common/logger"
)

// 表头
const (
	DateField      = "date"
	TypeField      = "type"
	AmountField    = "amount"
	CategorysField = "categorys"
	TagsField      = "tags"
	DescField      = "desc"
)

var Fields = []string{
	DateField,
	TypeField,
	AmountField,
	CategorysField,
	TagsField,
	DescField,
}

// 类型枚举
type TransactionType string

const (
	TransactionTypeIncome      TransactionType = "收入"
	TransactionTypeExpense     TransactionType = "支出"
	TransactionTypeTransferIn  TransactionType = "转入"
	TransactionTypeTransferOut TransactionType = "转出"
)

// 有效的交易类型集合
var validTransactionTypes = map[TransactionType]bool{
	TransactionTypeIncome:      true,
	TransactionTypeExpense:     true,
	TransactionTypeTransferIn:  true,
	TransactionTypeTransferOut: true,
}

// IsValidTransactionType 检查给定的 TransactionType 是否是有效的枚举值
func IsValidTransactionType(t TransactionType) bool {
	return validTransactionTypes[t]
}

// 交易表的行的数据结构
type Transaction struct {
	Date      time.Time
	Type      TransactionType
	Amount    float64
	Categorys []string
	Tags      []string
	Desc      string
}

type TransactionData []*Transaction

type TransactionTable struct {
	filePath string
	data     TransactionData
}

var globalTransactionTable *TransactionTable

func Init(dataPath string) error {
	filePath, err := findAndCopyTableFile(dataPath, "transaction")
	if err != nil {
		return fmt.Errorf("failed to find and copy table file: %w", err)
	}
	table, err := readTable(filePath)
	if err != nil {
		return fmt.Errorf("failed to load table: %w", err)
	}
	globalTransactionTable = &TransactionTable{
		filePath: filePath,
		data:     table,
	}
	logger.Debug("load table success, row number: %d", len(table))
	return nil
}

func Close() error {
	err := updateTable(globalTransactionTable.filePath)
	if err != nil {
		return fmt.Errorf("failed to update table: %w", err)
	}
	logger.Debug("update table success, row number: %d", len(globalTransactionTable.data))
	globalTransactionTable = nil
	return nil
}

func Sum() float64 {
	return globalTransactionTable.data.Sum()
}
