<div align="center">

# MedicNex File2Markdown

[English](README.md) | [中文](README_zh.md)

[![MedicNex AI](https://www.medicnex.com/static/images/medicnex-badge.svg)](https://www.medicnex.com)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)
![Docker](https://img.shields.io/badge/docker-supported-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.7+-orange.svg)
![GitHub contributors](https://img.shields.io/github/contributors/MedicNex/medicnex-file2md) 
![GitHub Repo stars](https://img.shields.io/github/stars/MedicNex/medicnex-file2md?style=social)

</div>

MedicNex File2Markdown 是一个基于 FastAPI 的微服务，可以将**123种文件格式**（Word、PDF、PowerPoint、Excel、CSV、图片、音频、视频、Apple iWork套件、82种编程语言等）转换为统一的 Markdown 代码块格式，对于 LLM 理解友好。

## 功能特性

- 🔐 **API Key 鉴权**：支持多个 API Key 管理
- 📄 **全面格式支持**：支持 **123种文件格式**，包含 16种解析器类型
- 💻 **代码文件支持**：支持 **82 种编程语言**文件转换，涵盖主流、函数式、脚本、配置等语言
- 🖼️ **智能图片识别**：集成 Vision API 和 PaddleOCR，支持 SVG 转 PNG 识别
- ⚡ **高性能异步**：基于 FastAPI 异步框架
- 🚀 **队列处理模式**：支持批量文档转换，限制最多并发任务个数（可通过`.env`配置）
- 🎯 **并发图片处理**：文档中多张图片同时进行 PaddleOCR 和 AI 视觉识别，处理速度提升 2-10 倍。通过 **`MAX_IMAGES_PER_DOC`** 环境变量可配置图片处理上限（设置为 `-1` 表示不限制）。
- 🐳 **容器化部署**：提供 Docker 和 Docker Compose 支持
- 📊 **统一输出格式**：所有文件类型统一输出为代码块格式

## 📑 目录

- [📋 统一输出格式](#-统一输出格式)
- [📂 支持的文件格式](#-支持的文件格式)
  - [📄 文档和数据文件](#-文档和数据文件)
  - [💻 代码文件（82 种编程语言）](#-代码文件82-种编程语言)
- [🚀 快速开始](#-快速开始)
  - [🐳 使用 Docker Compose（推荐）](#-使用-docker-compose推荐)
  - [💻 本地开发环境](#-本地开发环境)
- [🎵 音频和视频处理功能](#-音频和视频处理功能)
  - [音频文件处理特性](#音频文件处理特性)
  - [视频文件处理特性](#视频文件处理特性)
  - [技术配置](#技术配置)
  - [性能优化](#性能优化)
- [🔗 API 使用指南](#-api-使用指南)
  - [📤 单文件转换（同步模式）](#-单文件转换同步模式)
  - [📦 批量文件转换（异步队列模式）](#-批量文件转换异步队列模式)
  - [📋 查询任务状态](#-查询任务状态)
  - [📊 查询队列状态](#-查询队列状态)
  - [📋 获取支持的文件类型](#-获取支持的文件类型)
- [🧪 队列功能测试](#-队列功能测试)
- [🔗 API 端点总览](#-api-端点总览)
- [⚙️ 配置说明](#️-配置说明)
  - [🔧 环境变量](#-环境变量)
  - [🔑 API Key 管理](#-api-key-管理)
- [❌ 错误处理](#-错误处理)
- [🏗️ 架构设计](#️-架构设计)
- [⚡ 性能优化](#-性能优化)
- [📊 监控和日志](#-监控和日志)
- [📚 更多资源](#-更多资源)
- [🔧 扩展开发](#-扩展开发)
- [📄 许可证](#-许可证)
- [🤝 贡献](#-贡献)
- [📈 最新更新](#-最新更新)

## 📋 统一输出格式

所有文件转换结果都采用统一的代码块格式输出，便于 LLM 理解和处理：

| 📁 文件类型 | 🏷️ 输出格式 | 📄 内容示例 |
|------------|-------------|-------------|
| 🎞️ 幻灯片文件 | ```slideshow | PowerPoint/Keynote 演示内容 |
| 🖼️ 图像文件 | ```image | OCR 文字识别 + AI 视觉描述 |
| 📝 纯文本文件 | ```text | 原始文本内容 |
| 📄 文档文件 | ```document | Word/PDF/Pages 结构化内容 |
| 📊 表格文件 | ```sheet | CSV/Excel/Numbers 数据表格 |
| 🎵 音频文件 | ```audio | 语音转录 + 时间轴信息 |
| 🎬 视频文件 | ```video | SRT 字幕 + 音频转录 |
| 💻 代码文件 | ```python/javascript/... 等 | 语法高亮的代码块 |

## 📂 支持的文件格式

### 📄 文档和数据文件

| 格式 | 扩展名 | 解析器 | 输出格式 | 说明 |
|------|--------|--------|----------|------|
| 纯文本 | `.txt`, `.md`, `.markdown`, `.text` | PlainParser | `text` | 直接读取文本内容 |
| Word文档 | `.docx` | DocxParser | `document` | 提取文本、表格和格式，**并发处理图片** |
| Word文档 | `.doc` | DocParser | `document` | 通过 mammoth 转换，**并发处理图片** |
| RTF文档 | `.rtf` | RtfParser | `document` | 支持RTF格式，优先使用Pandoc，备用striprtf |
| ODT文档 | `.odt` | OdtParser | `document` | OpenDocument文本，支持表格和列表 |
| PDF文档 | `.pdf` | PdfParser | `document` | 提取文本和图片，**并发处理图片** |
| Keynote演示文稿 | `.key` | KeynoteParser | `slideshow` | Apple Keynote演示文稿，提取元数据和结构信息 |
| Pages文档 | `.pages` | PagesParser | `document` | Apple Pages文字处理文档，提取元数据和结构信息 |
| Numbers表格 | `.numbers` | NumbersParser | `sheet` | Apple Numbers电子表格，支持表格数据提取 |
| PowerPoint演示文稿 | `.ppt`, `.pptx` | PptxParser | `slideshow` | 提取幻灯片文本内容（不使用视觉模型） |
| Excel表格 | `.xls`, `.xlsx` | ExcelParser | `sheet` | 转换为HTML表格格式和统计信息，**并发处理图片** |
| CSV数据 | `.csv` | CsvParser | `sheet` | 转换为HTML表格格式和数据分析 |
| 图片文件 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`, `.tga` | ImageParser | `image` | PaddleOCR和视觉识别 |
| SVG文件 | `.svg` | SvgParser | `svg` | 同时识别代码结构和视觉特征，**转换为PNG进行PaddleOCR和AI视觉分析**（需要ImageMagick或Cairo库） |
| 音频文件 | `.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` | AudioParser | `audio` | **智能语音分析和ASR转换**，基于RMS能量分析自动分割，并发语音识别，自适应阈值检测 |
| 视频文件 | `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` | AudioParser | `video` | **视频音频提取和字幕生成**，自动提取音频轨道进行ASR转换，生成SRT格式字幕文件 |

### 💻 代码文件（82 种语言）

| 语言类别 | 支持的扩展名 | 输出格式 |
|----------|-------------|----------|
| **主流编程语言** | `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rs`, `.php`, `.rb` | 对应语言代码块 |
| **前端技术** | `.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.jsx`, `.tsx`, `.svelte` | 对应语言代码块 |
| **脚本语言** | `.r`, `.lua`, `.perl`, `.pl`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1` | 对应语言代码块 |
| **配置文件** | `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.cfg`, `.conf` | 对应语言代码块 |
| **数据库和其他** | `.sql`, `.dockerfile`, `.makefile`, `.cmake`, `.gradle`, `.proto`, `.graphql` | 对应语言代码块 |
| **函数式语言** | `.hs`, `.lhs`, `.clj`, `.cljs`, `.elm`, `.erl`, `.ex`, `.exs`, `.fs`, `.fsx` | 对应语言代码块 |
| **系统和工具** | `.vim`, `.vimrc`, `.env`, `.gitignore`, `.gitattributes`, `.editorconfig` | 对应语言代码块 |
| **Web框架** | `.astro`, `.postcss`, `.styl` | 对应语言代码块 |
| **科学计算** | `.m`, `.mat`, `.tex`, `.jl` | 对应语言代码块 |
| **移动开发** | `.swift`, `.kt`, `.dart` | 对应语言代码块 |

**完整支持列表**：Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby, R, HTML, CSS, SCSS, Sass, Less, Vue, React(JSX), Svelte, JSON, YAML, XML, SQL, Shell scripts, PowerShell, Dockerfile, Makefile, Haskell, Clojure, Elm, Erlang, Elixir, F#, Swift, Kotlin, Dart, Julia, MATLAB, LaTeX, Vim, 等82种语言。

## 🚀 快速开始

我们提供三种部署方式，您可以选择最适合的方案：

### 🐳 使用 Docker Compose（推荐）

最简单的部署方式，支持一键自动化部署，适用于Linux生产环境：

1. **克隆项目**：
```bash
git clone https://github.com/MedicNex/medicnex-file2md.git
cd medicnex-file2md
```

2. **一键部署**：
```bash
# 自动化部署（推荐）
./docker-deploy.sh
```

该脚本会自动：
- 检查Docker环境
- 生成安全的API密钥和Redis密码
- 构建Docker镜像
- 启动所有服务（API + Redis + 可选Nginx）
- 执行健康检查

3. **访问服务**：
- 🌐 API地址：http://localhost:8999
- 📖 API文档：http://localhost:8999/docs
- ❤️ 健康检查：http://localhost:8999/v1/health
- 🔑 API密钥：部署脚本会显示生成的密钥

4. **管理服务**：
```bash
# 查看服务状态
./docker-deploy.sh status

# 查看实时日志
./docker-deploy.sh logs

# 重启服务
./docker-deploy.sh restart

# 停止服务
./docker-deploy.sh stop
```

**详细文档**：📋 [Docker部署指南](DOCKER_DEPLOY_README.md)

### 💻 手动 Docker Compose 部署

如果您需要自定义配置：

1. **配置环境变量**：
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置你的配置
API_KEY=your-api-key-1,your-api-key-2
VISION_API_KEY=your-vision-api-key  # 可选，用于图片识别
REDIS_PASSWORD=your-redis-password
```

2. **启动服务**：
```bash
# 基础部署
docker-compose up -d

# 包含Nginx反向代理
docker-compose --profile with-nginx up -d
```

### 🛠️ 一键部署脚本（传统方式）

适用于直接在Linux服务器上部署：

1. **配置环境变量**：
```bash
cp .env.example .env
# 编辑 .env 文件
```

2. **执行部署**：
```bash
# Ubuntu 24.04 服务器部署
sudo ./deploy.sh
```

3. **查看日志**：
```bash
./monitor_logs.sh
```

### 💻 本地开发环境

#### 标准方式

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 安装系统依赖：

**Ubuntu/Debian：**
```bash
# PaddleOCR会在首次使用时自动下载所需模型
# 无需额外安装 OCR 系统依赖，PaddleOCR 为纯 Python 实现

# SVG视觉识别支持（推荐ImageMagick）
sudo apt-get install -y imagemagick libmagickwand-dev pkg-config

# 音频处理支持
sudo apt-get install -y ffmpeg libavcodec-extra

# Python开发工具
sudo apt-get install -y python3-dev python3-pip build-essential
```

**CentOS/RHEL：**
```bash
# 基础OCR支持
sudo yum update -y
sudo yum install -y epel-release
sudo yum install -y tesseract tesseract-langpack-chi-sim tesseract-langpack-eng

# SVG视觉识别支持
sudo yum install -y ImageMagick ImageMagick-devel pkgconfig

# 音频处理支持
sudo yum install -y ffmpeg ffmpeg-devel

# Python开发工具
sudo yum install -y python3-devel python3-pip gcc gcc-c++ make
```

**macOS：**
```bash
brew install tesseract tesseract-lang

# 可选：SVG视觉识别支持（二选一）
brew install freetype imagemagick  # ImageMagick支持
# 或者
brew install cairo pkg-config  # Cairo支持

# 音频处理支持
brew install ffmpeg  # 音频格式转换和处理
```

3. 设置环境变量：
```bash
export API_KEY="dev-test-key-123"
export VISION_API_KEY="your-vision-api-key"  # 可选
```

4. 启动服务：
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

#### macOS 快速部署方式（不使用Docker）

如果您在macOS上遇到Docker部署速度慢的问题，可以使用以下步骤直接在本地部署：

1. **创建虚拟环境**：
```bash
python -m venv venv
source venv/bin/activate
```

2. **安装依赖**：
```bash
# 先安装基础工具
pip install --upgrade pip setuptools wheel

# 逐个安装核心依赖（避免版本冲突）
pip install fastapi uvicorn pydantic python-multipart starlette
pip install loguru python-dotenv

# 安装特定版本的PaddleOCR和PaddlePaddle（解决兼容性问题）
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0

# 然后安装其他依赖
pip install -r requirements.txt --no-deps
```

3. **安装系统依赖**：
```bash
# SVG视觉识别支持（二选一）
brew install freetype imagemagick  # ImageMagick支持
# 或者
brew install cairo pkg-config  # Cairo支持

# 音频处理支持
brew install ffmpeg  # 音频格式转换和处理

# 注意：PaddleOCR会在首次使用时自动下载所需模型
# 在macOS上，PaddleOCR为纯Python实现，无需额外系统依赖
# 但首次运行时会下载约1GB的模型文件，请确保网络连接良好
```

4. **配置环境变量**：
创建一个`.env`文件在项目根目录，包含必要的配置：
```
DEBUG=true
PORT=8080
MAX_CONCURRENT=5
LOG_LEVEL=INFO
REDIS_CACHE_ENABLED=false  # 如果不需要Redis缓存，设为false
API_KEY=your_api_key_here  # 如果需要API密钥验证
# 如果需要使用视觉API功能，添加以下配置
# VISION_API_KEY=your_vision_api_key
```

5. **启动服务**：
```bash
python -m app.main
```
或者使用uvicorn直接启动：
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

首次启动时，PaddleOCR会自动下载并缓存所需模型文件（约1GB），这可能需要一些时间，取决于您的网络速度。下载完成后，后续启动将会更快。

**注意**：如果启动时遇到 `Unknown argument: use_gpu` 错误，这是因为PaddleOCR版本兼容性问题。请使用以下特定版本解决：
```bash
pip uninstall -y paddleocr paddlepaddle
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0
```

6. **可选：Redis缓存**：
如果需要Redis缓存功能，可以使用Homebrew安装Redis：
```bash
brew install redis
brew services start redis
```
然后在`.env`文件中启用Redis：
```
REDIS_CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🎵 音频和视频处理功能

### 音频文件处理特性

**支持格式**：`.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` (8种格式)

**核心功能**：
- 🎯 **智能音频预处理**：自动转换为16kHz单声道，应用80Hz高通滤波去除低频噪音
- 📊 **RMS能量分析**：计算音频信号的有效值，精确识别语音活动区域
- 🔄 **自适应阈值检测**：基于10百分位数+3dB的动态阈值，适应不同录音环境
- ✂️ **智能分割**：最小静音时长300ms，自动合并短段，避免过度分割
- ⚡ **并发ASR转换**：多段音频同时进行语音识别，大幅提升处理速度
- 📈 **质量评估**：基于平均能量计算置信度分数，评估转录质量

### 视频文件处理特性

**支持格式**：`.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` (7种格式)

**核心功能**：
- 🎬 **自动音频提取**：智能检测并提取视频文件中的音频轨道
- 📝 **SRT字幕生成**：生成标准时间戳格式的字幕文件 (HH:MM:SS,mmm)
- 🔄 **统一处理流程**：复用音频分析算法，保证一致的处理质量
- 📊 **时间轴同步**：精确的时间戳对应，确保字幕与视频同步

### 技术配置

**环境变量配置**：
```bash
# ASR服务配置
ASR_MODEL=whisper-1                    # ASR模型名称
ASR_API_BASE=https://api.openai.com/v1 # ASR API基础URL
ASR_API_KEY=your-openai-api-key        # ASR API密钥

# 音频处理参数
MAX_FILE_SIZE=100                      # 最大文件大小(MB)
AUDIO_CONCURRENT_LIMIT=5               # 并发ASR请求数
```

**系统依赖**：
```bash
# 音频处理库（必需）
pip install pydub numpy librosa

# 音频格式支持（可选，用于更多格式）
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS  
brew install ffmpeg
```

### 性能优化

- **并发处理**：多段音频同时进行ASR转换，处理速度提升3-5倍
- **智能分割**：避免在词语中间切断，提高识别准确率
- **自适应阈值**：根据音频特征动态调整检测参数
- **内存优化**：流式处理大文件，避免内存溢出
- **错误恢复**：ASR失败时自动回退到时间分割模式

## 🔗 API 使用指南

### 📤 单文件转换（同步模式）

```bash
curl -X POST "https://your-domain/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@example.py"
```

响应示例（Python文件）：
```json
{
  "filename": "example.py",
  "size": 1024,
  "content_type": "text/x-python",
  "content": "```python\ndef hello_world():\n    print('Hello, World!')\n```",
  "duration_ms": 150
}
```

### 📦 批量文件转换（异步队列模式）

使用队列模式批量提交多个文件，可通过`.env`中的`MAX_CONCURRENT`控制并发数量：

```bash
curl -X POST "https://your-domain/v1/convert-batch" \
  -H "Authorization: Bearer your-api-key" \
  -F "files=@document1.docx" \
  -F "files=@image1.png" \
  -F "files=@script.py"
```

响应示例：
```json
{
  "submitted_tasks": [
    {
      "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "message": "任务已提交到转换队列",
      "filename": "document1.docx",
      "status": "pending"
    },
    {
      "task_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
      "message": "任务已提交到转换队列",
      "filename": "image1.png",
      "status": "pending"
    },
    {
      "task_id": "c3d4e5f6-g7h8-9012-cdef-123456789012",
      "message": "任务已提交到转换队列",
      "filename": "script.py",
      "status": "pending"
    }
  ],
  "total_count": 3,
  "success_count": 3,
  "failed_count": 0
}
```

### 📋 查询任务状态

```bash
curl -X GET "https://your-domain/v1/task/{task_id}" \
  -H "Authorization: Bearer your-api-key"
```

响应示例（完成状态）：
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "document1.docx",
  "file_size": 15970,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "status": "completed",
  "created_at": "2024-01-20T10:30:00",
  "started_at": "2024-01-20T10:30:05",
  "completed_at": "2024-01-20T10:30:20",
  "duration_ms": 15000,
  "result": "```document\n文档内容...\n```",
  "error": null
}
```

### 📊 查询队列状态

```bash
curl -X GET "https://your-domain/v1/queue/info" \
  -H "Authorization: Bearer your-api-key"
```

响应示例：
```json
{
  "max_concurrent": 5,
  "queue_size": 2,
  "active_tasks": 3,
  "total_tasks": 10,
  "pending_count": 2,
  "processing_count": 3,
  "completed_count": 4,
  "failed_count": 1
}
```

响应示例（图片文件）：
```json
{
  "filename": "chart.png", 
  "size": 204800,
  "content_type": "image/png",
  "content": "```image\n# OCR:\n图表标题：销售数据分析\n\n# Visual_Features:\n这是一个显示月度销售趋势的柱状图...\n```",
  "duration_ms": 2500
}
```

响应示例（SVG文件）：
```json
{
  "filename": "icon.svg",
  "size": 1024,
  "content_type": "image/svg+xml",
  "content": "```svg\n# Code\n<code class=\"language-svg\">\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\">\n  <path d=\"M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z\"/>\n</svg>\n</code>\n\n# Visual_Features: 这是一个五角星图标，使用简洁的线条设计，星形完整对称，适合用作评分或收藏功能的图标元素。\n```",
  "duration_ms": 3200
}
```

## 🧪 队列功能测试

我们提供了一个完整的测试脚本来验证队列功能：

```bash
# 安装测试依赖
pip install aiohttp

# 设置环境变量（如果未设置）
export API_KEY="dev-test-key-123"

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

测试脚本将验证以下功能：
- ✅ 单文件同步转换
- ✅ 批量文件异步提交
- ✅ 任务状态查询  
- ✅ 队列状态监控
- ✅ 并发限制
- ✅ 任务完成检测

### 队列功能特点

🚀 **新增队列模式的主要优势：**

1. **并发控制**：通过 `.env` 中的变量 "MAX_CONCURRENT" 限制多个文档同时处理，避免系统过载
2. **异步处理**：客户端立即获得任务ID，无需等待处理完成
3. **状态跟踪**：实时查询每个任务的处理状态和进度
4. **队列管理**：自动排队处理，支持大批量文档转换
5. **资源优化**：合理利用系统资源，提升整体吞吐量

## 🔗 API 端点总览

| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/convert` | POST | 单文件同步转换 |
| `/v1/convert-batch` | POST | 批量文件异步提交 |
| `/v1/task/{task_id}` | GET | 查询任务状态 |
| `/v1/queue/info` | GET | 查询队列状态 |
| `/v1/queue/cleanup` | POST | 清理过期任务 |
| `/v1/supported-types` | GET | 获取支持的文件类型 |
| `/v1/health` | GET | 健康检查（含队列状态）|

### 健康检查

```bash
curl -X GET "https://your-domain/v1/health"
```

## ⚙️ 配置说明

### 🔧 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `API_KEY` | API密钥列表（逗号分隔） | `dev-test-key-123` | 是 |
| `VISION_API_KEY` | 视觉API密钥 | - | 否 |
| `VISION_API_BASE` | 视觉API基础URL | `https://api.openai.com/v1` | 否 |
| `VISION_MODEL` | 视觉识别模型名称 | `gpt-4o-mini` | 否 |
| `ASR_API_KEY` | ASR语音识别API密钥 | - | 音频功能必需 |
| `ASR_API_BASE` | ASR API基础URL | `https://api.openai.com/v1` | 否 |
| `ASR_MODEL` | ASR模型名称 | `whisper-1` | 否 |
| `PORT` | 服务端口 | `8080` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `MAX_IMAGES_PER_DOC` | 当文档中的图片数量超过此值时跳过图片处理（`-1` 表示不限制） | `5` | 否 |

### 🔑 API Key 管理

- 支持多个 API Key，用逗号分隔
- 在 `Authorization` 头中使用 `Bearer <API_KEY>` 格式

## ❌ 错误处理

| HTTP状态码 | 错误代码 | 说明 |
|------------|----------|------|
| 401 | `INVALID_API_KEY` | API Key 无效或缺失 |
| 415 | `UNSUPPORTED_TYPE` | 不支持的文件类型 |
| 422 | `PARSE_ERROR` | 文件解析失败 |
| 422 | `INVALID_FILE` | 文件无效 |

## 🏗️ 架构设计

### 📁 项目结构

```
medicnex-file2md/
├── 🐳 Docker 部署文件
│   ├── Dockerfile                    # Docker镜像构建文件
│   ├── docker-compose.yml           # Docker Compose服务编排
│   ├── docker-deploy.sh             # 一键Docker部署脚本
│   └── .dockerignore                # Docker构建忽略文件
├── 🛠️ 传统部署文件
│   ├── deploy.sh                    # Ubuntu服务器一键部署脚本
│   └── monitor_logs.sh              # 日志监控脚本
├── ⚙️ 配置文件
│   ├── .env.example                 # 环境变量模板
│   ├── requirements.txt             # Python依赖包
│   ├── LICENSE                      # Apache License 2.0许可证
│   └── DEPLOYMENT.md                # 部署说明文档
├── 📚 文档
│   ├── README.md                    # 项目主文档（本文件）
│   ├── CONTRIBUTING.md              # 贡献指南
│   ├── SUPPORTED_FORMATS.md         # 支持格式详细列表
│   ├── File2md_API_Guide.md         # API使用指南
│   ├── File2md_Examples.md          # 转换示例文档
│   └── REDIS_CACHE_GUIDE.md         # Redis缓存配置指南
└── 📱 应用核心
    └── app/
        ├── main.py                  # FastAPI 应用入口
        ├── config.py                # 配置管理
        ├── auth.py                  # API Key 鉴权
        ├── models.py                # Pydantic 数据模型
        ├── vision.py                # 视觉识别服务
        ├── queue_manager.py         # 队列管理器
        ├── cache.py                 # Redis缓存管理
        ├── utils.py                 # 工具函数
        ├── exceptions.py            # 异常处理
        ├── routers/
        │   └── convert.py           # 转换API路由
        └── parsers/                 # 🔧 解析器模块（16种解析器）
            ├── base.py              # 解析器基类
            ├── registry.py          # 解析器注册表
            ├── audio.py             # 音频/视频解析器（智能分块+ASR）
            ├── code.py              # 代码文件解析器（82种语言）
            ├── pdf.py               # PDF解析器
            ├── doc.py               # Word DOC解析器（旧版）
            ├── docx.py              # Word DOCX解析器
            ├── excel.py             # Excel解析器
            ├── pptx.py              # PowerPoint解析器
            ├── csv.py               # CSV解析器
            ├── numbers.py           # Apple Numbers解析器
            ├── keynote.py           # Apple Keynote解析器
            ├── pages.py             # Apple Pages解析器
            ├── image.py             # 图片解析器
            ├── svg.py               # SVG解析器
            ├── markdown.py          # Markdown解析器
            ├── odt.py               # OpenDocument文本解析器
            ├── rtf.py               # RTF文档解析器
            └── txt.py               # 文本解析器
```

### 🐳 容器化架构

**Docker服务组件**：
- **file2md-api**: 主API服务，集成PaddleOCR和所有解析器
- **redis**: 缓存服务，提升转换性能和队列管理
- **nginx**: 反向代理服务（可选，生产环境推荐）

**数据持久化**：
- `paddleocr_models`: PaddleOCR模型文件持久化
- `redis_data`: Redis数据持久化
- `temp_files`: 临时文件存储
- `app_logs`: 应用日志持久化

## ⚡ 性能优化

- 异步处理文件上传和解析
- **并发图片处理**：文档中多张图片同时进行 OCR 和 AI 视觉识别
  - 支持文件类型：PDF、DOC、DOCX、Excel
  - 性能提升：2-10倍处理速度（取决于图片数量和网络状况）
  - 技术实现：使用 `asyncio.gather()` 并发执行 PaddleOCR 和视觉模型调用
- 临时文件自动清理
- 内存优化的流式处理
- 支持大文件处理
- 智能编码检测

## 🔒 安全特性

- API Key 鉴权机制
- 文件类型白名单验证
- 临时文件安全清理
- 非 root 用户运行

## 📊 监控和日志

- 结构化 JSON 日志
- 健康检查端点
- 处理时间统计
- 错误追踪和报告

## 📚 更多资源

### 🚀 Redis 部署指南
- **[Redis缓存配置](REDIS_CACHE_GUIDE.md)** - 📊 Redis缓存优化配置指南

### 📖 功能文档
- **[支持的文件格式](SUPPORTED_FORMATS.md)** - 详细的123种支持格式列表和功能说明
- **[转换示例文档](File2md_Examples.md)** - 详细的实际转换案例和功能演示
- **[前端集成指南](File2md_API_Guide.md)** - 前端开发者接入文档

## 🔧 扩展开发

### 📝 添加新的文件解析器

1. 继承 `BaseParser` 类
2. 实现 `parse()` 方法
3. 在 `ParserRegistry` 中注册

示例：
```python
from app.parsers.base import BaseParser

class CustomParser(BaseParser):
    @classmethod
    def get_supported_extensions(cls):
        return ['.custom']
    
    async def parse(self, file_path: str) -> str:
        # 读取文件内容
        with open(file_path, 'r') as f:
            content = f.read()
        
        # 格式化为代码块
        return f"```custom\n{content}\n```"
```

## 📄 许可证

本项目基于 [Apache License 2.0](LICENSE) 开源许可证发布。

```
Copyright 2025 MedicNex

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## 🤝 贡献

我们热烈欢迎社区贡献！以下是参与贡献的方式：

### 🐛 报告问题
- 在 [Issues](../../issues) 页面报告 Bug
- 提供详细的错误信息和复现步骤
- 包含您的环境信息（操作系统、Python版本等）

### 💡 功能建议
- 在 [Issues](../../issues) 页面提出新功能建议
- 描述功能的使用场景和预期效果
- 讨论实现方案的可行性

### 🔧 代码贡献
1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 📋 贡献指南
- 遵循现有的代码风格和规范
- 为新功能添加相应的测试
- 更新相关文档
- 确保所有测试通过
- 在 PR 中清楚描述更改内容

### 🎯 贡献领域
- 🔧 **新解析器**：添加对新文件格式的支持
- 🚀 **性能优化**：提升处理速度和内存效率
- 📚 **文档改进**：完善使用指南和API文档
- 🐳 **部署优化**：改进Docker和部署脚本
- 🧪 **测试完善**：增加测试覆盖率

更多详细信息请参阅 [贡献指南](CONTRIBUTING.md)。

感谢您对 MedicNex File2Markdown 项目的关注和贡献！🙏

### 🎉贡献者

<div align="center">
<a href="https://github.com/MedicNex/medicnex-file2md/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MedicNex/medicnex-file2md" />
</a>
</div>

---

## 📈 最新更新

### v2.6.0（最新）
- 🐳 **Docker完整支持**：全新的容器化部署方案
  - **Dockerfile**: 基于Ubuntu 24.04的优化镜像，包含PaddleOCR所有依赖
  - **docker-compose.yml**: 完整的服务编排，包含API、Redis、Nginx
  - **docker-deploy.sh**: 一键自动化部署脚本，自动生成安全密钥
  - **数据持久化**: PaddleOCR模型、Redis数据、日志的持久化存储
  - **健康检查**: 内置的服务健康监控和自动恢复
  - **资源限制**: 合理的内存和CPU限制配置
  - **安全配置**: 非root用户运行，自动生成强密钥
- 📋 **文档优化**: 重新组织部署指南，提供三种部署方式选择
- 🔧 **架构说明**: 更新项目结构说明，清晰展示Docker相关文件

### v2.5.0
- OCR 引擎从 Tesseract 换成 **PaddleOCR**，提高识别准确率

### v2.4.0
- 🎵 **音频和视频处理功能**：全新的音频/视频文件处理支持
  - **音频格式支持**：`.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` (8种格式)
  - **视频格式支持**：`.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` (7种格式) 
  - **智能音频预处理**：16kHz单声道转换，80Hz高通滤波去除噪音
  - **RMS能量分析**：基于信号有效值的精确语音检测
  - **自适应阈值**：10百分位数+3dB动态阈值，适应不同环境
  - **智能分割算法**：300ms最小静音检测，自动合并短段
  - **并发ASR转换**：多段音频同时语音识别，3-5倍速度提升
  - **SRT字幕生成**：视频文件自动生成标准时间戳字幕
  - **质量评估**：基于能量的置信度计算和质量指标
- 📊 **统计更新**：支持格式从109种增加到**123种**，新增AudioParser解析器
- 🔧 **依赖增强**：新增pydub、numpy、librosa音频处理库支持

### v2.3.0
- 📱 **Apple iWork 支持**：新增对 Apple iWork 套件的支持
  - **Keynote (.key)**：演示文稿文件，提取元数据和结构信息，输出为 `slideshow` 格式
  - **Pages (.pages)**：文字处理文档，提取元数据和结构信息，输出为 `document` 格式
  - **Numbers (.numbers)**：电子表格文件，支持表格数据提取，输出为 `sheet` 格式
  - **智能解析**：Numbers文件优先使用 `numbers-parser` 库提取完整表格数据，回退到基础解析
- 📊 **统计更新**：支持格式从106种增加到**109种**，解析器从13个增加到**16个**
- 🔧 **依赖更新**：添加 `numbers-parser==4.4.6` 依赖以支持Numbers文件解析

### v2.2.0 
- 📊 **数据更新**：完整测试并更新支持格式列表
  - **109种文件格式**：完整验证所有支持的扩展名
  - **16个解析器**：优化分类和统计信息
  - **新增文档**：创建详细的[支持格式列表](SUPPORTED_FORMATS.md)
- 🔧 **API增强**：`/v1/supported-types` 端点返回准确的格式信息
- 🖼️ **SVG功能**：完善SVG转PNG的视觉识别功能（ImageMagick支持）
- 🛡️ **安全改进**：健康检查API移除敏感信息暴露

### v2.1.0 
- ✨ **新增**：并发图片处理功能
  - PDF、DOC、DOCX、Excel 文档中的多张图片现在可以并发处理
  - OCR 和 AI 视觉识别同时进行，大幅提升处理速度
  - 处理速度提升 2-10 倍（取决于图片数量）
- 🔧 **优化**：改进了异常处理和错误恢复机制
- 🐛 **修复**：解决了大型文档图片处理的内存问题

---

<div align="center">

## **🚀 MedicNex File2Markdown**

<a href="https://www.star-history.com/#MedicNex/medicnex-file2md&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date" />
 </picture>
</a>

*高效智能的文件转换微服务，让 AI 更好地理解您的文档*

</div>