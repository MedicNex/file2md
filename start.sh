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
export API_KEY=${API_KEY:-"dev-test-key-123"}
export PORT=${PORT:-8999}
export MAX_CONCURRENT=${MAX_CONCURRENT:-"10"}
# ImageMagick环境变量
export MAGICK_HOME=/opt/homebrew/opt/imagemagick

echo "🚀 启动 MedicNex File2Markdown 服务..."
echo "🔑 API Keys: $API_KEY"
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

cat > /www/wwwroot/medicnex-file2md/multiport.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'medicnex-file2md-0',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 8999',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '8999',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-0-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-0-out.log'
    },
    {
      name: 'medicnex-file2md-1',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9002',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9002',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-1-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-1-out.log'
    },
    {
      name: 'medicnex-file2md-2',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9003',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9003',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-2-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-2-out.log'
    },
    {
      name: 'medicnex-file2md-3',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9004',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9004',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-3-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-3-out.log'
    },
    {
      name: 'medicnex-file2md-4',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9005',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9005',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-4-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-4-out.log'
    },
    {
      name: 'medicnex-file2md-5',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9006',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9006',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-5-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-5-out.log'
    },
    {
      name: 'medicnex-file2md-6',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9007',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9007',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-6-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-6-out.log'
    },
    {
      name: 'medicnex-file2md-7',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9008',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9008',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-7-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-7-out.log'
    },
    {
      name: 'medicnex-file2md-8',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9009',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9009',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-8-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-8-out.log'
    },
    {
      name: 'medicnex-file2md-9',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9010',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9010',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-9-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-9-out.log'
    },
    {
      name: 'medicnex-file2md-10',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9011',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9011',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-10-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-10-out.log'
    },
    {
      name: 'medicnex-file2md-11',
      script: '/www/wwwroot/medicnex-file2md/venv/bin/python3',
      args: '-m uvicorn app.main:app --host 0.0.0.0 --port 9012',
      cwd: '/www/wwwroot/medicnex-file2md',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_memory_restart: '4096M',
      env: { 
        NODE_ENV: 'production', 
        PYTHONPATH: '/www/wwwroot/medicnex-file2md', 
        API_KEY: 'sk-J4WdRKQNTaapOJ5p0VcjCxYa4BRvZhiHNZFu1255nT',
        PORT: '9012',
        MAGICK_HOME: '/opt/homebrew/opt/imagemagick',
        MAX_CONCURRENT: '10'
      },
      error_file: '/www/wwwlogs/pm2/medicnex-11-error.log',
      out_file: '/www/wwwlogs/pm2/medicnex-11-out.log'
    }
  ]
};
EOF 