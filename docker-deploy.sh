#!/bin/bash

# MedicNex File2MD Docker部署脚本
# 支持.env文件热重载
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

# 检查.env文件
if [[ ! -f ".env" ]]; then
    log_warning "未找到.env文件，将使用默认配置"
    if [[ -f ".env.example" ]]; then
        log_info "复制.env.example为.env..."
        cp .env.example .env
        log_success "已创建.env文件，请根据需要修改配置"
    else
        log_warning "未找到.env.example文件，将使用docker-compose.yml中的默认配置"
    fi
else
    log_info "找到.env文件，将使用自定义配置"
fi

log_info "开始Docker部署..."

# 停止现有容器
log_info "停止现有容器..."
docker-compose down 2>/dev/null || true

# 清理选项
if [[ "$1" == "--clean" ]]; then
    log_info "清理旧镜像和卷..."
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f
fi

# 创建必要目录
log_info "创建必要目录..."
mkdir -p logs temp .paddleocr

# 设置目录权限
chmod 755 logs temp .paddleocr

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
for i in {1..15}; do
    if curl -s http://localhost:8999/v1/health > /dev/null 2>&1; then
        log_success "✓ 健康检查通过"
        break
    else
        if [[ $i -eq 15 ]]; then
            log_error "✗ 健康检查失败，服务可能未正常启动"
            log_info "查看容器日志: docker-compose logs medicnex-file2md"
            exit 1
        fi
        log_info "健康检查重试 $i/15..."
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
echo "  - Web界面: http://localhost:8999/webui"
echo ""
echo "🔧 管理命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 查看应用日志: docker-compose logs -f medicnex-file2md"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 更新服务: docker-compose pull && docker-compose up -d"
echo "  - 重新构建: docker-compose up --build -d"
echo ""
echo "📝 配置管理："
echo "  - 修改配置: 编辑.env文件后重启服务"
echo "  - 热重载: 修改.env文件后服务会自动重新加载"
echo "  - 查看配置: cat .env"
echo ""
echo "📊 容器状态："
docker-compose ps 