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

MedicNex File2Markdown is a FastAPI-based microservice that converts **123 file formats** (Word, PDF, PowerPoint, Excel, CSV, images, audio, video, Apple iWork suite, 82 programming languages, etc.) into unified Markdown code block format, which is LLM-friendly.

## Features

- 🔐 **API Key Authentication**: Support for multiple API key management
- 📄 **Comprehensive Format Support**: Supports **123 file formats** with 16 parser types
- 💻 **Code File Support**: Supports **82 programming languages** file conversion, covering mainstream, functional, scripting, and configuration languages
- 🖼️ **Smart Image Recognition**: Integrated Vision API and PaddleOCR, supports SVG to PNG recognition
- ⚡ **High-Performance Async**: Based on FastAPI async framework
- 🚀 **Queue Processing Mode**: Supports batch document conversion, limit the maximum number of concurrent tasks (configurable via `.env`)
- 🎯 **Concurrent Image Processing**: Multiple images in documents are processed simultaneously with PaddleOCR and AI vision recognition, improving processing speed by 2-10x. The limit can be configured via **`MAX_IMAGES_PER_DOC`** (`-1` for no limit).
- 🐳 **Containerized Deployment**: Provides Docker and Docker Compose support
- 📊 **Unified Output Format**: All file types output in unified code block format

## 📑 Table of Contents

