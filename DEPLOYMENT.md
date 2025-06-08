# MedicNex File2Markdown 部署指南

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

3. **启动服务**
```bash
./start.sh
```

或手动启动：
```bash
export AGENT_API_KEYS="your-api-key-here"
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
  -e AGENT_API_KEYS="your-api-key-here" \
  -e OPENAI_API_KEY="your-openai-key" \
  medicnex-file2md
```

### 方式三：Docker Compose

1. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件设置你的 API Keys
```

2. **启动服务**
```bash
docker-compose up -d
```

## 环境要求

- Python 3.11+
- 系统依赖：tesseract-ocr（用于OCR功能）
- 可选：OpenAI API Key（用于图片智能识别）

## 配置说明

### 必需环境变量

- `AGENT_API_KEYS`: API密钥列表，用逗号分隔

### 可选环境变量

- `VISION_API_KEY`: 视觉API密钥（用于图片识别）
- `VISION_API_BASE`: 视觉API基础URL（默认OpenAI）
- `VISION_MODEL`: 视觉识别模型名称（默认gpt-4o-mini）
- `OPENAI_API_KEY`: OpenAI API密钥（兼容旧配置）
- `PORT`: 服务端口（默认8080）
- `LOG_LEVEL`: 日志级别（默认INFO）

## 验证部署

1. **健康检查**
```bash
curl http://localhost:8080/v1/health
```

2. **API文档**
访问：http://localhost:8080/docs

3. **运行测试**
```bash
python3 test_service.py
```

## 生产环境建议

1. **使用强密码的API Key**
2. **配置HTTPS反向代理**
3. **设置适当的日志级别**
4. **监控服务健康状态**
5. **定期备份配置**

## 故障排除

### 常见问题

1. **端口被占用**
   - 修改PORT环境变量
   - 或停止占用端口的进程

2. **依赖安装失败**
   - 确保Python版本3.11+
   - 使用虚拟环境

3. **OCR功能不可用**
   - 安装tesseract-ocr
   - Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
   - macOS: `brew install tesseract`

4. **图片识别失败**
   - 检查VISION_API_KEY是否正确设置
   - 验证VISION_API_BASE端点是否可访问
   - 确认VISION_MODEL模型名称正确
   - 确保API Key有足够的额度

## 监控和维护

### 日志查看
```bash
# Docker方式
docker logs <container-id>

# 本地运行
# 日志输出到stderr
```

### 性能监控
- 监控 `/v1/health` 端点
- 检查响应时间和错误率
- 监控内存和CPU使用率

### 更新部署
```bash
# 拉取最新代码
git pull

# 重新构建和部署
docker-compose down
docker-compose up -d --build
``` 