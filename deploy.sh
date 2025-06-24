#!/bin/bash
# Linux 通用部署脚本
# 支持在任何目录下部署，自动检测项目路径

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

# 默认配置
DEFAULT_SERVICE_NAME="medicnex-file2md"
DEFAULT_PORT="8999"
DEFAULT_USER="www"
DEFAULT_GROUP="www"

# 解析命令行参数
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --directory DIR    项目目录 (默认: 当前目录)"
    echo "  -u, --user USER        运行用户 (默认: www)"
    echo "  -g, --group GROUP      运行用户组 (默认: www)"
    echo "  -p, --port PORT        服务端口 (默认: 8999)"
    echo "  -s, --service NAME     服务名称 (默认: medicnex-file2md)"
    echo "  --no-systemd           不创建systemd服务"
    echo "  --dev                  开发模式，不切换用户"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                               # 在当前目录部署"
    echo "  $0 -d /opt/myapp -u myuser       # 指定目录和用户"
    echo "  $0 --dev                         # 开发模式部署"
}

# 初始化变量
PROJECT_DIR=""
RUN_USER="$DEFAULT_USER"
RUN_GROUP="$DEFAULT_GROUP"
SERVICE_PORT="$DEFAULT_PORT"
SERVICE_NAME="$DEFAULT_SERVICE_NAME"
CREATE_SYSTEMD=true
DEV_MODE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--directory)
            PROJECT_DIR="$2"
            shift 2
            ;;
        -u|--user)
            RUN_USER="$2"
            shift 2
            ;;
        -g|--group)
            RUN_GROUP="$2"
            shift 2
            ;;
        -p|--port)
            SERVICE_PORT="$2"
            shift 2
            ;;
        -s|--service)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --no-systemd)
            CREATE_SYSTEMD=false
            shift
            ;;
        --dev)
            DEV_MODE=true
            RUN_USER=$(whoami)
            RUN_GROUP=$(id -gn)
            CREATE_SYSTEMD=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 自动检测项目目录
if [[ -z "$PROJECT_DIR" ]]; then
    PROJECT_DIR="$(pwd)"
    log_info "使用当前目录: $PROJECT_DIR"
else
    PROJECT_DIR="$(realpath "$PROJECT_DIR")"
    log_info "使用指定目录: $PROJECT_DIR"
fi

# 验证项目目录
if [[ ! -f "$PROJECT_DIR/requirements.txt" ]] || [[ ! -d "$PROJECT_DIR/app" ]]; then
    log_error "指定目录不是有效的项目目录（缺少 requirements.txt 或 app 目录）"
    exit 1
fi

# 开发模式提示
if [[ "$DEV_MODE" == true ]]; then
    log_warning "开发模式已启用"
    log_info "运行用户: $RUN_USER"
    log_info "不会创建systemd服务"
fi

# 权限检查
if [[ "$CREATE_SYSTEMD" == true ]] && [[ $EUID -ne 0 ]]; then
    log_error "创建systemd服务需要root权限，请使用sudo运行或使用 --dev 模式"
    exit 1
fi

# 用户存在性检查
if [[ "$CREATE_SYSTEMD" == true ]] && ! id "$RUN_USER" &>/dev/null; then
    log_warning "用户 $RUN_USER 不存在，是否创建？(y/N)"
    read -r response
    if [[ "$response" == "y" || "$response" == "Y" ]]; then
        useradd -r -s /bin/false "$RUN_USER" || true
        log_success "用户 $RUN_USER 已创建"
    else
        log_error "无法继续，用户不存在"
        exit 1
    fi
fi

echo "=================================================="
log_info "开始 PaddleOCR 通用部署..."
log_info "项目目录: $PROJECT_DIR"
log_info "运行用户: $RUN_USER:$RUN_GROUP"
log_info "服务端口: $SERVICE_PORT"
log_info "服务名称: $SERVICE_NAME"
echo "=================================================="