- [📋 Unified Output Format](#-unified-output-format)
- [📂 Supported File Formats](#-supported-file-formats)
  - [📄 Document and Data Files](#-document-and-data-files)
  - [💻 Code Files (82 Programming Languages)](#-code-files-82-programming-languages)
- [🚀 Quick Start](#-quick-start)
  - [🐳 Using Docker Compose (Recommended)](#-using-docker-compose-recommended)
  - [💻 Local Development Environment](#-local-development-environment)
- [🎵 Audio and Video Processing Features](#-audio-and-video-processing-features)
- [🔗 API Usage Guide](#-api-usage-guide)
  - [📤 Single File Conversion (Sync Mode)](#-single-file-conversion-sync-mode)
  - [📦 Batch File Conversion (Async Queue Mode)](#-batch-file-conversion-async-queue-mode)
  - [📋 Query Task Status](#-query-task-status)
  - [📊 Query Queue Status](#-query-queue-status)
- [🔗 API Endpoints Overview](#-api-endpoints-overview)
- [⚙️ Configuration](#️-configuration)
  - [🔧 Environment Variables](#-environment-variables)
  - [🔑 API Key Management](#-api-key-management)
- [❌ Error Handling](#-error-handling)
- [🏗️ Architecture Design](#️-architecture-design)
- [⚡ Performance Optimization](#-performance-optimization)
- [📊 Monitoring and Logging](#-monitoring-and-logging)
- [📚 More Resources](#-more-resources)
- [🔧 Extension Development](#-extension-development)
- [📄 License](#-license)
- [🤝 Contributing](#-contributing)
- [📈 Latest Updates](#-latest-updates)

## 📋 Unified Output Format

All file conversion results use a unified code block format for easy LLM understanding and processing:

| 📁 File Type | 🏷️ Output Format | 📄 Content Example |
|------------|-------------|-------------|
| 🎞️ Slideshow Files | ```slideshow | PowerPoint/Keynote presentation content |
| 🖼️ Image Files | ```image | OCR text recognition + AI visual description |
| 📝 Plain Text Files | ```text | Original text content |
| 📄 Document Files | ```document | Word/PDF/Pages structured content |
| 📊 Spreadsheet Files | ```sheet | CSV/Excel/Numbers data tables |
| 🎵 Audio Files | ```audio | Speech transcription + timeline information |
| 🎬 Video Files | ```video | SRT subtitles + audio transcription |
| 💻 Code Files | ```python/javascript/... etc | Syntax highlighted code blocks |

## 📂 Supported File Formats

### 📄 Document and Data Files

| Format | Extensions | Parser | Output Format | Description |
|------|--------|--------|----------|------|
| Plain Text | `.txt`, `.md`, `.markdown`, `.text` | PlainParser | `text` | Direct text content reading |
| Word Documents | `.docx` | DocxParser | `document` | Extract text, tables, and formatting, **concurrent image processing** |
| Word Documents | `.doc` | DocParser | `document` | Convert via mammoth, **concurrent image processing** |
| RTF Documents | `.rtf` | RtfParser | `document` | Support RTF format, prefer Pandoc, fallback to striprtf |
| ODT Documents | `.odt` | OdtParser | `document` | OpenDocument text, support tables and lists |
| PDF Documents | `.pdf` | PdfParser | `document` | Extract text and images, **concurrent image processing** |
| Keynote Presentations | `.key` | KeynoteParser | `slideshow` | Apple Keynote presentations, extract metadata and structure |
| Pages Documents | `.pages` | PagesParser | `document` | Apple Pages word processing documents, extract metadata and structure |
| Numbers Spreadsheets | `.numbers` | NumbersParser | `sheet` | Apple Numbers spreadsheets, support table data extraction |
| PowerPoint Presentations | `.ppt`, `.pptx` | PptxParser | `slideshow` | Extract slide text content (no vision model) |
| Excel Spreadsheets | `.xls`, `.xlsx` | ExcelParser | `sheet` | Convert to HTML table format and statistics, **concurrent image processing** |
| CSV Data | `.csv` | CsvParser | `sheet` | Convert to HTML table format and data analysis |
| Image Files | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`, `.tga` | ImageParser | `image` | PaddleOCR and vision recognition |
| SVG Files | `.svg` | SvgParser | `svg` | Recognize both code structure and visual features, **convert to PNG for PaddleOCR and AI vision analysis** |
| Audio Files | `.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` | AudioParser | `audio` | **Smart speech analysis and ASR conversion** with intelligent segmentation |
| Video Files | `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` | AudioParser | `video` | **Video audio extraction and subtitle generation** with SRT format output |

### 💻 Code Files (82 Languages)

| Language Category | Supported Extensions | Output Format |
|----------|-------------|----------|
| **Mainstream Languages** | `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rs`, `.php`, `.rb` | Corresponding language code blocks |
| **Frontend Technologies** | `.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.jsx`, `.tsx`, `.svelte` | Corresponding language code blocks |
| **Script Languages** | `.r`, `.lua`, `.perl`, `.pl`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1` | Corresponding language code blocks |
| **Configuration Files** | `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.cfg`, `.conf` | Corresponding language code blocks |
| **Database and Others** | `.sql`, `.dockerfile`, `.makefile`, `.cmake`, `.gradle`, `.proto`, `.graphql` | Corresponding language code blocks |
| **Functional Languages** | `.hs`, `.lhs`, `.clj`, `.cljs`, `.elm`, `.erl`, `.ex`, `.exs`, `.fs`, `.fsx` | Corresponding language code blocks |
| **System and Tools** | `.vim`, `.vimrc`, `.env`, `.gitignore`, `.gitattributes`, `.editorconfig` | Corresponding language code blocks |

**Complete List**: Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby, R, HTML, CSS, SCSS, Sass, Less, Vue, React(JSX), Svelte, JSON, YAML, XML, SQL, Shell scripts, PowerShell, Dockerfile, Makefile, Haskell, Clojure, Elm, Erlang, Elixir, F#, Swift, Kotlin, Dart, Julia, MATLAB, LaTeX, Vim, and 82 other languages.

## 🚀 Quick Start

We provide three deployment options to choose from:

### 🐳 Using Docker Compose (Recommended)

The simplest deployment method with one-click automated deployment:

1. **Clone the project**:
```bash
git clone https://github.com/MedicNex/medicnex-file2md.git
cd medicnex-file2md
```

2. **One-click deployment**:
```bash
# Automated deployment (recommended)
./docker-deploy.sh
```

This script will automatically:
- Check Docker environment
- Generate secure API keys and Redis password
- Build Docker images
- Start all services (API + Redis + optional Nginx)
- Perform health checks

3. **Access services**:
- 🌐 API URL: http://localhost:8999
- 📖 API Documentation: http://localhost:8999/docs
- ❤️ Health Check: http://localhost:8999/v1/health
- 🔑 API Key: The deployment script will display the generated key

4. **Manage services**:
```bash
# Check service status
./docker-deploy.sh status

# View real-time logs
./docker-deploy.sh logs

# Restart services
./docker-deploy.sh restart

# Stop services
./docker-deploy.sh stop
```

### 💻 Manual Docker Compose Deployment

If you need custom configuration:

1. **Configure environment variables**:
```bash
# Copy environment variable template
cp .env.example .env

# Edit .env file, set your configurations
API_KEY=your-api-key-1,your-api-key-2
VISION_API_KEY=your-vision-api-key  # Optional, for image recognition
REDIS_PASSWORD=your-redis-password
```

2. **Start services**:
```bash
# Basic deployment
docker-compose up -d

# Include Nginx reverse proxy
docker-compose --profile with-nginx up -d
```

### 🛠️ One-Click Deployment Script (Traditional Method)

Suitable for direct deployment on Linux servers:

1. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env file
```

2. **Execute deployment**:
```bash
# Ubuntu 24.04 server deployment
sudo ./deploy.sh
```

3. **View logs**:
```bash
./monitor_logs.sh
```

### 💻 Local Development Environment

#### Standard Method

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install system dependencies:

**Ubuntu/Debian:**
```bash
# PaddleOCR will automatically download required models on first use
# No additional OCR system dependencies needed, PaddleOCR is pure Python

# SVG vision recognition support (ImageMagick recommended)
sudo apt-get install -y imagemagick libmagickwand-dev pkg-config

# Audio processing support
sudo apt-get install -y ffmpeg libavcodec-extra

# Python development tools
sudo apt-get install -y python3-dev python3-pip build-essential
```

**macOS:**
```bash
# SVG vision recognition support (choose one)
brew install freetype imagemagick  # ImageMagick support
# or
brew install cairo pkg-config  # Cairo support

# Audio processing support
brew install ffmpeg  # Audio format conversion and processing
```

3. Set environment variables:
```bash
export API_KEY="dev-test-key-123"
export VISION_API_KEY="your-vision-api-key"  # optional
```

4. Start the service:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8999 --reload
```

#### macOS Quick Deployment (Without Docker)

If you're experiencing slow Docker deployment on macOS, you can use these steps for direct local deployment:

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate
```

2. **Install dependencies**:
```bash
# First install base tools
pip install --upgrade pip setuptools wheel

# Install core dependencies individually (to avoid version conflicts)
pip install fastapi uvicorn pydantic python-multipart starlette
pip install loguru python-dotenv

# Install specific versions of PaddleOCR and PaddlePaddle (to resolve compatibility issues)
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0

# Then install other dependencies
pip install -r requirements.txt --no-deps
```

3. **Install system dependencies**:
```bash
# SVG vision recognition support (choose one)
brew install freetype imagemagick  # ImageMagick support
# or
brew install cairo pkg-config  # Cairo support

# Audio processing support
brew install ffmpeg  # Audio format conversion and processing

# Note: PaddleOCR will automatically download required models on first use
# On macOS, PaddleOCR is a pure Python implementation with no additional system dependencies
# However, it will download approximately 1GB of model files on first run, ensure good network connection
```

4. **Configure environment variables**:
Create a `.env` file in the project root directory with necessary configurations:
```
DEBUG=true
PORT=8999
MAX_CONCURRENT=5
LOG_LEVEL=INFO
REDIS_CACHE_ENABLED=false  # Set to false if Redis cache is not needed
API_KEY=your_api_key_here  # If API key authentication is required
# If you need vision API functionality, add the following configuration
# VISION_API_KEY=your_vision_api_key
```

5. **Start the service**:
```bash
python -m app.main
```
Or start directly with uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8999 --reload
```

On first startup, PaddleOCR will automatically download and cache required model files (approximately 1GB), which may take some time depending on your network speed. Subsequent starts will be faster once the models are cached.

**Note**: If you encounter an `Unknown argument: use_gpu` error during startup, this is due to PaddleOCR version compatibility issues. Use these specific versions to resolve:
```bash
pip uninstall -y paddleocr paddlepaddle
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0
```

6. **Optional: Redis cache**:
If you need Redis cache functionality, install Redis using Homebrew:
```bash
brew install redis
brew services start redis
```
Then enable Redis in your `.env` file:
```
REDIS_CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🎵 Audio and Video Processing Features

### Audio File Processing

**Supported Formats**: `.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` (8 formats)

**Core Features**:
- 🎯 **Smart Audio Preprocessing**: Automatic conversion to 16kHz mono, apply 80Hz high-pass filter to remove low-frequency noise
- 📊 **RMS Energy Analysis**: Calculate RMS of audio signal for precise voice activity detection
- 🔄 **Adaptive Threshold Detection**: Dynamic threshold based on 10th percentile + 3dB, adapts to different recording environments
- ✂️ **Smart Segmentation**: 300ms minimum silence duration, automatic merging of short segments
- ⚡ **Concurrent ASR Conversion**: Multiple audio segments processed simultaneously for ASR, significantly improving processing speed
- 📈 **Quality Assessment**: Confidence scores based on average energy calculation

### Video File Processing

**Supported Formats**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` (7 formats)

**Core Features**:
- 🎬 **Automatic Audio Extraction**: Smart detection and extraction of audio tracks from video files
- 📝 **SRT Subtitle Generation**: Generate standard timestamp format subtitles (HH:MM:SS,mmm)
- 🔄 **Unified Processing Pipeline**: Reuse audio analysis algorithms for consistent processing quality
- 📊 **Timeline Synchronization**: Precise timestamp correspondence ensuring subtitle-video sync

### Technical Configuration

**Environment Variable Configuration**:
```bash
# ASR service configuration
ASR_MODEL=whisper-1                    # ASR model name
ASR_API_BASE=https://api.openai.com/v1 # ASR API base URL
ASR_API_KEY=your-openai-api-key        # ASR API key

# Audio processing parameters
MAX_FILE_SIZE=100                      # Maximum file size (MB)
AUDIO_CONCURRENT_LIMIT=5               # Concurrent ASR requests
```

**System Dependencies**:
```bash
# Audio processing libraries (required)
pip install pydub numpy librosa

# Audio format support (optional, for more formats)
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS  
brew install ffmpeg
```

### Performance Optimization

- **Concurrent Processing**: Multiple audio segments processed simultaneously for ASR, 3-5x speed improvement
- **Smart Segmentation**: Avoid cutting in the middle of words, improving recognition accuracy
- **Adaptive Threshold**: Dynamically adjust detection parameters based on audio characteristics
- **Memory Optimization**: Stream processing for large files, avoiding memory overflow
- **Error Recovery**: Automatic fallback to time-based segmentation when ASR fails

## 🔗 API Usage Guide

### 📤 Single File Conversion (Sync Mode)

```bash
curl -X POST "https://your-domain/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@example.py"
```

Response example (Python file):
```json
{
  "filename": "example.py",
  "size": 1024,
  "content_type": "text/x-python",
  "content": "```python\ndef hello_world():\n    print('Hello, World!')\n```",
  "duration_ms": 150
}
```

### 📦 Batch File Conversion (Async Queue Mode)

Use queue mode to batch submit multiple files. The number of concurrent connections can be controlled by `MAX_CONCURRENT` in `.env`:

```bash
curl -X POST "https://your-domain/v1/convert-batch" \
  -H "Authorization: Bearer your-api-key" \
  -F "files=@document1.docx" \
  -F "files=@image1.png" \
  -F "files=@script.py"
```

Response example:
```json
{
  "submitted_tasks": [
    {
      "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "message": "Task submitted to conversion queue",
      "filename": "document1.docx",
      "status": "pending"
    }
  ],
  "total_count": 3,
  "success_count": 3,
  "failed_count": 0
}
```

### 📋 Query Task Status

```bash
curl -X GET "https://your-domain/v1/task/{task_id}" \
  -H "Authorization: Bearer your-api-key"
```

### 📊 Query Queue Status

```bash
curl -X GET "https://your-domain/v1/queue/info" \
  -H "Authorization: Bearer your-api-key"
```

Response example:
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

Response example (Image file):
```json
{
  "filename": "chart.png", 
  "size": 204800,
  "content_type": "image/png",
  "content": "```image\n# OCR:\nChart Title: Sales Data Analysis\n\n# Visual_Features:\nThis is a bar chart showing monthly sales trends...\n```",
  "duration_ms": 2500
}
```

Response example (SVG file):
```json
{
  "filename": "icon.svg",
  "size": 1024,
  "content_type": "image/svg+xml",
  "content": "```svg\n# Code\n<code class=\"language-svg\">\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\">\n  <path d=\"M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z\"/>\n</svg>\n</code>\n\n# Visual_Features: This is a five-pointed star icon with clean line design, perfectly symmetrical star shape, suitable for rating or favorite functionality.\n```",
  "duration_ms": 3200
}
```

### 🔍 Image OCR Recognition (OCR Only)

```bash
curl -X POST "https://your-domain/v1/ocr" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@document.png"
```

**Description:**  
Recognize text in uploaded images using OCR only (PaddleOCR), without calling Vision API.

**Supported formats:** JPG, JPEG, PNG, BMP, TIFF, TIF, GIF, WEBP

**Request parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes      | Image file to recognize |

**Response example:**
```json
{
  "filename": "document.png",
  "size": 204800,
  "content_type": "image/png",
  "ocr_text": "This is the recognized text from the image\nSupports multiple lines\nSupports English and Chinese",
  "duration_ms": 1200,
  "from_cache": false
}
```

**Response fields:**
- `filename`: Original file name
- `size`: File size (bytes)
- `content_type`: MIME type
- `ocr_text`: Recognized text content
- `duration_ms`: Processing time (ms)
- `from_cache`: Whether the result is from cache

**Error example:**
```json
{
  "code": "UNSUPPORTED_TYPE",
  "message": "Unsupported file type: .pdf, only image formats are supported: .jpg, .jpeg, .png, .bmp, .tiff, .tif, .gif, .webp"
}
```

## 🔗 API Endpoints Overview

| Endpoint | Method | Description |
|------|------|------|
| `/v1/convert` | POST | Single file synchronous conversion |
| `/v1/ocr` | POST | Image OCR recognition (OCR only) |
| `/v1/convert-batch` | POST | Batch file asynchronous submission |
| `/v1/task/{task_id}` | GET | Query task status |
| `/v1/queue/info` | GET | Query queue status |
| `/v1/queue/cleanup` | POST | Clean up expired tasks |
| `/v1/supported-types` | GET | Get supported file types |
| `/v1/health` | GET | Health check (with queue status)|

### Health Check

```bash
curl -X GET "https://your-domain/v1/health"
```

## ⚙️ Configuration

### 🔧 Environment Variables

| Variable | Description | Default | Required |
|--------|------|--------|------|
| `API_KEY` | API key list (comma-separated) | `dev-test-key-123` | Yes |
| `VISION_API_KEY` | Vision API key | - | No |
| `VISION_API_BASE` | Vision API base URL | `https://api.openai.com/v1` | No |
| `VISION_MODEL` | Vision recognition model name | `gpt-4o-mini` | No |
| `ASR_API_KEY` | ASR speech recognition API key | - | Required for audio features |
| `ASR_API_BASE` | ASR API base URL | `https://api.openai.com/v1` | No |
| `ASR_MODEL` | ASR model name | `whisper-1` | No |
| `PORT` | Service port | `8999` | No |
| `LOG_LEVEL` | Log level | `INFO` | No |
| `MAX_IMAGES_PER_DOC` | Max images processed per document (`-1` = unlimited) | `5` | No |

### 🔑 API Key Management

- Supports multiple API keys, separated by commas
- Use `Bearer <API_KEY>` format in the `Authorization` header

## ❌ Error Handling

| HTTP Status Code | Error Code | Description |
|------------|----------|------|
| 401 | `INVALID_API_KEY` | Invalid or missing API Key |
| 415 | `UNSUPPORTED_TYPE` | Unsupported file type |
| 422 | `PARSE_ERROR` | File parsing failed |
| 422 | `INVALID_FILE` | Invalid file |

## ⚡ Performance Optimization

- Asynchronous processing for file uploads and parsing
- **Concurrent Image Processing**: Multiple images in documents are processed simultaneously with OCR and AI vision recognition
  - Supported file types: PDF, DOC, DOCX, Excel
  - Performance improvement: 2-10x processing speed (depending on image count and network conditions)
  - Technical implementation: Use `asyncio.gather()` for concurrent PaddleOCR and vision model calls
- Automatic temporary file cleanup
- Memory-optimized streaming processing
- Support for large file processing
- Smart encoding detection

## 🔒 Security Features

- API Key authentication mechanism
- File type whitelist validation
- Secure temporary file cleanup
- Run as non-root user

## 📊 Monitoring and Logging

- Structured JSON logging
- Health check endpoints
- Processing time statistics
- Error tracking and reporting

## 📚 More Resources

### 🚀 Redis Deployment Guide
- **[Redis Cache Configuration](REDIS_CACHE_GUIDE.md)** - 📊 Redis cache optimization configuration guide

### 📖 Feature Documentation
- **[Supported File Formats](SUPPORTED_FORMATS.md)** - Detailed list of 123 supported formats and feature descriptions
- **[Conversion Examples](File2md_Examples.md)** - Detailed real conversion cases and feature demonstrations
- **[Frontend Integration Guide](File2md_API_Guide.md)** - Frontend developer integration documentation

## 🔧 Extension Development

### 📝 Adding New File Parsers

1. Inherit from `BaseParser` class
2. Implement `parse()` method
3. Register in `ParserRegistry`

Example:
```python
from app.parsers.base import BaseParser

class CustomParser(BaseParser):
    @classmethod
    def get_supported_extensions(cls):
        return ['.custom']
    
    async def parse(self, file_path: str) -> str:
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Format as code block
        return f"```custom\n{content}\n```"
```

## 🏗️ Architecture Design

### 📁 Project Structure

```
medicnex-file2md/
├── 🐳 Docker deployment files
│   ├── Dockerfile                    # Docker image build file
│   ├── docker-compose.yml           # Docker Compose service orchestration
│   ├── docker-deploy.sh             # One-click Docker deployment script
│   └── .dockerignore                # Docker build ignore file
├── 🛠️ Traditional deployment files
│   ├── deploy.sh                    # Ubuntu server one-click deployment 
│   └── monitor_logs.sh              # Log monitoring script
├── ⚙️ Configuration files
│   ├── .env.example                 # Environment variable template
│   ├── requirements.txt             # Python dependencies
│   ├── LICENSE                      # Apache License 2.0
│   └── README.md                    # Project documentation (this file)
└── 📱 Application core
    └── app/
        ├── main.py                  # FastAPI application entry
        ├── config.py                # Configuration management
        ├── auth.py                  # API Key authentication
        ├── models.py                # Pydantic data models
        ├── vision.py                # Vision recognition service
        ├── queue_manager.py         # Queue manager
        ├── cache.py                 # Redis cache management
        ├── utils.py                 # Utility functions
        ├── exceptions.py            # Exception handling
        ├── routers/
        │   └── convert.py           # Conversion API routes
        └── parsers/                 # 🔧 Parser modules (16 parsers)
            ├── base.py              # Parser base class
            ├── registry.py          # Parser registry
            ├── audio.py             # Audio/video parser (smart chunking + ASR)
            ├── code.py              # Code file parser (82 languages)
            ├── pdf.py               # PDF parser
            ├── doc.py               # Word DOC parser (legacy)
            ├── docx.py              # Word DOCX parser
            ├── excel.py             # Excel parser
            ├── pptx.py              # PowerPoint parser
            ├── csv.py               # CSV parser
            ├── numbers.py           # Apple Numbers parser
            ├── keynote.py           # Apple Keynote parser
            ├── pages.py             # Apple Pages parser
            ├── image.py             # Image parser
            ├── svg.py               # SVG parser
            ├── markdown.py          # Markdown parser
            ├── odt.py               # OpenDocument text parser
            ├── rtf.py               # RTF document parser
            └── txt.py               # Text parser
 ```

### 🐳 Containerized Architecture

**Docker Service Components**:
- **file2md-api**: Main API service, integrating PaddleOCR and all parsers
- **redis**: Cache service, improving conversion performance and queue management
- **nginx**: Reverse proxy service (optional, recommended for production)

**Data Persistence**:
- `paddleocr_models`: PaddleOCR model files persistence
- `redis_data`: Redis data persistence
- `temp_files`: Temporary file storage
- `app_logs`: Application log persistence

## 📄 License

This project is released under the [Apache License 2.0](LICENSE).

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

## 🤝 Contributing

We warmly welcome community contributions! Here's how you can participate:

### 🐛 Report Issues
- Report bugs on the [Issues](../../issues) page
- Provide detailed error information and reproduction steps
- Include your environment information (OS, Python version, etc.)

### 💡 Feature Suggestions
- Propose new features on the [Issues](../../issues) page
- Describe use cases and expected effects
- Discuss feasibility of implementation approaches

### 🔧 Code Contributions
1. **Fork** this repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add some amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Submit **Pull Request**

### 🎯 Contribution Areas
- 🔧 **New Parsers**: Add support for new file formats
- 🚀 **Performance Optimization**: Improve processing speed and memory efficiency
- 📚 **Documentation Improvement**: Enhance usage guides and API documentation
- 🐳 **Deployment Optimization**: Improve Docker and deployment scripts
- 🧪 **Test Enhancement**: Increase test coverage

For more detailed information, please refer to [Contributing Guide](CONTRIBUTING.md).

Thank you for your attention and contribution to the MedicNex File2Markdown project! 🙏

### 🎉Contributers

<div align="center">
<a href="https://github.com/MedicNex/medicnex-file2md/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=MedicNex/medicnex-file2md" />
</a>
</div>

---

## 📈 Latest Updates

### v2.6.0 (Latest)
- 🐳 **Complete Docker Support**: Brand new containerized deployment solution
  - **Dockerfile**: Optimized image based on Ubuntu 24.04, including all PaddleOCR dependencies
  - **docker-compose.yml**: Complete service orchestration including API, Redis, Nginx
  - **docker-deploy.sh**: One-click automated deployment script with automatic secure key generation
  - **Data Persistence**: Persistent storage for PaddleOCR models, Redis data, and logs
  - **Health Checks**: Built-in service health monitoring and automatic recovery
  - **Resource Limits**: Reasonable memory and CPU limit configurations
  - **Security Configuration**: Non-root user execution, automatic strong key generation
- 📋 **Documentation Optimization**: Reorganized deployment guide with three deployment options
- 🔧 **Architecture Description**: Updated project structure description with clear Docker-related files

### v2.5.0
- OCR engine switched from Tesseract to **PaddleOCR**, improving recognition accuracy

### v2.4.0
- 🎵 **Audio and Video Processing Features**: Brand new audio/video file processing support
  - **Audio Format Support**: `.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` (8 formats)
  - **Video Format Support**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` (7 formats) 
  - **Smart Audio Preprocessing**: 16kHz mono conversion, 80Hz high-pass filtering for noise removal
  - **RMS Energy Analysis**: Precise voice detection based on signal RMS
  - **Adaptive Threshold**: 10th percentile + 3dB dynamic threshold, adapts to different environments
  - **Smart Segmentation Algorithm**: 300ms minimum silence detection, automatic short segment merging
  - **Concurrent ASR Conversion**: Multiple audio segments simultaneously processed for speech recognition, 3-5x speed improvement
  - **SRT Subtitle Generation**: Automatic standard timestamp subtitle generation for video files
  - **Quality Assessment**: Confidence calculation and quality metrics based on energy
- 📊 **Statistics Update**: Supported formats increased from 109 to **123**, added AudioParser
- 🔧 **Dependency Enhancement**: Added pydub, numpy, librosa audio processing library support

### v2.3.0
- 📱 **Apple iWork Support**: Added support for Apple iWork suite
  - **Keynote (.key)**: Presentation files, extract metadata and structure, output as `slideshow` format
  - **Pages (.pages)**: Word processing documents, extract metadata and structure, output as `document` format
  - **Numbers (.numbers)**: Spreadsheet files, support table data extraction, output as `sheet` format
  - **Smart Parsing**: Numbers files prioritize `numbers-parser` library for complete table data extraction, fallback to basic parsing
- 📊 **Statistics Update**: Supported formats increased from 106 to **109**, parsers from 13 to **16**
- 🔧 **Dependency Update**: Added `numbers-parser==4.4.6` dependency for Numbers file parsing

### v2.2.0 
- 📊 **Data Update**: Complete testing and updated supported format list
  - **109 File Formats**: Complete validation of all supported extensions
  - **16 Parsers**: Optimized classification and statistics
  - **New Documentation**: Created detailed [Supported Formats List](SUPPORTED_FORMATS.md)
- 🔧 **API Enhancement**: `/v1/supported-types` endpoint returns accurate format information
- 🖼️ **SVG Features**: Enhanced SVG to PNG visual recognition (ImageMagick support)
- 🛡️ **Security Improvements**: Health check API removes sensitive information exposure

### v2.1.0 
- ✨ **New**: Concurrent image processing functionality
  - Multiple images in PDF, DOC, DOCX, Excel documents can now be processed concurrently
  - OCR and AI vision recognition run simultaneously, dramatically improving processing speed
  - Processing speed improved 2-10x (depending on image count)
- 🔧 **Optimization**: Improved exception handling and error recovery mechanisms
- 🐛 **Fix**: Resolved memory issues with large document image processing

---

<div align="center">

**🚀 MedicNex File2Markdown**

<a href="https://www.star-history.com/#MedicNex/medicnex-file2md&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=MedicNex/medicnex-file2md&type=Date" />
 </picture>
</a>

*Efficient and intelligent file conversion microservice, making AI better understand your documents*

</div> 