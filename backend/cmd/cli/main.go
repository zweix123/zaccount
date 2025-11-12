package main

import (
	"flag"
	"fmt"

	"github.com/zweix123/zaccount/backend/cmd/common"
	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

var (
	logLevel = flag.String("log-level", "info", "log level, debug, info, warn, error")
	dataPath = flag.String("data-path", common.DataPathRelative, "data path")
)

func main() {
	flag.Parse()
	logger.InitLogger(*logLevel)

	logger.Debug("table dir path: %s", *dataPath)
	transaction.Init(*dataPath)
	defer transaction.Close()

	fmt.Printf("sum: %.2f\n", transaction.GetData().Sum())
}
