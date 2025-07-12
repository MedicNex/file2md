#!/bin/bash

# Docker部署脚本
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

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

log_info "开始Docker部署..."

# 停止现有容器
log_info "停止现有容器..."
docker-compose down 2>/dev/null || true

# 清理旧镜像（可选）
if [[ "$1" == "--clean" ]]; then
    log_info "清理旧镜像..."
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
fi

# 创建必要目录
log_info "创建必要目录..."
mkdir -p logs temp .paddleocr

# 构建并启动服务
log_info "构建并启动服务..."
docker-compose up --build -d

# 等待服务启动
log_info "等待服务启动..."
sleep 30

# 检查服务状态
log_info "检查服务状态..."
docker-compose ps

# 健康检查
log_info "执行健康检查..."
for i in {1..10}; do
    if curl -s http://localhost:8999/v1/health > /dev/null 2>&1; then
        log_success "✓ 健康检查通过"
        break
    else
        log_info "健康检查重试 $i/10..."
        sleep 10
    fi
done

# 显示服务信息
echo ""
echo "=================================================="
log_success "Docker部署完成！"
echo "=================================================="
echo ""
echo "🌐 服务信息："
echo "  - API地址: http://localhost:8999"
echo "  - 健康检查: http://localhost:8999/v1/health"
echo "  - API文档: http://localhost:8999/docs"
echo ""
echo "🔧 管理命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 更新服务: docker-compose pull && docker-compose up -d"
echo ""
echo "📊 容器状态："
docker-compose ps 