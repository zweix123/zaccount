package handler

import (
	"fmt"
	"net/http"
	"os"

	logger "github.com/zweix123/zaccount/backend/common/logger"
	"github.com/zweix123/zaccount/backend/common/util"
)

const (
	Port = "8080" // 服务器端口
)

var webPath = util.GetRalePath("..", "..", "..", "web")

func Init() error {
	if _, err := os.Stat(webPath); os.IsNotExist(err) {
		return fmt.Errorf("web directory not found: %s", webPath)
	}
	// 注册文件服务(页面后端)
	fileServer := http.FileServer(http.Dir(webPath))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			http.ServeFile(w, r, fmt.Sprintf("%s/index.html", webPath))
			return
		}
		fileServer.ServeHTTP(w, r)
	})

	// 注册API服务(业务后端)
	http.HandleFunc("/test", HandleTest)
	http.HandleFunc("/config/init", HandleConfigInit)
	http.HandleFunc("/display/common", HandleDisplayCommonData)

	// 启动服务
	addr := fmt.Sprintf(":%s", Port)
	logger.Debug("server starting, listen on: %s, open in browser: http://localhost:%s", addr, Port)
	return http.ListenAndServe(addr, nil)
}

func HandleTest(w http.ResponseWriter, r *http.Request) {
	logger.Info("request_in||url=%s", r.URL.String())
	w.Write([]byte("test success"))
	logger.Info("response_out||url=%s", r.URL.String())
}
