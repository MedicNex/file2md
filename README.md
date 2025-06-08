# MedicNex File2Markdown 服务

一个基于 FastAPI 的微服务，可以将各种文档格式（Word、PDF、PowerPoint、Excel、CSV、图片、代码文件等）转换为 Markdown 文本。

## 功能特性

- 🔐 **API Key 鉴权**：支持多个 API Key 管理
- 📄 **多格式支持**：支持 TXT、MD、DOCX、DOC、PDF、PPTX、XLS、XLSX、CSV、图片、代码文件等格式
- 💻 **代码文件支持**：支持 83+ 种编程语言文件转换
- 🖼️ **智能图片识别**：集成 OpenAI Vision API 和 Tesseract OCR
- ⚡ **高性能异步**：基于 FastAPI 异步框架
- 🐳 **容器化部署**：提供 Docker 和 Docker Compose 支持
- 📊 **统一输出格式**：所有文件类型统一输出为代码块格式

## 统一输出格式

所有文件转换结果都采用统一的代码块格式输出：

| 文件类型 | 输出格式 | 示例 |
|----------|----------|------|
| 幻灯片文件 | `````slideshow` | PowerPoint 内容 |
| 图像文件 | `````image` | OCR + 视觉描述 |
| 纯文本文件 | `````text` | 文本内容 |
| 文档文件 | `````document` | Word/PDF 内容 |
| 表格文件 | `````sheet` | Excel/CSV 数据 |
| 代码文件 | `````python`、`````javascript` 等 | 对应语言代码块 |

## 支持的文件格式

### 文档和数据文件

| 格式 | 扩展名 | 解析器 | 输出格式 | 说明 |
|------|--------|--------|----------|------|
| 纯文本 | `.txt`, `.md`, `.markdown`, `.text` | PlainParser | `text` | 直接读取文本内容 |
| Word文档 | `.docx` | DocxParser | `document` | 提取文本、表格和格式 |
| Word文档 | `.doc` | DocParser | `document` | 通过 mammoth 转换 |
| PDF文档 | `.pdf` | PdfParser | `document` | 提取文本和图片 |
| PowerPoint | `.ppt`, `.pptx` | PptxParser | `slideshow` | 提取幻灯片内容 |
| Excel表格 | `.xls`, `.xlsx` | ExcelParser | `sheet` | 转换为表格和统计信息 |
| CSV数据 | `.csv` | CsvParser | `sheet` | 数据分析和表格展示 |
| 图片文件 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp` | ImageParser | `image` | OCR和视觉识别 |

### 代码文件（83+ 种语言）

| 语言类别 | 支持的扩展名 | 输出格式 |
|----------|-------------|----------|
| **主流编程语言** | `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rs`, `.php`, `.rb` | 对应语言代码块 |
| **前端技术** | `.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.jsx`, `.tsx`, `.svelte` | 对应语言代码块 |
| **脚本语言** | `.r`, `.R`, `.lua`, `.perl`, `.pl`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1` | 对应语言代码块 |
| **配置文件** | `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.cfg`, `.conf` | 对应语言代码块 |
| **其他** | `.sql`, `.dockerfile`, `.makefile`, `.cmake`, `.gradle`, `.proto`, `.graphql` | 对应语言代码块 |

**完整支持列表**：Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby, R, HTML, CSS, SCSS, Sass, Less, Vue, React(JSX), Svelte, JSON, YAML, XML, SQL, Shell scripts, PowerShell, Dockerfile, Makefile, 等83+种语言。

## 快速开始

### 使用 Docker Compose（推荐）

1. 克隆项目：
```bash
git clone <repository-url>
cd medicnex-file2md
```

2. 配置环境变量：
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置你的 API Keys
AGENT_API_KEYS=your-api-key-1,your-api-key-2
VISION_API_KEY=your-vision-api-key  # 可选，用于图片识别
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问服务：
- API 文档：https://file.medicnex.com/docs
- 健康检查：https://file.medicnex.com/v1/health

### 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 安装系统依赖（Ubuntu/Debian）：
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

3. 设置环境变量：
```bash
export AGENT_API_KEYS="dev-test-key-123"
export VISION_API_KEY="your-vision-api-key"  # 可选
```

4. 启动服务：
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## API 使用

### 文件转换

```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@example.py"
```

响应示例（Python文件）：
```json
{
  "filename": "example.py",
  "size": 1024,
  "content_type": "text/x-python",
  "markdown": "```python\ndef hello_world():\n    print('Hello, World!')\n```",
  "duration_ms": 150
}
```

响应示例（图片文件）：
```json
{
  "filename": "chart.png", 
  "size": 204800,
  "content_type": "image/png",
  "markdown": "```image\n# OCR:\n图表标题：销售数据分析\n\n# Description:\n这是一个显示月度销售趋势的柱状图...\n```",
  "duration_ms": 2500
}
```

### 获取支持的文件类型

```bash
curl -X GET "https://file.medicnex.com/v1/supported-types" \
  -H "Authorization: Bearer your-api-key"
```

### 健康检查

```bash
curl -X GET "https://file.medicnex.com/v1/health"
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `AGENT_API_KEYS` | API密钥列表（逗号分隔） | `dev-test-key-123` | 是 |
| `VISION_API_KEY` | 视觉API密钥 | - | 否 |
| `VISION_API_BASE` | 视觉API基础URL | `https://api.openai.com/v1` | 否 |
| `VISION_MODEL` | 视觉识别模型名称 | `gpt-4o-mini` | 否 |
| `OPENAI_API_KEY` | OpenAI API密钥（兼容旧配置） | - | 否 |
| `PORT` | 服务端口 | `8080` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |

### API Key 管理

- 支持多个 API Key，用逗号分隔
- 在 `Authorization` 头中使用 `Bearer <API_KEY>` 格式
- 开发环境默认提供测试密钥：`dev-test-key-123`

## 错误处理

| HTTP状态码 | 错误代码 | 说明 |
|------------|----------|------|
| 401 | `INVALID_API_KEY` | API Key 无效或缺失 |
| 415 | `UNSUPPORTED_TYPE` | 不支持的文件类型 |
| 422 | `PARSE_ERROR` | 文件解析失败 |
| 422 | `INVALID_FILE` | 文件无效 |

## 架构设计

```
app/
├── main.py              # FastAPI 应用入口
├── auth.py              # API Key 鉴权
├── models.py            # Pydantic 数据模型
├── vision.py            # 视觉识别服务
├── routers/
│   └── convert.py       # 转换API路由
└── parsers/
    ├── base.py          # 解析器基类
    ├── registry.py      # 解析器注册表
    ├── txt.py           # 文本解析器
    ├── docx.py          # Word解析器
    ├── doc.py           # Word(旧版)解析器
    ├── pdf.py           # PDF解析器
    ├── pptx.py          # PowerPoint解析器
    ├── excel.py         # Excel解析器
    ├── csv.py           # CSV解析器
    ├── image.py         # 图片解析器
    └── code.py          # 代码文件解析器
```

## 性能优化

- 异步处理文件上传和解析
- 临时文件自动清理
- 内存优化的流式处理
- 支持大文件处理
- 智能编码检测

## 安全特性

- API Key 鉴权机制
- 文件类型白名单验证
- 临时文件安全清理
- 非 root 用户运行

## 监控和日志

- 结构化 JSON 日志
- 健康检查端点
- 处理时间统计
- 错误追踪和报告

## 扩展开发

### 添加新的文件解析器

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

## 许可证

本项目为 MedicNex 私有项目

## 贡献

欢迎提交 Issue 和 Pull Request！

---

> 开发者：Kris
> 最后更新：2025-06-08 