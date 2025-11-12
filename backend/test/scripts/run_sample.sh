#!/bin/bash

# 示例脚本
# 1. 启动后端服务器
# 2. 等待服务器就绪
# 3. 访问所有现有接口
# 4. 清理：停止后端服务器

set -e  # 遇到错误立即退出

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取 backend 目录的绝对路径（脚本在 backend/test/scripts 下，所以需要向上两级）
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# 获取项目根目录
PROJECT_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"
# 真实数据目录（项目根目录下的 data 目录）
DATA_DIR="$(cd "$PROJECT_ROOT/data" && pwd)"

# 服务器配置
SERVER_PORT=8080
SERVER_URL="http://localhost:${SERVER_PORT}"
MAX_WAIT_TIME=30  # 最大等待时间（秒）

# 后端服务器进程 ID
SERVER_PID=""

# 清理函数：停止后端服务器并释放端口
cleanup() {
    echo ""
    echo "开始清理..."
    
    # 清理主进程
    if [ -n "$SERVER_PID" ]; then
        echo "正在停止后端服务器 (PID: $SERVER_PID)..."
        # 先尝试优雅终止
        kill "$SERVER_PID" 2>/dev/null || true
        sleep 1
        # 如果进程还在运行，强制终止
        if kill -0 "$SERVER_PID" 2>/dev/null; then
            echo "进程仍在运行，强制终止..."
            kill -9 "$SERVER_PID" 2>/dev/null || true
        fi
        wait "$SERVER_PID" 2>/dev/null || true
        echo "后端服务器进程已停止"
    fi
    
    # 清理所有占用端口的进程（包括可能的子进程）
    if check_port; then
        echo "检测到端口 ${SERVER_PORT} 仍被占用，清理所有占用该端口的进程..."
        if command -v lsof >/dev/null 2>&1; then
            PIDS=$(lsof -ti:${SERVER_PORT} 2>/dev/null || true)
            if [ -n "$PIDS" ]; then
                for pid in $PIDS; do
                    if [ "$pid" != "$$" ]; then  # 不终止自己
                        echo "终止占用端口的进程: $pid"
                        kill -9 "$pid" 2>/dev/null || true
                    fi
                done
                sleep 2  # 等待端口释放
            fi
        fi
        
        # 再次检查端口是否已释放
        if check_port; then
            echo "⚠️  警告: 端口 ${SERVER_PORT} 可能仍被占用"
        else
            echo "✓ 端口 ${SERVER_PORT} 已释放"
        fi
    else
        echo "✓ 端口 ${SERVER_PORT} 已释放"
    fi
}

# 注册清理函数，确保脚本退出时（包括异常退出）都会执行清理
trap cleanup EXIT INT TERM

# 检查端口是否被占用
check_port() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:${SERVER_PORT} >/dev/null 2>&1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -an | grep -q ":${SERVER_PORT}.*LISTEN" 2>/dev/null
    else
        # 如果都没有，尝试连接测试
        timeout 1 bash -c "echo > /dev/tcp/localhost/${SERVER_PORT}" 2>/dev/null
    fi
}

# 检查服务器是否就绪（通过 HTTP 请求）
check_server_ready() {
    if command -v curl >/dev/null 2>&1; then
        curl -s -f -o /dev/null "${SERVER_URL}/test" 2>/dev/null
    elif command -v wget >/dev/null 2>&1; then
        wget -q -O /dev/null "${SERVER_URL}/test" 2>/dev/null
    else
        # 如果都没有，只检查端口
        check_port
    fi
}

# 等待服务器启动
wait_for_server() {
    echo "等待服务器启动..."
    local waited=0
    while [ $waited -lt $MAX_WAIT_TIME ]; do
        if check_server_ready; then
            echo ""
            echo "✓ 服务器已启动并就绪 (端口 ${SERVER_PORT})"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
        echo -n "."
    done
    echo ""
    echo "❌ 服务器启动超时（等待了 ${MAX_WAIT_TIME} 秒）"
    return 1
}

# 发送HTTP请求并显示结果
send_request() {
    local url=$1
    local description=$2
    
    echo ""
    echo "=========================================="
    echo "$description"
    echo "=========================================="
    echo "URL: $url"
    echo ""
    
    if command -v curl >/dev/null 2>&1; then
        echo "响应:"
        curl -s -w "\nHTTP状态码: %{http_code}\n" "$url" | head -20
    elif command -v wget >/dev/null 2>&1; then
        echo "响应:"
        wget -q -O - "$url" | head -20
        echo ""
        echo "HTTP状态码: 200 (wget 不显示状态码)"
    else
        echo "❌ 未找到 curl 或 wget，无法发送请求"
        return 1
    fi
    echo ""
}

