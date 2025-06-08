#!/bin/bash

# MedicNex File2Markdown 服务启动脚本

echo "🚀 启动 MedicNex File2Markdown 服务..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.11+"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 install -r requirements.txt

# 设置环境变量（如果没有设置的话）
export AGENT_API_KEYS=${AGENT_API_KEYS:-"dev-test-key-123"}
export PORT=${PORT:-8080}

echo "🔑 API Keys: $AGENT_API_KEYS"
echo "🌐 端口: $PORT"

# 启动服务
echo "🎯 启动服务..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload

echo "✅ 服务已启动！"
echo "📖 API 文档: http://localhost:$PORT/docs"
echo "🔍 健康检查: http://localhost:$PORT/v1/health" 