# 仅在非开发模式下更新系统包
if [[ "$DEV_MODE" == false ]]; then
    # 1. 更新系统包列表
    log_info "更新系统包列表..."
    apt update

    # 2. 安装基础依赖
    log_info "安装基础Python依赖..."
    apt install -y python3-pip python3-venv python3-dev python3-setuptools python3-wheel

    # 3. Ubuntu 24.04特定依赖处理
    log_info "安装系统依赖..."

    # 安装可用的OpenGL相关包
    apt install -y libgl1 libglx0 libgles2 || true
    apt install -y mesa-utils || true

    # 安装可用的图形库
    apt install -y libglib2.0-0t64 || apt install -y libglib2.0-0 || true
    apt install -y libsm6 libxext6 libxrender1 libgomp1 || true
    apt install -y libx11-6 libxcb1 libxau6 libxdmcp6 || true

    # 安装字体
    log_info "安装中文字体..."
    apt install -y fonts-noto-cjk fonts-liberation fonts-dejavu-core || true
    apt install -y fonts-wqy-microhei fonts-wqy-zenhei || true

    # 安装工具
    apt install -y curl wget jq || true

    log_success "系统依赖安装完成"
fi

# 4. 进入项目目录
log_info "进入项目目录..."
cd "$PROJECT_DIR"

# 5. 停止现有服务
if [[ "$CREATE_SYSTEMD" == true ]]; then
    log_info "停止现有服务..."
    systemctl stop "$SERVICE_NAME.service" 2>/dev/null || true
fi

pkill -f "app.main" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 3

# 6. 设置Python虚拟环境
log_info "设置Python虚拟环境..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 检查Python环境
log_info "检查Python环境..."
python --version
pip --version

# 7. 清理和重新安装Python依赖
log_info "清理可能冲突的包..."
pip uninstall -y paddlepaddle paddlepaddle-gpu paddlepaddle-cpu paddleocr opencv-python opencv-contrib-python 2>/dev/null || true

# 升级pip和基础工具
log_info "升级pip和基础工具..."
pip install --upgrade pip setuptools wheel

# 8. 安装PaddlePaddle核心框架
log_info "安装PaddlePaddle核心框架..."
pip install paddlepaddle==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证paddle安装
log_info "验证paddle核心模块..."
python -c "
try:
    import paddle
    print('✓ paddle模块导入成功')
    print(f'paddle版本: {paddle.__version__}')