echo "=========================================="
echo "启动服务并访问所有接口示例"
echo "=========================================="
echo "Backend 目录: $BACKEND_DIR"
echo "数据目录: $DATA_DIR"
echo ""

# 检查是否已有服务器在运行
if check_port; then
    echo "⚠️  警告: 端口 ${SERVER_PORT} 已被占用"
    echo "   尝试清理占用该端口的进程..."
    
    # 尝试清理占用端口的进程
    if command -v lsof >/dev/null 2>&1; then
        PIDS=$(lsof -ti:${SERVER_PORT} 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            for pid in $PIDS; do
                echo "   终止占用端口的进程: $pid"
                kill -9 "$pid" 2>/dev/null || true
            done
            sleep 2  # 等待端口释放
        fi
    fi
    
    # 再次检查端口
    if check_port; then
        echo "❌ 无法释放端口 ${SERVER_PORT}，请手动停止占用该端口的进程"
        exit 1
    else
        echo "✓ 端口 ${SERVER_PORT} 已释放"
    fi
fi

# 准备数据目录
echo "准备数据目录..."
echo "数据目录: $DATA_DIR"
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ 数据目录不存在: $DATA_DIR"
    exit 1
fi

# 检查数据文件是否存在
DATA_FILE=$(find "$DATA_DIR" -name "transaction_*.csv" | head -1)
if [ -z "$DATA_FILE" ]; then
    echo "❌ 未找到数据文件 (transaction_*.csv)"
    exit 1
fi
echo "使用数据文件: $DATA_FILE"
echo ""

# 启动后端服务器
echo "启动后端服务器..."
echo "使用数据目录: $DATA_DIR"
cd "$BACKEND_DIR"
go run cmd/api/main.go --data-path="$DATA_DIR" --log-level=debug > /tmp/backend_server.log 2>&1 &
SERVER_PID=$!

echo "后端服务器进程 ID: $SERVER_PID"
echo "日志文件: /tmp/backend_server.log"
echo ""

# 等待服务器启动
if ! wait_for_server; then
    echo "服务器启动失败，查看日志:"
    tail -20 /tmp/backend_server.log
    exit 1
fi

# 访问所有接口
echo ""
echo "=========================================="
echo "访问所有接口"
echo "=========================================="
echo ""

# 1. 访问 /test 接口
send_request "${SERVER_URL}/test" "接口 1: /test (GET, 无参数)"

# 2. 访问 /config/init 接口
send_request "${SERVER_URL}/config/init" "接口 2: /config/init (GET, 无参数)"

# 3. 访问 /analyze 接口（需要日期参数）
# 从数据文件中获取日期范围
EARLIEST_DATE=$(ls "$DATA_DIR"/transaction_*.csv 2>/dev/null | head -1 | xargs basename | sed 's/transaction_\(.*\)\.csv/\1/')
LATEST_DATE=$(ls "$DATA_DIR"/transaction_*.csv 2>/dev/null | tail -1 | xargs basename | sed 's/transaction_\(.*\)\.csv/\1/')

# 如果没有找到日期，使用默认值
if [ -z "$EARLIEST_DATE" ] || [ -z "$LATEST_DATE" ]; then
    EARLIEST_DATE="2025-10-29"
    LATEST_DATE="2025-11-12"
fi

echo ""
echo "=========================================="
echo "接口 3: /analyze (GET, 需要 start_date 和 end_date 参数)"
echo "=========================================="
echo "URL: ${SERVER_URL}/analyze?start_date=${EARLIEST_DATE}&end_date=${LATEST_DATE}"
echo ""

if command -v curl >/dev/null 2>&1; then
    echo "响应:"
    curl -s -w "\nHTTP状态码: %{http_code}\n" "${SERVER_URL}/analyze?start_date=${EARLIEST_DATE}&end_date=${LATEST_DATE}" | head -20
elif command -v wget >/dev/null 2>&1; then
    echo "响应:"
    wget -q -O - "${SERVER_URL}/analyze?start_date=${EARLIEST_DATE}&end_date=${LATEST_DATE}" | head -20
    echo ""
    echo "HTTP状态码: 200 (wget 不显示状态码)"
else
    echo "❌ 未找到 curl 或 wget，无法发送请求"
fi
echo ""

# 完成
echo ""
echo "=========================================="
echo "✓ 所有接口访问完成"
echo "=========================================="
echo ""
echo "服务器仍在运行，日志文件: /tmp/backend_server.log"
echo "按 Ctrl+C 停止服务器并退出"
echo ""

# 等待用户中断或保持运行
wait $SERVER_PID 2>/dev/null || true

