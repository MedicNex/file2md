#!/bin/bash

# 设置项目目录
PROJECT_DIR="/www/wwwroot/medicnex-file2md"
cd $PROJECT_DIR

# 激活虚拟环境
source $PROJECT_DIR/venv/bin/activate

# 加载环境变量
if [ -f $PROJECT_DIR/.env ]; then
    export $(cat $PROJECT_DIR/.env | grep -v '^#' | xargs)
fi

# 设置默认环境变量（如果没有.env文件）
export AGENT_API_KEYS=${AGENT_API_KEYS:-"dev-test-key-123"}
export PORT=${PORT:-8999}

echo "🚀 启动 MedicNex File2Markdown 服务..."
echo "🔑 API Keys: $AGENT_API_KEYS"
echo "🌐 端口: $PORT"

# 检查Python环境
echo "🐍 Python路径: $(which python3)"

# 检查依赖
echo "📦 检查uvicorn模块..."
python3 -c "import uvicorn; print('✅ uvicorn可用')" || {
    echo "❌ uvicorn未安装，正在安装依赖..."
    pip install -r requirements.txt
}

# 启动服务（注意：使用app.main:app而不是main.py）
echo "🎯 启动服务..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT

echo "✅ 服务已启动！"
echo "📖 API 文档: http://localhost:$PORT/docs"
echo "🔍 健康检查: http://localhost:$PORT/v1/health" 