#!/bin/bash

# 开发环境启动脚本
# 分别启动后端和前端服务

set -e

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}启动开发环境${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查后端目录
if [ ! -d "$PROJECT_ROOT/backend" ]; then
    echo -e "${YELLOW}错误: 找不到 backend 目录${NC}"
    exit 1
fi

# 检查前端目录
if [ ! -d "$PROJECT_ROOT/web" ]; then
    echo -e "${YELLOW}错误: 找不到 web 目录${NC}"
    exit 1
fi

# 清理函数：当脚本退出时清理后台进程
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 启动后端
echo -e "${BLUE}启动后端服务 (端口 8080)...${NC}"
cd "$PROJECT_ROOT/backend"
go run ./cmd/api/main.go &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${YELLOW}后端启动失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo ""

# 启动前端
echo -e "${BLUE}启动前端服务 (端口 3000)...${NC}"
cd "$PROJECT_ROOT/web"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}检测到 node_modules 不存在，正在安装依赖...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 2

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${YELLOW}前端启动失败${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开发环境启动完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "后端服务: ${BLUE}http://localhost:8080${NC}"
echo -e "前端服务: ${BLUE}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 等待用户中断
wait

