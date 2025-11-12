package logger

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"runtime"
	"strings"
)

const (
	callDepth = 4
)

type CustomHandler struct {
	handler slog.Handler
	opts    *slog.HandlerOptions
}

func NewCustomHandler(opts *slog.HandlerOptions) *CustomHandler {
	if opts == nil {
		opts = &slog.HandlerOptions{}
	}
	return &CustomHandler{
		opts: opts,
	}
}

func (h *CustomHandler) Enabled(ctx context.Context, level slog.Level) bool { // 实现接口
	if h.opts.Level != nil {
		return level >= h.opts.Level.Level()
	}
	return true
}

func (h *CustomHandler) WithAttrs(attrs []slog.Attr) slog.Handler { // 实现接口
	return &CustomHandler{
		opts: h.opts,
	}
}

func (h *CustomHandler) WithGroup(name string) slog.Handler { // 实现接口
	return &CustomHandler{
		opts: h.opts,
	}
}

func (h *CustomHandler) Handle(ctx context.Context, r slog.Record) error { // 接口实现
	var level string
	switch r.Level {
	case slog.LevelDebug:
		level = "DEBUG"
	case slog.LevelInfo:
		level = "INFO"
	case slog.LevelWarn:
		level = "WARN"
	case slog.LevelError:
		level = "ERROR"
	default:
		level = "INFO"
	}

	// 获取时间
	timeStr := r.Time.Format("2006-01-02 15:04:05.000")

	// 获取代码位置
	var codeStr string
	pc, f, n, ok := runtime.Caller(callDepth)
	if ok {
		f = filepath.Base(f)
		dir := runtime.FuncForPC(pc).Name()
		codeStr = fmt.Sprintf("%s/%s:%d", dir, f, n)
	} else {
		codeStr = "???:0"
	}

	// 处理附加属性
	var attrsStr string
	if r.NumAttrs() > 0 {
		attrs := make([]string, 0)
		r.Attrs(func(attr slog.Attr) bool {
			attrs = append(attrs, fmt.Sprintf("%s=%v", attr.Key, attr.Value.Any()))
			return true
		})
		if len(attrs) > 0 {
			attrsStr = strings.Join(attrs, "||")
		}
	}

	var logLine string
	if len(attrsStr) == 0 {
		logLine = fmt.Sprintf("[%s][%s][%s]%s", level, timeStr, codeStr, r.Message)
	} else {
		logLine = fmt.Sprintf("[%s][%s][%s]%s||%s", level, timeStr, codeStr, r.Message, attrsStr)
	}

	// 输出到标准输出
	fmt.Fprintln(os.Stdout, logLine)
	return nil
}
