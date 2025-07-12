#!/bin/bash

# MedicNex File2MD Docker镜像构建脚本

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

# 默认参数
IMAGE_NAME="medicnex-file2md"
TAG="latest"
PLATFORM=""
CLEAN=false
PUSH=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        --push)
            PUSH=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  -t, --tag TAG       指定镜像标签 (默认: latest)"
            echo "  -p, --platform PLAT 指定平台 (linux/amd64, linux/arm64)"
            echo "  -c, --clean         清理旧镜像"
            echo "  --push              推送到镜像仓库"
            echo "  -h, --help          显示帮助信息"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker未安装，请先安装Docker"
    exit 1
fi

# 检查必要文件
if [[ ! -f "Dockerfile" ]]; then
    log_error "未找到Dockerfile"
    exit 1
fi

if [[ ! -f "docker-entrypoint.sh" ]]; then
    log_error "未找到docker-entrypoint.sh"
    exit 1
fi

# 清理旧镜像
if [[ "$CLEAN" == "true" ]]; then
    log_info "清理旧镜像..."
    docker rmi ${IMAGE_NAME}:${TAG} 2>/dev/null || true
    docker system prune -f
fi

# 构建参数
BUILD_ARGS=""
if [[ -n "$PLATFORM" ]]; then
    BUILD_ARGS="--platform $PLATFORM"
    log_info "构建平台: $PLATFORM"
fi

# 显示构建信息
log_info "开始构建Docker镜像..."
echo "镜像名称: ${IMAGE_NAME}:${TAG}"
echo "构建参数: $BUILD_ARGS"

# 构建镜像
log_info "执行docker build..."
if docker build $BUILD_ARGS -t ${IMAGE_NAME}:${TAG} .; then
    log_success "镜像构建成功！"
else
    log_error "镜像构建失败"
    exit 1
fi

# 显示镜像信息
log_info "镜像信息:"
docker images ${IMAGE_NAME}:${TAG}

# 显示镜像大小
IMAGE_SIZE=$(docker images ${IMAGE_NAME}:${TAG} --format "table {{.Size}}" | tail -n 1)
log_info "镜像大小: $IMAGE_SIZE"

# 测试镜像
log_info "测试镜像..."
if docker run --rm ${IMAGE_NAME}:${TAG} /usr/local/bin/docker-entrypoint.sh --help > /dev/null 2>&1; then
    log_success "镜像测试通过"
else
    log_warning "镜像测试失败，但构建成功"
fi

# 推送到镜像仓库
if [[ "$PUSH" == "true" ]]; then
    log_info "推送到镜像仓库..."
    if docker push ${IMAGE_NAME}:${TAG}; then
        log_success "镜像推送成功"
    else
        log_error "镜像推送失败"
        exit 1
    fi
fi

# 显示使用说明
echo ""
echo "=================================================="
log_success "Docker镜像构建完成！"
echo "=================================================="
echo ""
echo "🚀 快速启动:"
echo "  docker run -d --name medicnex-file2md -p 8999:8999 ${IMAGE_NAME}:${TAG}"
echo ""
echo "📝 使用自定义配置:"
echo "  docker run -d --name medicnex-file2md -p 8999:8999 \\"
echo "    -v \$(pwd)/.env:/app/.env:ro \\"
echo "    -v \$(pwd)/logs:/app/logs \\"
echo "    ${IMAGE_NAME}:${TAG}"
echo ""
echo "🔧 管理命令:"
echo "  - 查看日志: docker logs medicnex-file2md"
echo "  - 停止服务: docker stop medicnex-file2md"
echo "  - 重启服务: docker restart medicnex-file2md"
echo "  - 删除容器: docker rm medicnex-file2md"
echo ""
echo "🌐 访问地址:"
echo "  - API文档: http://localhost:8999/docs"
echo "  - Web界面: http://localhost:8999/webui"
echo "  - 健康检查: http://localhost:8999/v1/health" 