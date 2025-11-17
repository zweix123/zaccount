package main

import (
	"flag"
	"fmt"

	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/common/util"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

var dataPathRelative = util.GetRalePath([]string{"..", "..", "..", "data"}...) // 数据目录相对路径

var (
	logLevel = flag.String("log-level", "info", "log level, debug, info, warn, error")
	dataPath = flag.String("data-path", dataPathRelative, "data path")
)

func main() {
	flag.Parse()
	logger.InitLogger(*logLevel)

	logger.Debug("table dir path: %s", *dataPath)
	if err := transaction.Init(*dataPath); err != nil {
		logger.Error("transaction init failed, err is %s", err.Error())
		return
	}
	defer transaction.Close()

	fmt.Printf("sum: %.2f\n", transaction.GetData().Sum())
}
