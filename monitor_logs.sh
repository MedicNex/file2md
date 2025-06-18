#!/bin/bash
# File2MD 服务器日志监控脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印分割线
print_section() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

# 显示帮助信息
show_help() {
    echo -e "${YELLOW}File2MD 日志监控工具${NC}"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -a, --app          查看应用服务日志"
    echo "  -r, --redis        查看Redis服务日志"
    echo "  -f, --follow       实时跟踪日志"
    echo "  -e, --errors       只显示错误日志"
    echo "  -s, --status       查看服务状态"
    echo "  -c, --cache        查看缓存相关日志"
    echo "  -n, --lines NUM    显示最后N行日志 (默认50)"
    echo "  -t, --tail         实时查看所有相关日志"
    echo "  -h, --help         显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 -a              # 查看应用日志"
    echo "  $0 -a -f           # 实时监控应用日志"
    echo "  $0 -c -n 100       # 查看最后100行缓存相关日志"
    echo "  $0 -t              # 实时监控所有日志"
}

# 检查服务状态
check_service_status() {
    print_section "服务状态检查"
    
    echo "🔸 File2MD 应用服务状态:"
    if systemctl is-active --quiet medicnex-file2md; then
        echo -e "${GREEN}✅ medicnex-file2md: RUNNING${NC}"
        systemctl status medicnex-file2md --no-pager -l
    else
        echo -e "${RED}❌ medicnex-file2md: STOPPED${NC}"
        systemctl status medicnex-file2md --no-pager -l
    fi
    
    echo
    echo "🔸 Redis 服务状态:"
    if systemctl is-active --quiet redis-medicnex; then
        echo -e "${GREEN}✅ redis-medicnex: RUNNING${NC}"
        systemctl status redis-medicnex --no-pager -l
    else
        echo -e "${YELLOW}⚠️ redis-medicnex: 检查手动启动的Redis${NC}"
        # 检查手动启动的Redis进程
        redis_processes=$(ps aux | grep "redis-server.*6381" | grep -v grep)
        if [ -n "$redis_processes" ]; then
            echo -e "${GREEN}✅ Redis (手动启动): RUNNING${NC}"
            echo "$redis_processes"
        else
            echo -e "${RED}❌ Redis: NOT FOUND${NC}"
        fi
    fi
}

# 查看应用日志
view_app_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_section "File2MD 应用日志"
    
    if [ "$follow" = "true" ]; then
        echo "🔸 实时监控应用日志 (按 Ctrl+C 退出)..."
        sudo journalctl -u medicnex-file2md -f --no-pager
    else
        echo "🔸 显示最后 $lines 行应用日志:"
        sudo journalctl -u medicnex-file2md -n $lines --no-pager
    fi
}

# 查看Redis日志
view_redis_logs() {
    local lines=${1:-50}
    local follow=${2:-false}
    
    print_section "Redis 服务日志"
    
    if [ "$follow" = "true" ]; then
        echo "🔸 实时监控Redis日志 (按 Ctrl+C 退出)..."
        # 尝试systemd日志
        if systemctl is-active --quiet redis-medicnex; then
            sudo journalctl -u redis-medicnex -f --no-pager
        else
            echo "Redis systemd服务未运行，尝试查找Redis日志文件..."
            # 查找常见的Redis日志位置
            redis_log_files=(
                "/var/log/redis/redis-server.log"
                "/var/log/redis.log"
                "/usr/local/var/log/redis.log"
                "/tmp/redis.log"
            )
            
            for log_file in "${redis_log_files[@]}"; do
                if [ -f "$log_file" ]; then
                    echo "找到Redis日志文件: $log_file"
                    tail -f "$log_file"
                    return
                fi
            done
            
            echo "未找到Redis日志文件，请检查Redis配置"
        fi
    else
        echo "🔸 显示最后 $lines 行Redis日志:"
        if systemctl is-active --quiet redis-medicnex; then
            sudo journalctl -u redis-medicnex -n $lines --no-pager
        else
            echo "Redis systemd服务未运行，显示进程信息:"
            ps aux | grep redis | grep -v grep
        fi
    fi
}

# 查看错误日志
view_error_logs() {
    local lines=${1:-50}
    
    print_section "错误日志"
    
    echo "🔸 应用错误日志:"
    sudo journalctl -u medicnex-file2md -p err -n $lines --no-pager
    
    echo
    echo "🔸 Redis错误日志:"
    if systemctl is-active --quiet redis-medicnex; then
        sudo journalctl -u redis-medicnex -p err -n $lines --no-pager
    else
        echo "Redis systemd服务未运行"
    fi
    
    echo
    echo "🔸 系统错误日志 (与Redis/Python相关):"
    sudo journalctl -p err --since "1 hour ago" | grep -i -E "(redis|python|medicnex)" | tail -n $lines
}

# 查看缓存相关日志
view_cache_logs() {
    local lines=${1:-50}
    
    print_section "缓存相关日志"
    
    echo "🔸 缓存操作日志:"
    sudo journalctl -u medicnex-file2md -n $lines --no-pager | grep -i -E "(cache|redis)"
    
    echo
    echo "🔸 Redis连接日志:"
    sudo journalctl -u medicnex-file2md --since "1 hour ago" --no-pager | grep -i -E "(redis|connection)"
}

# 实时监控所有日志
tail_all_logs() {
    print_section "实时监控所有相关日志"
    
    echo "🔸 启动多窗口日志监控 (按 Ctrl+C 退出)..."
    echo "正在监控: File2MD应用 + Redis服务"
    
    # 使用multitail或者简单的方法
    if command -v multitail &> /dev/null; then
        multitail \
            -l "sudo journalctl -u medicnex-file2md -f --no-pager" \
            -l "sudo journalctl -u redis-medicnex -f --no-pager"
    else
        echo "提示: 安装 multitail 可以同时查看多个日志"
        echo "使用简单模式监控应用日志..."
        sudo journalctl -u medicnex-file2md -f --no-pager
    fi
}

# 主函数
main() {
    local lines=50
    local follow=false
    local show_app=false
    local show_redis=false
    local show_errors=false
    local show_status=false
    local show_cache=false
    local tail_all=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--app)
                show_app=true
                shift
                ;;
            -r|--redis)
                show_redis=true
                shift
                ;;
            -f|--follow)
                follow=true
                shift
                ;;
            -e|--errors)
                show_errors=true
                shift
                ;;
            -s|--status)
                show_status=true
                shift
                ;;
            -c|--cache)
                show_cache=true
                shift
                ;;
            -n|--lines)
                lines="$2"
                shift 2
                ;;
            -t|--tail)
                tail_all=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定选项，显示帮助
    if [ "$show_app" = false ] && [ "$show_redis" = false ] && [ "$show_errors" = false ] && [ "$show_status" = false ] && [ "$show_cache" = false ] && [ "$tail_all" = false ]; then
        show_help
        exit 0
    fi
    
    # 执行相应的操作
    if [ "$show_status" = true ]; then
        check_service_status
    fi
    
    if [ "$show_app" = true ]; then
        view_app_logs $lines $follow
    fi
    
    if [ "$show_redis" = true ]; then
        view_redis_logs $lines $follow
    fi
    
    if [ "$show_errors" = true ]; then
        view_error_logs $lines
    fi
    
    if [ "$show_cache" = true ]; then
        view_cache_logs $lines
    fi
    
    if [ "$tail_all" = true ]; then
        tail_all_logs
    fi
}

# 运行主函数
main "$@" 