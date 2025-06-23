#!/bin/bash
# MedicNex File2MD Docker部署脚本

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

# 检查Docker和Docker Compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 环境检查通过"
}

# 创建环境配置文件
create_env_file() {
    if [[ ! -f ".env" ]]; then
        log_info "创建环境配置文件..."
        
        # 生成随机API密钥
        API_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
        REDIS_PASSWORD=$(openssl rand -hex 16 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)
        
        cat > .env << EOF
# MedicNex File2MD Docker环境配置
# 自动生成于 $(date)

# API密钥（请妥善保存）
API_KEY=$API_KEY
REQUIRE_API_KEY=true

# Redis密码
REDIS_PASSWORD=$REDIS_PASSWORD

# CORS配置（请根据需要修改）
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8999

# 可选配置
VISION_API_KEY=
OPENAI_API_KEY=
VISION_API_BASE=https://api.openai.com/v1
VISION_MODEL=gpt-4o-mini

# 性能配置
MAX_CONCURRENT=5
MAX_FILE_SIZE=100
LOG_LEVEL=INFO
EOF
        
        log_success "环境配置文件已创建：.env"
        log_warning "请记录您的API密钥：$API_KEY"
        
    else
        log_info "环境配置文件已存在，跳过创建"
    fi
}

# 构建并启动服务
deploy_services() {
    log_info "开始构建和部署服务..."
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建Docker镜像（这可能需要几分钟）..."
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi
    
    # 启动服务
    log_info "启动服务..."
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待Redis启动
    for i in {1..30}; do
        if docker exec medicnex-redis redis-cli ping &>/dev/null; then
            log_success "Redis 服务已就绪"
            break
        fi
        if [[ $i -eq 30 ]]; then
            log_error "Redis 服务启动超时"
            return 1
        fi
        sleep 2
    done
    
    # 等待API服务启动
    for i in {1..60}; do
        if curl -s http://localhost:8999/v1/health &>/dev/null; then
            log_success "API 服务已就绪"
            break
        fi
        if [[ $i -eq 60 ]]; then
            log_error "API 服务启动超时"
            return 1
        fi
        sleep 3
    done
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查API健康状态
    health_response=$(curl -s http://localhost:8999/v1/health)
    if [[ $? -eq 0 ]]; then
        echo "$health_response" | jq '.' 2>/dev/null || echo "$health_response"
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        return 1
    fi
}

# 显示部署信息
show_deployment_info() {
    API_KEY=$(grep "^API_KEY=" .env | cut -d'=' -f2)
    
    echo ""
    echo "=================================================="
    log_success "🎉 MedicNex File2MD Docker部署完成！"
    echo "=================================================="
    echo ""
    echo "📊 服务信息："
    echo "  🌐 API地址: http://localhost:8999"
    echo "  📖 API文档: http://localhost:8999/docs"
    echo "  ❤️  健康检查: http://localhost:8999/v1/health"
    echo "  🔑 API密钥: $API_KEY"
    echo ""
    echo "🔧 管理命令："
    echo "  查看服务状态: docker-compose ps"
    echo "  查看日志: docker-compose logs -f"
    echo "  重启服务: docker-compose restart"
    echo "  停止服务: docker-compose down"
    echo "  更新服务: docker-compose pull && docker-compose up -d"
    echo ""
    echo "🧪 测试命令："
    echo "  健康检查: curl -s http://localhost:8999/v1/health"
    echo "  缓存状态: curl -s -H 'X-API-Key: $API_KEY' http://localhost:8999/v1/cache/stats"
    echo ""
    echo "💡 提示："
    echo "  - 请妥善保存API密钥"
    echo "  - 首次运行会下载PaddleOCR模型，请耐心等待"
    echo "  - 如需修改配置，请编辑 .env 文件后重启服务"
    echo ""
}

# 主函数
main() {
    echo "=================================================="
    log_info "开始 MedicNex File2MD Docker 部署"
    echo "=================================================="
    
    # 检查前置条件
    check_docker
    
    # 创建配置文件
    create_env_file
    
    # 部署服务
    deploy_services
    
    # 等待服务就绪
    wait_for_services
    
    # 健康检查
    health_check
    
    # 显示部署信息
    show_deployment_info
}

# 命令行参数处理
case "${1:-}" in
    "stop")
        log_info "停止所有服务..."
        docker-compose down 2>/dev/null || docker compose down 2>/dev/null
        log_success "服务已停止"
        ;;
    "restart")
        log_info "重启服务..."
        docker-compose restart 2>/dev/null || docker compose restart 2>/dev/null
        log_success "服务已重启"
        ;;
    "logs")
        docker-compose logs -f 2>/dev/null || docker compose logs -f 2>/dev/null
        ;;
    "status")
        docker-compose ps 2>/dev/null || docker compose ps 2>/dev/null
        ;;
    "clean")
        log_warning "这将删除所有容器和数据卷，确定要继续吗？(y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            docker-compose down -v --rmi all 2>/dev/null || docker compose down -v --rmi all 2>/dev/null
            log_success "清理完成"
        else
            log_info "取消清理操作"
        fi
        ;;
    "")
        main
        ;;
    *)
        echo "用法: $0 [命令]"
        echo ""
        echo "可用命令："
        echo "  (无参数)  - 执行完整部署"
        echo "  stop      - 停止服务"
        echo "  restart   - 重启服务"
        echo "  logs      - 查看日志"
        echo "  status    - 查看服务状态"
        echo "  clean     - 清理所有数据（危险操作）"
        exit 1
        ;;
esac 