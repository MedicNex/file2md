#!/bin/bash

# File2MD Docker入口点脚本
# 启动Redis和应用服务，支持.env文件热重载

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查.env文件
if [[ ! -f "/app/.env" ]]; then
    log_warning "未找到.env文件，将使用默认配置"
    # 创建默认.env文件
    cat > /app/.env << EOF
# 应用基础配置
PORT=8999
DEBUG=false
LOG_LEVEL=INFO
ENABLE_DETAILED_LOGGING=false
MAX_LOG_CONTENT_LENGTH=500

# 队列配置
MAX_CONCURRENT=5
QUEUE_CLEANUP_HOURS=24

# 文件处理配置
MAX_FILE_SIZE=100
MAX_IMAGES_PER_DOC=5
TEMP_DIR=/tmp
MAX_TEXT_LINES=50000
MAX_TEXT_CHARS=10000000
TEXT_CHUNK_SIZE=1048576

# Redis缓存配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_CACHE_ENABLED=true
REDIS_CACHE_TTL=86400
REDIS_CONNECTION_TIMEOUT=5.0
REDIS_MAX_CONNECTIONS=20

# API安全配置
REQUIRE_API_KEY=false

# 视觉API配置
VISION_API_BASE=https://api.openai.com/v1
VISION_MODEL=gpt-4o-mini
VISION_MAX_RETRIES=3
VISION_RETRY_DELAY=1.0
VISION_BACKOFF_FACTOR=2.0

# CORS配置
ENABLE_CORS=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080
CORS_ALLOW_CREDENTIALS=true
EOF
    log_success "已创建默认.env文件"
fi

# 创建必要目录
mkdir -p /app/logs /app/temp /app/.paddleocr /var/lib/redis
chown -R appuser:appuser /app || true

# 启动Redis服务器
start_redis() {
    log_info "启动Redis服务器..."
    su - appuser -c "redis-server /etc/redis/redis.conf --daemonize yes"
    sleep 2
    
    # 检查Redis是否启动成功
    if redis-cli ping > /dev/null 2>&1; then
        log_success "Redis服务器启动成功"
    else
        log_error "Redis服务器启动失败"
        exit 1
    fi
}

# 启动应用服务
start_app() {
    log_info "启动应用服务..."
    cd /app
    # 使用虚拟环境中的Python
    su - appuser -c "/opt/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8999 --reload"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    redis-cli shutdown > /dev/null 2>&1 || true
    pkill -f uvicorn || true
}

# 信号处理
trap stop_services SIGTERM SIGINT

# 主函数
main() {
    case "$1" in
        "start")
            log_info "启动File2MD服务..."
            start_redis
            start_app
            ;;
        "redis")
            log_info "仅启动Redis服务器..."
            start_redis
            # 保持容器运行
            tail -f /dev/null
            ;;
        "app")
            log_info "仅启动应用服务..."
            start_app
            ;;
        "shell")
            log_info "启动交互式shell..."
            exec /bin/bash
            ;;
        *)
            echo "用法: $0 {start|redis|app|shell}"
            echo "  start  - 启动Redis和应用服务"
            echo "  redis  - 仅启动Redis服务器"
            echo "  app    - 仅启动应用服务"
            echo "  shell  - 启动交互式shell"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 