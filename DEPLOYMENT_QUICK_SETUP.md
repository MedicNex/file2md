# MedicNex File2Markdown 快速部署指南

> 🎯 专门针对 **file.medicnex.com** 域名的快速部署配置
> 
> ✨ **v1.1 新功能**：支持 83+ 种代码文件转换，统一代码块输出格式

## 🚀 一键部署脚本

### 1. 环境变量配置

在项目根目录创建 `.env` 文件：

```env
# API密钥配置
AGENT_API_KEYS=medicnex-2024-prod-key-f2md,medicnex-backup-key-f2md

# 视觉API配置
VISION_API_KEY=sk-sfncynyftubpujczaokfwiopimnmtxwxgnzmbwanwuavdhoc
VISION_API_BASE=https://api.siliconflow.cn/v1
VISION_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

# 服务配置
PORT=8999
LOG_LEVEL=INFO
HOST=0.0.0.0
```

### 2. Nginx配置文件

创建 `/www/server/nginx/conf/vhost/file.medicnex.com.conf`：

```nginx
# HTTP配置 - 重定向到HTTPS
server {
    listen 80;
    server_name file.medicnex.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name file.medicnex.com;
    
    # SSL证书配置
    ssl_certificate /www/server/panel/vhost/cert/file.medicnex.com/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/file.medicnex.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 文件上传大小限制
    client_max_body_size 100M;
    client_body_timeout 60s;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # API路由
    location /v1/ {
        proxy_pass http://127.0.0.1:8999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # 缓冲设置
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # 健康检查 - 无需认证
    location /health {
        proxy_pass http://127.0.0.1:8999/v1/health;
        access_log off;
    }
    
    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8999/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # ReDoc文档
    location /redoc {
        proxy_pass http://127.0.0.1:8999/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 根路径
    location / {
        proxy_pass http://127.0.0.1:8999;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 访问日志
    access_log /www/wwwlogs/file.medicnex.com.log;
    error_log /www/wwwlogs/file.medicnex.com.error.log;
}
```

### 3. PM2进程配置

创建 `ecosystem.config.js`：

```javascript
module.exports = {
  apps: [{
    name: 'medicnex-file2md',
    script: 'python3',
    args: ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8999'],
    cwd: '/www/wwwroot/medicnex-file2md',
    instances: 2,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PYTHONPATH: '/www/wwwroot/medicnex-file2md',
      PYTHONUNBUFFERED: '1'
    },
    error_file: '/www/wwwlogs/medicnex-file2md-error.log',
    out_file: '/www/wwwlogs/medicnex-file2md-out.log',
    log_file: '/www/wwwlogs/medicnex-file2md.log',
    time: true,
    autorestart: true,
    restart_delay: 1000
  }]
}
```

### 4. 一键部署脚本

创建 `deploy.sh`：

```bash
#!/bin/bash

# MedicNex File2Markdown 一键部署脚本
# 域名: file.medicnex.com

set -e

echo "🚀 开始部署 MedicNex File2Markdown 服务..."

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 权限运行此脚本"
    exit 1
fi

# 项目配置
PROJECT_NAME="medicnex-file2md"
PROJECT_PATH="/www/wwwroot/${PROJECT_NAME}"
DOMAIN="file.medicnex.com"
PYTHON_VERSION="3.9"

echo "📁 设置项目目录..."
mkdir -p ${PROJECT_PATH}
chown -R www:www ${PROJECT_PATH}

echo "🐍 检查Python环境..."
python3 --version
pip3 --version

echo "📦 安装系统依赖..."
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra

echo "📋 安装Python依赖..."
cd ${PROJECT_PATH}
pip3 install -r requirements.txt

echo "⚙️ 配置环境变量..."
if [ ! -f .env ]; then
    echo "❌ 请先创建 .env 文件"
    exit 1
fi

echo "🔧 配置Nginx..."
# Nginx配置已在上述步骤中提供

echo "🔄 启动服务..."
pm2 start ecosystem.config.js
pm2 save
pm2 startup

echo "🔄 重启Nginx..."
nginx -t && nginx -s reload

echo "🏥 检查服务状态..."
sleep 5
curl -f https://${DOMAIN}/health || {
    echo "❌ 服务启动失败，请检查日志"
    pm2 logs ${PROJECT_NAME}
    exit 1
}

echo "✅ 部署成功！"
echo "🌐 服务地址: https://${DOMAIN}"
echo "📚 API文档: https://${DOMAIN}/docs"
echo "🔍 健康检查: https://${DOMAIN}/health"

# 显示服务状态
pm2 status
```

