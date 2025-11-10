package transaction

import (
	"fmt"

	"github.com/zweix123/suger/common"
)

func (data TransactionData) Sum() float64 {
	sum := 0.0
	for _, transaction := range data {
		switch transaction.Type {
		case TransactionTypeIncome:
			sum += transaction.Amount
		case TransactionTypeExpense:
			sum -= transaction.Amount
		case TransactionTypeTransferIn:
			sum += transaction.Amount
		case TransactionTypeTransferOut:
			sum -= transaction.Amount
		default:
			common.Assert(false, fmt.Sprintf("invalid transaction type: %s", transaction.Type))
		}
	}
	return sum
}
