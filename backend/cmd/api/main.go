package main

import (
	"flag"
	"os"

	"github.com/zweix123/zaccount/backend/cmd/common"
	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/handler"
	"github.com/zweix123/zaccount/backend/internal/infrastructure/transaction"
)

var (
	dataPath = flag.String("data-path", common.DataPathRelative, "data path, default: ../data")
	logLevel = flag.String("log-level", "info", "log level, debug, info, warn, error")
)

func main() {
	flag.Parse()
	logger.InitLogger(*logLevel)

	transaction.Init(*dataPath)
	defer transaction.Close()

	if err := handler.Init(); err != nil {
		logger.Error("failed to init handler: %v", err)
		os.Exit(1)
	}
}
