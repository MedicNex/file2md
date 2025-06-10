#!/bin/bash
cd /www/wwwroot/medicnex-file2md
source venv/bin/activate

# 检查必需的环境变量
if [ -z "$API_KEY" ]; then
    echo "❌ 错误: API_KEY 环境变量未设置"
    echo "请设置环境变量: export API_KEY='your-api-key'"
    exit 1
fi

export PORT=${PORT:-8999}
# ImageMagick环境变量
export MAGICK_HOME=/opt/homebrew/opt/imagemagick
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