## 🔧 快速操作命令

### 服务管理

```bash
# 启动服务
pm2 start medicnex-file2md

# 停止服务
pm2 stop medicnex-file2md

# 重启服务
pm2 restart medicnex-file2md

# 查看日志
pm2 logs medicnex-file2md

# 查看服务状态
pm2 status
```

### 测试命令

```bash
# 健康检查
curl https://file.medicnex.com/health

# 获取支持的文件类型
curl -H "Authorization: Bearer medicnex-2024-prod-key-f2md" \
     https://file.medicnex.com/v1/supported-types

# 测试文件上传
curl -X POST \
     -H "Authorization: Bearer medicnex-2024-prod-key-f2md" \
     -F "file=@test.txt" \
     https://file.medicnex.com/v1/convert
```

## 📊 监控检查

### 服务监控

```bash
# 检查端口占用
netstat -nlp | grep 8999

# 检查进程状态
ps aux | grep uvicorn

# 检查内存使用
free -h

# 检查磁盘空间
df -h
```

### 日志监控

```bash
# 应用日志
tail -f /www/wwwlogs/medicnex-file2md.log

# Nginx访问日志
tail -f /www/wwwlogs/file.medicnex.com.log

# Nginx错误日志
tail -f /www/wwwlogs/file.medicnex.com.error.log

# 系统日志
journalctl -f -u nginx
```

## 🔒 安全配置

### 防火墙设置

```bash
# 只允许必要端口
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 888   # 宝塔面板
ufw enable
```

### SSL证书自动续期

```bash
# 设置定时任务
crontab -e

# 添加以下行（每天检查一次）
0 2 * * * /usr/bin/certbot renew --quiet && nginx -s reload
```

## 🔄 更新部署

```bash
#!/bin/bash
# 更新脚本 update.sh

echo "🔄 开始更新服务..."

# 停止服务
pm2 stop medicnex-file2md

# 备份当前版本
cp -r /www/wwwroot/medicnex-file2md /www/wwwroot/medicnex-file2md.backup.$(date +%Y%m%d)

# 更新代码（假设使用Git）
cd /www/wwwroot/medicnex-file2md
git pull origin main

# 更新依赖
pip3 install -r requirements.txt

# 重启服务
pm2 start medicnex-file2md

echo "✅ 更新完成！"

# 验证服务
curl -f https://file.medicnex.com/health && echo "✅ 服务正常" || echo "❌ 服务异常"
```

## 📞 故障排除快速指南

| 问题 | 检查命令 | 解决方案 |
|------|----------|----------|
| 服务无法访问 | `curl https://file.medicnex.com/health` | 检查PM2和Nginx状态 |
| SSL证书问题 | `curl -k https://file.medicnex.com/health` | 更新SSL证书 |
| 文件上传失败 | `ls -la /tmp/` | 检查临时目录权限 |
| API密钥错误 | 检查 `.env` 文件 | 验证API_KEYS配置 |
| OCR不工作 | `tesseract --version` | 重装tesseract |

---

**🎉 部署完成后访问地址：**
- **主服务**: https://file.medicnex.com
- **API文档**: https://file.medicnex.com/docs  
- **健康检查**: https://file.medicnex.com/health 