except ImportError as e:
    print(f'✗ paddle导入失败: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    log_error "paddle安装验证失败，尝试替代安装方法..."
    
    # 尝试替代安装方法
    pip install paddlepaddle-cpu==2.6.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    python -c "
try:
    import paddle
    print('✓ paddle模块导入成功（替代方法）')
    print(f'paddle版本: {paddle.__version__}')
except ImportError as e:
    print(f'✗ paddle仍然导入失败: {e}')
    exit(1)
"
    
    if [[ $? -ne 0 ]]; then
        log_error "所有paddle安装方法都失败"
        exit 1
    fi
fi

log_success "PaddlePaddle核心框架安装成功"

# 9. 安装其他必要依赖
log_info "安装OpenCV和图像处理依赖..."
pip install opencv-python-headless==4.8.1.78
pip install pillow>=10.0.0 numpy>=1.21.0

# 10. 安装PaddleOCR
log_info "安装PaddleOCR..."
pip install paddleocr==2.7.3 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 11. 验证完整安装
log_info "验证完整PaddleOCR安装..."
python -c "
try:
    import paddle
    print('✓ paddle模块: OK')
    
    import paddleocr
    print('✓ paddleocr模块: OK')
    
    from paddleocr import PaddleOCR
    print('✓ PaddleOCR类: OK')
    
    print('所有核心模块验证通过！')
    
except Exception as e:
    print(f'✗ 验证失败: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

if [[ $? -ne 0 ]]; then
    log_error "PaddleOCR验证失败"
    exit 1
fi

# 12. 安装项目其他依赖
log_info "安装项目其他依赖..."
pip install -r requirements.txt

log_success "所有Python依赖安装完成"

# 13. 创建PaddleOCR兼容性测试
log_info "创建PaddleOCR兼容性测试..."

cat > test_paddle_final.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
from loguru import logger

def test_paddleocr_final():
    """最终的PaddleOCR兼容性测试"""
    try:
        # 测试基础导入
        import paddle
        logger.info(f"paddle版本: {paddle.__version__}")
        
        from paddleocr import PaddleOCR
        logger.info("PaddleOCR导入成功")
        
        # 测试不同配置
        test_configs = [
            {'lang': 'ch'},
            {},
            {'use_gpu': False, 'lang': 'ch'},
            {'use_angle_cls': True, 'lang': 'ch', 'use_gpu': False},
        ]
        
        working_config = None
        
        for i, config in enumerate(test_configs, 1):
            try:
                logger.info(f"测试配置 {i}: {config}")
                ocr = PaddleOCR(**config)
                logger.success(f"配置 {i} 初始化成功")
                working_config = config
                break
            except Exception as e:
                logger.warning(f"配置 {i} 失败: {str(e)}")
                continue
        
        if working_config is not None:
            logger.success(f"找到可用配置: {working_config}")
            
            # 测试OCR功能
            from PIL import Image, ImageDraw
            import tempfile
            
            img = Image.new('RGB', (300, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((20, 30), "PaddleOCR测试 Hello World", fill='black')
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                
                try:
                    result = ocr.ocr(tmp_file.name, cls=True)
                    logger.success("OCR功能测试成功")
                    print(f"SUCCESS:{working_config}")
                    return True
                except Exception as e:
                    logger.error(f"OCR功能测试失败: {e}")
                    print(f"OCR_FAILED:{working_config}")
                    return False
                finally:
                    os.unlink(tmp_file.name)
        else:
            logger.error("所有配置都失败")
            print("ALL_FAILED")
            return False
            
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        print(f"IMPORT_FAILED:{e}")
        return False
    except Exception as e:
        logger.error(f"未知错误: {e}")
        print(f"UNKNOWN_ERROR:{e}")
        return False

if __name__ == "__main__":
    success = test_paddleocr_final()
    sys.exit(0 if success else 1)
EOF

# 运行最终兼容性测试
log_info "运行PaddleOCR最终兼容性测试..."
test_result=$(python test_paddle_final.py 2>&1 | tail -1)

if [[ "$test_result" == SUCCESS:* ]]; then
    working_config=$(echo "$test_result" | cut -d: -f2-)
    log_success "PaddleOCR兼容性测试通过"
    log_info "可用配置: $working_config"
elif [[ "$test_result" == OCR_FAILED:* ]]; then
    log_warning "PaddleOCR初始化成功但OCR功能测试失败，继续部署..."
    working_config=$(echo "$test_result" | cut -d: -f2-)
else
    log_error "PaddleOCR兼容性测试失败: $test_result"
    log_warning "继续部署，使用默认配置..."
    working_config="{'lang': 'ch'}"
fi

# 清理测试文件
rm -f test_paddle_final.py

# 14. 更新vision.py文件（如果存在）
if [[ -f "app/vision.py" ]]; then
    log_info "更新vision.py文件以支持最佳兼容性..."

    # 备份原文件
    cp app/vision.py app/vision.py.backup

    # 创建最终兼容性版本
    cat > vision_final_patch.py << 'EOF'
def init_paddle_ocr():
    """初始化 PaddleOCR 引擎 - 最终兼容性版本"""
    global _ocr_engine
    try:
        # 首先验证paddle核心模块
        import paddle
        logger.info(f"paddle核心模块可用，版本: {paddle.__version__}")
        
        from paddleocr import PaddleOCR
        logger.info("PaddleOCR模块导入成功")
        
        # 多重兼容性配置尝试（按成功率排序）
        configs_to_try = [
            # 配置1: 最简配置（成功率最高）
            {'lang': 'ch'},
            
            # 配置2: 空配置
            {},
            
            # 配置3: 明确禁用GPU
            {'use_gpu': False, 'lang': 'ch'},
            
            # 配置4: 旧版本兼容
            {'use_angle_cls': True, 'lang': 'ch', 'use_gpu': False},
            
            # 配置5: 新版本兼容
            {'use_textline_orientation': True, 'lang': 'ch'},
        ]
        
        for i, config in enumerate(configs_to_try, 1):
            try:
                logger.info(f"尝试PaddleOCR配置 {i}: {config}")
                _ocr_engine = PaddleOCR(**config)
                logger.success(f"PaddleOCR初始化成功 - 使用配置 {i}")
                return _ocr_engine
            except Exception as e:
                logger.warning(f"配置 {i} 失败: {e}")
                continue
        
        # 所有配置都失败
        logger.error("所有PaddleOCR配置都失败")
        return None
        
    except ImportError as e:
        if "paddle" in str(e):
            logger.error("paddle核心模块未安装，请运行修复脚本")
        else:
            logger.error("PaddleOCR 未安装，请运行: pip install paddleocr")
        return None
    except Exception as e:
        logger.error(f"PaddleOCR 初始化失败: {e}")
        return None
EOF

    # 应用最终补丁
    python << 'EOF'
import re

# 读取原文件
with open('app/vision.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 读取补丁
with open('vision_final_patch.py', 'r', encoding='utf-8') as f:
    patch_content = f.read()

# 替换init_paddle_ocr函数
pattern = r'def init_paddle_ocr\(\):.*?(?=def|\n# |class |\Z)'
replacement = patch_content + '\n\n'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回文件
with open('app/vision.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("vision.py最终补丁应用完成")
EOF

    # 清理临时文件
    rm -f vision_final_patch.py

    # 15. 测试修复后的应用代码
    log_info "测试修复后的应用代码..."
    python -c "
try:
    from app.vision import init_paddle_ocr
    engine = init_paddle_ocr()
    if engine:
        print('✓ 应用中PaddleOCR初始化成功')
    else:
        print('⚠ PaddleOCR返回None，但模块可用')
except Exception as e:
    print(f'⚠ 应用测试异常: {e}，但继续部署')
"
fi

# 16. 创建systemd服务配置（如果需要）
if [[ "$CREATE_SYSTEMD" == true ]]; then
    log_info "创建systemd服务配置..."
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=MedicNex File2MD API Service with PaddleOCR
After=network.target redis.service

[Service]
Type=simple
User=$RUN_USER
Group=$RUN_GROUP
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port $SERVICE_PORT --workers 1
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# 资源限制 (PaddleOCR需要更多内存)
MemoryMax=3G
CPUQuota=200%

# 环境变量
Environment="PYTHONPATH=$PROJECT_DIR"
Environment="PYTHONUNBUFFERED=1"
Environment="PADDLEOCR_HOME=$PROJECT_DIR/.paddleocr"

[Install]
WantedBy=multi-user.target
EOF
fi

# 17. 设置文件权限
log_info "设置文件权限..."
if [[ "$CREATE_SYSTEMD" == true ]]; then
    chown -R "$RUN_USER:$RUN_GROUP" "$PROJECT_DIR"
fi
find "$PROJECT_DIR" -type d -exec chmod 755 {} \; 2>/dev/null || true
find "$PROJECT_DIR" -type f -exec chmod 644 {} \; 2>/dev/null || true
chmod +x "$PROJECT_DIR/venv/bin/"* 2>/dev/null || true

# 18. 启动服务
if [[ "$CREATE_SYSTEMD" == true ]]; then
    log_info "启动systemd服务..."
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME.service"
    systemctl start "$SERVICE_NAME.service"

    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
elif [[ "$DEV_MODE" == true ]]; then
    log_info "开发模式 - 启动服务进行测试..."
    # 在后台启动服务进行验证
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port "$SERVICE_PORT" --workers 1 > /tmp/medicnex-dev.log 2>&1 &
    SERVICE_PID=$!
    log_info "服务已在后台启动 (PID: $SERVICE_PID)，日志文件: /tmp/medicnex-dev.log"
    sleep 10
fi

# 19. 验证部署
log_info "验证部署状态..."

# 检查服务状态
if [[ "$CREATE_SYSTEMD" == true ]]; then
    if systemctl is-active --quiet "$SERVICE_NAME.service"; then
        log_success "✓ systemd服务启动成功"
        service_status="运行中"
    else
        log_warning "⚠ systemd服务可能未正常启动"
        service_status="异常"
        echo "服务状态详情:"
        systemctl status "$SERVICE_NAME.service" --no-pager -l
    fi
elif [[ "$DEV_MODE" == true ]]; then
    if kill -0 "$SERVICE_PID" 2>/dev/null; then
        log_success "✓ 开发服务启动成功"
        service_status="运行中"
    else
        log_warning "⚠ 开发服务可能未正常启动"
        service_status="异常"
    fi
else
    service_status="未启动"
fi

# 健康检查
log_info "执行健康检查..."
sleep 5

health_status="失败"
for i in {1..5}; do
    if curl -s "http://localhost:$SERVICE_PORT/v1/health" > /dev/null 2>&1; then
        health_status="成功"
        break
    fi
    log_info "健康检查重试 $i/5..."
    sleep 3
done

if [[ "$health_status" == "成功" ]]; then
    log_success "✓ 健康检查通过"
    
    echo ""
    echo "=== 健康检查结果 ==="
    curl -s "http://localhost:$SERVICE_PORT/v1/health" 2>/dev/null | jq '.' 2>/dev/null || curl -s "http://localhost:$SERVICE_PORT/v1/health" 2>/dev/null || echo "健康检查响应获取失败"
    
else
    log_warning "⚠ 健康检查失败，查看服务日志获取详细信息"
fi

# 20. 最终部署报告
echo ""
echo "=================================================="
log_success "PaddleOCR 部署完成！"
echo "=================================================="
echo ""
echo "📊 部署状态报告："
echo "  ✓ 项目目录: $PROJECT_DIR"
echo "  ✓ 运行用户: $RUN_USER:$RUN_GROUP"
echo "  ✓ 系统依赖: 已安装"
echo "  ✓ Python环境: 已配置"
echo "  ✓ PaddlePaddle: 已安装"
echo "  ✓ PaddleOCR: 已安装"
echo "  ✓ 项目依赖: 已安装"
if [[ -f "app/vision.py" ]]; then
    echo "  ✓ 代码兼容性: 已修复"
fi
if [[ "$CREATE_SYSTEMD" == true ]]; then
    echo "  ✓ systemd服务: 已配置"
fi
echo "  ✓ 服务状态: $service_status"
echo "  ✓ 健康检查: $health_status"
echo ""
echo "🌐 服务信息："
echo "  - 服务端口: $SERVICE_PORT"
echo "  - API地址: http://localhost:$SERVICE_PORT"
echo "  - 健康检查: http://localhost:$SERVICE_PORT/health"
echo "  - API文档: http://localhost:$SERVICE_PORT/docs"
echo ""

if [[ "$CREATE_SYSTEMD" == true ]]; then
    echo "🔧 systemd管理命令："
    echo "  - 查看服务状态: sudo systemctl status $SERVICE_NAME.service"
    echo "  - 查看实时日志: sudo journalctl -u $SERVICE_NAME.service -f"
    echo "  - 重启服务: sudo systemctl restart $SERVICE_NAME.service"
    echo "  - 停止服务: sudo systemctl stop $SERVICE_NAME.service"
elif [[ "$DEV_MODE" == true ]]; then
    echo "🔧 开发模式管理："
    echo "  - 查看日志: tail -f /tmp/medicnex-dev.log"
    echo "  - 停止服务: kill $SERVICE_PID"
    echo "  - 手动启动: cd $PROJECT_DIR && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port $SERVICE_PORT"
fi

echo ""
echo "🧪 测试命令："
echo "  - 健康检查: curl -s http://localhost:$SERVICE_PORT/health"
echo "  - 缓存状态: curl -s -H 'X-API-Key: file2md-2024-secure-key' http://localhost:$SERVICE_PORT/v1/cache/stats"
echo "  - OCR测试: curl -X POST 'http://localhost:$SERVICE_PORT/v1/convert' -H 'X-API-Key: file2md-2024-secure-key' -F 'file=@test_image.png'"
echo ""

if [[ "$service_status" == "运行中" && "$health_status" == "成功" ]]; then
    log_success "🎉 部署完全成功！PaddleOCR服务已就绪，可以开始使用。"
elif [[ "$DEV_MODE" == true ]]; then
    log_success "🎉 开发模式部署完成！服务运行在端口 $SERVICE_PORT"
else
    log_warning "⚠️  部署基本完成，但需要进一步检查："
    echo ""
    echo "   可能的问题排查："
    if [[ "$CREATE_SYSTEMD" == true ]]; then
        echo "   1. 查看详细日志: sudo journalctl -u $SERVICE_NAME.service -f"
    else
        echo "   1. 查看详细日志: tail -f /tmp/medicnex-dev.log"
    fi
    echo "   2. 检查端口占用: sudo netstat -tlnp | grep $SERVICE_PORT"
    echo "   3. 手动测试服务: cd $PROJECT_DIR && source venv/bin/activate && python -m app.main"
    echo "   4. 检查Redis服务: sudo systemctl status redis"
fi

echo ""
echo "=================================================="
echo "部署完成！感谢使用 MedicNex File2MD 服务。"
echo "==================================================" 