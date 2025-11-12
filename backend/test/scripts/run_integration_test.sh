#!/bin/bash

# 集成测试脚本
# 1. 启动后端服务器
# 2. 等待服务器就绪
# 3. 并行执行所有集成测试
# 4. 清理：停止后端服务器

set -e  # 遇到错误立即退出

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取 backend 目录的绝对路径（脚本在 backend/test/scripts 下，所以需要向上两级）
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# 获取项目根目录
PROJECT_ROOT="$(cd "$BACKEND_DIR/../.." && pwd)"
# 集成测试目录
INTEGRATION_DIR="$(cd "$SCRIPT_DIR/../integration" && pwd)"

# 服务器配置
SERVER_PORT=8080
SERVER_URL="http://localhost:${SERVER_PORT}"
MAX_WAIT_TIME=30  # 最大等待时间（秒）

# 后端服务器进程 ID
SERVER_PID=""

# 清理函数：停止后端服务器
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo ""
        echo "正在停止后端服务器 (PID: $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
        echo "后端服务器已停止"
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

echo "=========================================="
echo "运行 Backend 集成测试"
echo "=========================================="
echo "Backend 目录: $BACKEND_DIR"
echo "集成测试目录: $INTEGRATION_DIR"
echo ""

# 检查是否已有服务器在运行
if check_port; then
    echo "⚠️  警告: 端口 ${SERVER_PORT} 已被占用"
    echo "   如果这是另一个测试实例，请先停止它"
    # 在非交互式环境中自动继续，交互式环境中询问用户
    if [ -t 0 ]; then
        read -p "   是否继续？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "   非交互式环境，自动继续..."
    fi
fi

# 启动后端服务器
echo "启动后端服务器..."
cd "$BACKEND_DIR"
go run cmd/api/main.go > /tmp/backend_server.log 2>&1 &
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

# 查找所有集成测试文件
echo ""
echo "查找集成测试文件..."
TEST_FILES=($(find "$INTEGRATION_DIR" -name "test.py" -type f | sort))

if [ ${#TEST_FILES[@]} -eq 0 ]; then
    echo "❌ 未找到任何集成测试文件 (test.py)"
    exit 1
fi

echo "找到 ${#TEST_FILES[@]} 个测试文件:"
for test_file in "${TEST_FILES[@]}"; do
    echo "  - $test_file"
done
echo ""

# 并行执行所有测试
echo "=========================================="
echo "开始并行执行集成测试"
echo "=========================================="
echo ""

# 存储所有后台任务的 PID
declare -a TEST_PIDS=()
declare -a TEST_NAMES=()

# 启动所有测试（并行）
for test_file in "${TEST_FILES[@]}"; do
    test_name=$(basename $(dirname "$test_file"))
    echo "启动测试: $test_name"
    python3 "$test_file" &
    TEST_PIDS+=($!)
    TEST_NAMES+=("$test_name")
done

# 等待所有测试完成并收集结果
# 暂时禁用 set -e，以便收集所有测试结果
set +e
FAILED_TESTS=()
SUCCESS_TESTS=()

for i in "${!TEST_PIDS[@]}"; do
    pid=${TEST_PIDS[$i]}
    name=${TEST_NAMES[$i]}
    echo ""
    echo "等待测试完成: $name (PID: $pid)"
    if wait $pid; then
        echo "✅ 测试通过: $name"
        SUCCESS_TESTS+=("$name")
    else
        echo "❌ 测试失败: $name"
        FAILED_TESTS+=("$name")
    fi
done

# 重新启用 set -e
set -e

# 输出测试结果摘要
echo ""
echo "=========================================="
echo "测试结果摘要"
echo "=========================================="
echo "总测试数: ${#TEST_FILES[@]}"
echo "通过: ${#SUCCESS_TESTS[@]}"
echo "失败: ${#FAILED_TESTS[@]}"
echo ""

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo "失败的测试:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    echo ""
    echo "=========================================="
    echo "✗ 部分测试失败"
    echo "=========================================="
    exit 1
else
    echo "=========================================="
    echo "✓ 所有测试通过"
    echo "=========================================="
    exit 0
fi

