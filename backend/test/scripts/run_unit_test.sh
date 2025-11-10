#!/bin/bash

# 执行 backend 下所有的 _test.go 单测文件
# 使用 go test -v -cover -race ./...

set -e  # 遇到错误立即退出

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取 backend 目录的绝对路径（脚本在 backend/test/scripts 下，所以需要向上两级）
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "运行 Backend 单元测试"
echo "=========================================="
echo "Backend 目录: $BACKEND_DIR"
echo ""

# 切换到 backend 目录
cd "$BACKEND_DIR"

# 执行测试
echo "执行命令: go test -v -cover -race ./..."
echo ""

go test -v -cover -race ./...

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ 所有测试通过"
    echo "=========================================="
    exit 0
else
    echo ""
    echo "=========================================="
    echo "✗ 测试失败"
    echo "=========================================="
    exit 1
fi

