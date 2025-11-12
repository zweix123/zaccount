package logger

import (
	"fmt"
	"log/slog"
	"strings"
)

var Logger *slog.Logger // 全局日志记录器

type LogLevel string // 日志级别类型

const (
	LogLevelDebug LogLevel = "debug"
	LogLevelInfo  LogLevel = "info"
	LogLevelWarn  LogLevel = "warn"
	LogLevelError LogLevel = "error"
)

// InitLogger 初始化日志记录器
// level: 日志级别，可以是 "debug", "info", "warn", "error"
func InitLogger(level string) {
	var logLevel slog.Level

	switch strings.ToLower(level) {
	case string(LogLevelDebug):
		logLevel = slog.LevelDebug
	case string(LogLevelInfo):
		logLevel = slog.LevelInfo
	case string(LogLevelWarn):
		logLevel = slog.LevelWarn
	case string(LogLevelError):
		logLevel = slog.LevelError
	default:
		logLevel = slog.LevelInfo // 默认为 info
	}

	opts := &slog.HandlerOptions{
		Level: logLevel,
	}

	handler := NewCustomHandler(opts)
	Logger = slog.New(handler)
}

func Debug(msg string, args ...any) {
	Logger.Debug(fmt.Sprintf(msg, args...))
}

func Info(msg string, args ...any) {
	Logger.Info(fmt.Sprintf(msg, args...))
}

func Warn(msg string, args ...any) {
	Logger.Warn(fmt.Sprintf(msg, args...))
}

func Error(msg string, args ...any) {
	Logger.Error(fmt.Sprintf(msg, args...))
}
