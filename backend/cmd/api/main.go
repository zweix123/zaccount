package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/zweix123/zaccount/backend/common/util"
)

func main() {
	// 获取 web 目录路径（相对于当前文件位置）
	webPath := util.GetRalePath("..", "..", "..", "web")

	// 检查 web 目录是否存在
	if _, err := os.Stat(webPath); os.IsNotExist(err) {
		log.Fatalf("Web directory not found: %s", webPath)
	}

	// 设置静态文件服务
	fileServer := http.FileServer(http.Dir(webPath))

	// 配置路由
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// 如果是根路径，返回 index.html
		if r.URL.Path == "/" {
			http.ServeFile(w, r, fmt.Sprintf("%s/index.html", webPath))
			return
		}
		// 其他路径直接提供静态文件服务
		fileServer.ServeHTTP(w, r)
	})

	// 启动服务器
	port := "8080"
	if p := os.Getenv("PORT"); p != "" {
		port = p
	}

	addr := fmt.Sprintf(":%s", port)
	fmt.Printf("Server starting on http://localhost%s\n", addr)
	fmt.Printf("Serving files from: %s\n", webPath)

	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
