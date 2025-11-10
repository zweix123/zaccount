package main

import (
	"fmt"

	"github.com/zweix123/zaccount/backend/common/util"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

func main() {
	dataPath := util.GetRalePath("..", "..", "..", "data")
	fmt.Println("table dir path: ", dataPath)
	transaction.Init(dataPath)
	defer transaction.Close()
	fmt.Printf("sum: %.2f\n", transaction.Sum())
}
