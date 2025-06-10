# MedicNex File2Markdown 部署指南

## 服务概述

MedicNex File2Markdown 是一个高性能的文档转换微服务，支持：

- **90+ 种文件格式**：文档、图片、代码文件等
- **统一代码块输出**：所有文件类型均输出为Markdown代码块格式
- **智能图片识别**：OCR + 视觉模型双重识别
- **代码文件支持**：83+ 种编程语言自动识别

## 快速部署

### 方式一：本地运行

1. **克隆项目**
```bash
git clone <repository-url>
cd medicnex-file2md
```

2. **安装依赖**
```bash
pip3 install -r requirements.txt
```

3. **安装系统依赖（OCR功能）**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng

# macOS
brew install tesseract tesseract-lang

# CentOS/RHEL
sudo yum install tesseract tesseract-langpack-chi_sim tesseract-langpack-eng
```

4. **启动服务**
```bash
./start.sh
```

或手动启动：
```bash
export API_KEY="your-api-key-here"
export VISION_API_KEY="your-vision-api-key"  # 可选
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 方式二：Docker 部署

1. **构建镜像**
```bash
docker build -t medicnex-file2md .
```

2. **运行容器**
```bash
docker run -d \
  -p 8080:8080 \
  -e API_KEY="your-api-key-here" \
  -e VISION_API_KEY="your-vision-api-key" \
  -e VISION_API_BASE="https://api.openai.com/v1" \
  -e VISION_MODEL="gpt-4o-mini" \
  medicnex-file2md
```

### 方式三：Docker Compose（推荐）

1. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件设置你的 API Keys
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **查看日志**
```bash
docker-compose logs -f
```

## 环境要求

### 系统要求
- **操作系统**: Linux/macOS/Windows
- **Python**: 3.11+
- **内存**: 最小2GB，推荐4GB+
- **存储**: 最小1GB可用空间

### 系统依赖
- **tesseract-ocr**: 用于OCR功能
- **ImageMagick**: 用于PDF图片处理（可选）
- **libmagic**: 用于文件类型检测（可选）

### 支持的文件格式
- **文档类**: TXT, MD, DOCX, DOC, PDF (90+ MB)
- **演示文稿**: PPTX, PPT（提取文本内容，不使用视觉模型）  
- **表格数据**: XLSX, XLS, CSV（转换为HTML表格格式）
- **图像文件**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- **代码文件**: 83+ 种编程语言（Python, JavaScript, Java, C++, Go, Rust等）

## 配置说明

### 必需环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `API_KEY` | API密钥列表，用逗号分隔 | `key1,key2,key3` |

### 可选环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `VISION_API_KEY` | 视觉API密钥（用于图片识别） | - | `sk-vision-123` |
| `VISION_API_BASE` | 视觉API基础URL | `https://api.openai.com/v1` | `https://api.siliconflow.cn/v1` |
| `VISION_MODEL` | 视觉识别模型名称 | `gpt-4o-mini` | `Qwen/Qwen2.5-VL-72B-Instruct` |
| `OPENAI_API_KEY` | OpenAI API密钥（兼容旧配置） | - | `sk-openai-456` |
| `PORT` | 服务端口 | `8080` | `8999` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `DEBUG` |

### 配置示例

**.env 文件**:
```bash
# 必需配置
API_KEY=sk-prod-key-1,sk-prod-key-2

# 视觉识别配置（推荐）
VISION_API_KEY=sk-vision-api-key
VISION_API_BASE=https://api.openai.com/v1
VISION_MODEL=gpt-4o-mini

# 服务配置
PORT=8080
LOG_LEVEL=INFO
```

## 验证部署

### 1. 健康检查
```bash
curl http://localhost:8080/v1/health
```

预期响应：
```json
{
  "status": "UP",
  "service": "file2markdown"
}
```

### 2. 检查支持的文件类型
```bash
curl -H "Authorization: Bearer your-api-key" \
     http://localhost:8080/v1/supported-types
```

### 3. 测试文件转换

**测试代码文件**：
```bash
echo 'print("Hello, World!")' > test.py
curl -X POST http://localhost:8080/v1/convert \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@test.py"
```

