# MedicNex File2Markdown 宝塔面板部署文档

## 📋 部署环境要求

- **操作系统**: Linux Debian/Ubuntu
- **宝塔面板**: 7.7.0+ 
- **Python版本**: 3.9+
- **内存**: 建议 2GB+
- **磁盘**: 建议 10GB+ 可用空间

## 🔧 部署步骤

### 1. 环境准备

#### 1.1 安装宝塔面板
```bash
# Debian/Ubuntu系统
wget -O install.sh http://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

#### 1.2 安装Python环境
在宝塔面板中安装：
- **Python项目管理器** (必需)
- **Nginx** (用于反向代理)
- **PM2管理器** (用于进程管理)

### 2. 项目部署

#### 2.1 上传项目文件
1. 在宝塔面板 **文件管理** 中创建项目目录：`/www/wwwroot/medicnex-file2md`
2. 上传所有项目文件到该目录
3. 确保文件权限正确：
```bash
chown -R www:www /www/wwwroot/medicnex-file2md
chmod +x /www/wwwroot/medicnex-file2md/start.sh
```

#### 2.2 安装Python依赖
1. 进入 **Python项目管理器**
2. 点击 **添加项目**：
   - **项目名称**: `medicnex-file2md`
   - **项目路径**: `/www/wwwroot/medicnex-file2md`
   - **Python版本**: 选择3.9+
3. 创建项目后，点击 **模块** → **pip安装模块**：
```bash
pip install -r requirements.txt
```

#### 2.3 安装系统依赖
```bash
# 安装Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra

# 验证安装
tesseract --version
```

### 3. 配置环境变量

#### 3.1 创建环境配置文件
在项目根目录创建 `.env` 文件：
```env
# API密钥配置（必需）
AGENT_API_KEYS=your-api-key-1,your-api-key-2

# 视觉API配置（可选，用于图片识别）
VISION_API_KEY=your-vision-api-key
VISION_API_BASE=https://api.siliconflow.cn/v1
VISION_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

# 服务配置
PORT=8999
LOG_LEVEL=INFO
```

#### 3.2 安全配置建议
```bash
# 设置环境文件权限
chmod 600 /www/wwwroot/medicnex-file2md/.env

# 生成强密码作为API Key
openssl rand -hex 32
```

### 4. 启动服务

#### 4.1 使用PM2管理器启动
1. 进入 **PM2管理器**
2. 点击 **添加项目**：
   - **项目名称**: `medicnex-file2md`
   - **运行目录**: `/www/wwwroot/medicnex-file2md`
   - **启动文件**: `start.sh`
   - **运行模式**: `fork`
3. 点击 **提交** 启动服务

#### 4.2 手动启动（备选方案）
```bash
cd /www/wwwroot/medicnex-file2md
./start.sh
```

### 5. Nginx反向代理配置

#### 5.1 创建站点
1. 在宝塔面板 **网站** 中添加站点
2. 域名：`file.medicnex.com`
3. 根目录：随意设置（不使用）

#### 5.2 配置反向代理
在站点设置 → **反向代理** 中添加：
```nginx
# 代理名称：medicnex-api
# 目标URL：http://127.0.0.1:8999
# 发送域名：$host
# 内容替换：留空
```

#### 5.3 高级Nginx配置
在 **配置文件** 中添加：
```nginx
server {
    listen 80;
    server_name file.medicnex.com;
    
    # 文件上传大小限制
    client_max_body_size 100M;
    
    # API路由
    location /v1/ {
        proxy_pass http://127.0.0.1:8999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:8999/v1/health;
    }
    
    # 文档页面
    location /docs {
        proxy_pass http://127.0.0.1:8999/docs;
    }
}
```

### 6. SSL证书配置（推荐）

#### 6.1 申请免费SSL证书
1. 在宝塔面板 **SSL** 中申请Let's Encrypt证书
2. 开启 **强制HTTPS**

#### 6.2 HTTPS配置
```nginx
server {
    listen 443 ssl http2;
    server_name file.medicnex.com;
    
    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 其他配置与HTTP相同...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name file.medicnex.com;
    return 301 https://$server_name$request_uri;
}
```

### 7. 监控和维护

#### 7.1 日志查看
```bash
# 应用日志
tail -f /www/wwwroot/medicnex-file2md/logs/app.log

# PM2日志
pm2 logs medicnex-file2md

# Nginx日志
tail -f /www/server/nginx/logs/file.medicnex.com.log
```

#### 7.2 服务管理命令
```bash
# 重启服务
pm2 restart medicnex-file2md

# 停止服务
pm2 stop medicnex-file2md

# 查看服务状态
pm2 status

# 重载Nginx配置
nginx -s reload
```

#### 7.3 定期维护
1. **备份数据**：定期备份项目文件和配置
2. **更新依赖**：定期更新Python包
3. **监控资源**：关注CPU、内存使用情况
4. **日志清理**：定期清理过大的日志文件

### 8. 故障排除

#### 8.1 常见问题
| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 服务无法启动 | 端口被占用 | 检查端口占用：`netstat -nlp \| grep 8999` |
| 文件上传失败 | 权限问题 | 检查文件权限：`chown -R www:www /www/wwwroot/medicnex-file2md` |
| API Key错误 | 环境变量未设置 | 检查.env文件配置 |
| OCR功能异常 | Tesseract未安装 | 重新安装：`apt-get install tesseract-ocr` |

#### 8.2 性能优化
```bash
# 增加进程数（根据CPU核心数调整）
pm2 start start.sh -i 4 --name medicnex-file2md

# 优化Python进程
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
```

### 9. 安全建议

1. **API密钥管理**：
   - 使用强密码生成API Key
   - 定期轮换API密钥
   - 限制API访问频率

2. **网络安全**：
   - 配置防火墙规则
   - 启用SSL/TLS加密
   - 隐藏服务器信息

3. **文件安全**：
   - 限制上传文件大小和类型
   - 定期清理临时文件
   - 备份重要数据

### 10. 更新部署

```bash
# 1. 停止服务
pm2 stop medicnex-file2md

# 2. 备份当前版本
cp -r /www/wwwroot/medicnex-file2md /www/wwwroot/medicnex-file2md.backup

# 3. 更新代码
# 上传新版本文件

# 4. 更新依赖
pip install -r requirements.txt

# 5. 重启服务
pm2 start medicnex-file2md
```

## 📞 技术支持

如遇到部署问题，请提供以下信息：
- 操作系统版本
- 宝塔面板版本
- 错误日志内容
- 服务状态截图

---

**部署完成后，请访问 `https://file.medicnex.com/v1/health` 验证服务是否正常运行！** 