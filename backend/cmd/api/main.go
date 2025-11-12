package main

import (
	"flag"
	"os"

	"github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/internal/handler"
)

var logLevel = flag.String("log-level", "info", "log level, debug, info, warn, error")

func main() {
	flag.Parse()
	logger.InitLogger(*logLevel)

	if err := handler.Init(); err != nil {
		logger.Error("failed to init handler: %v", err)
		os.Exit(1)
	}
}