预期响应：
```json
{
  "filename": "test.py",
  "size": 22,
  "content_type": "text/x-python",
  "content": "```python\nprint(\"Hello, World!\")\n```",
  "duration_ms": 45
}
```

**测试文档文件**：
```bash
curl -X POST http://localhost:8080/v1/convert \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.pdf"
```

### 4. API文档
访问：http://localhost:8080/docs

### 5. 运行完整测试
```bash
python3 test_service.py
```

## 生产环境建议

### 安全配置
1. **使用强密码的API Key**
   ```bash
   # 生成安全的API Key
   openssl rand -hex 32
   ```

2. **配置HTTPS反向代理**
   ```nginx
   server {
       listen 443 ssl;
       server_name file.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://127.0.0.1:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **配置防火墙**
   ```bash
   # 只允许必要端口
   ufw allow 22    # SSH
   ufw allow 443   # HTTPS
   ufw deny 8080   # 直接访问应用端口
   ```

### 性能优化
1. **资源配置**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     file2md:
       image: medicnex-file2md
       deploy:
         resources:
           limits:
             memory: 4G
             cpus: '2'
           reservations:
             memory: 2G
             cpus: '1'
   ```

2. **环境变量优化**
   ```bash
   # 生产环境建议
   LOG_LEVEL=WARN
   WORKERS=4  # CPU核心数
   ```

### 监控配置
1. **设置健康检查**
2. **配置日志聚合**
3. **监控服务性能指标**
4. **设置告警规则**

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查看端口占用
   sudo netstat -tlnp | grep :8080
   # 修改PORT环境变量或停止占用进程
   ```

2. **依赖安装失败**
   ```bash
   # 确保Python版本
   python3 --version  # 应为3.11+
   
   # 使用虚拟环境
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **OCR功能不可用**
   ```bash
   # 测试tesseract安装
   tesseract --version
   
   # 重新安装
   sudo apt-get install --reinstall tesseract-ocr tesseract-ocr-chi-sim
   ```

4. **图片识别失败**
   ```bash
   # 检查API配置
   echo $VISION_API_KEY
   echo $VISION_API_BASE
   
   # 测试API连接
   curl -H "Authorization: Bearer $VISION_API_KEY" \
        $VISION_API_BASE/models
   ```

5. **代码文件识别错误**
   - 检查文件扩展名是否在支持列表中
   - 验证文件编码是否正确
   - 查看日志中的详细错误信息

### 日志分析

1. **查看实时日志**
   ```bash
   # Docker方式
   docker logs -f <container-id>
   
   # Docker Compose方式
   docker-compose logs -f file2md
   ```

2. **常见错误模式**
   ```bash
   # 搜索错误
   docker logs <container-id> 2>&1 | grep ERROR
   
   # 搜索特定文件类型错误
   docker logs <container-id> 2>&1 | grep "解析.*失败"
   ```

## 监控和维护

### 性能监控
```bash
# 监控容器资源使用
docker stats

# 监控API响应时间
curl -w "@curl-format.txt" -s -o /dev/null \
     -H "Authorization: Bearer your-api-key" \
     http://localhost:8080/v1/health
```

### 自动化监控脚本
```bash
#!/bin/bash
# health-check.sh
ENDPOINT="http://localhost:8080/v1/health"
RESPONSE=$(curl -s $ENDPOINT)

if [[ $RESPONSE == *"UP"* ]]; then
    echo "Service is UP"
    exit 0
else
    echo "Service is DOWN"
    exit 1
fi
```

### 定期维护

1. **清理临时文件**
   ```bash
   # 清理/tmp目录下的临时文件
   find /tmp -name "tmp*" -mtime +1 -delete
   ```

2. **日志轮转**
   ```bash
   # 配置logrotate
   /var/log/file2md/*.log {
       daily
       rotate 7
       compress
       delaycompress
   }
   ```

3. **更新部署**
   ```bash
   # 备份当前配置
   cp .env .env.backup
   
   # 拉取最新代码
   git pull
   
   # 重新构建和部署
   docker-compose down
   docker-compose up -d --build
   
   # 验证部署
   ./health-check.sh
   ```

### 扩展部署

**负载均衡配置**:
```yaml
# docker-compose.yml
version: '3.8'
services:
  file2md-1:
    image: medicnex-file2md
    ports:
      - "8080:8080"
  
  file2md-2:
    image: medicnex-file2md
    ports:
      - "8081:8080"
  
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

---

> **更新说明**：  
> 版本 1.1 新增：  
> - 83+ 种代码文件支持  
> - 统一代码块输出格式  
> - 增强的错误处理和日志记录 