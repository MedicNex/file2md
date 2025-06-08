# MedicNex File2Markdown 服务

一个基于 FastAPI 的微服务，可以将各种文档格式（Word、PDF、PowerPoint、Excel、CSV、图片、代码文件等）转换为 Markdown 文本。

## 功能特性

- 🔐 **API Key 鉴权**：支持多个 API Key 管理
- 📄 **多格式支持**：支持 TXT、MD、DOCX、DOC、RTF、ODT、PDF、PPTX、XLS、XLSX、CSV、图片(包括SVG)、代码文件等格式
- 💻 **代码文件支持**：支持 85+ 种编程语言文件转换
- 🖼️ **智能图片识别**：集成 OpenAI Vision API 和 Tesseract OCR
- ⚡ **高性能异步**：基于 FastAPI 异步框架
- 🚀 **队列处理模式**：支持批量文档转换，限制最多5个并发任务
- 🎯 **并发图片处理**：文档中多张图片同时进行 OCR 和 AI 视觉识别，处理速度提升 2-10 倍
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
| Word文档 | `.docx` | DocxParser | `document` | 提取文本、表格和格式，**并发处理图片** |
| Word文档 | `.doc` | DocParser | `document` | 通过 mammoth 转换，**并发处理图片** |
| RTF文档 | `.rtf` | RtfParser | `document` | 支持RTF格式，优先使用Pandoc，备用striprtf |
| ODT文档 | `.odt` | OdtParser | `document` | OpenDocument文本，支持表格和列表 |
| PDF文档 | `.pdf` | PdfParser | `document` | 提取文本和图片，**并发处理图片** |
| PowerPoint | `.ppt`, `.pptx` | PptxParser | `slideshow` | 提取幻灯片文本内容（不使用视觉模型） |
| Excel表格 | `.xls`, `.xlsx` | ExcelParser | `sheet` | 转换为HTML表格格式和统计信息，**并发处理图片** |
| CSV数据 | `.csv` | CsvParser | `sheet` | 转换为HTML表格格式和数据分析 |
| 图片文件 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`, `.tga` | ImageParser | `image` | OCR和视觉识别 |
| SVG文件 | `.svg` | SvgParser | `svg` | 识别为代码格式，保持XML结构 |

### 代码文件（85+ 种语言）

| 语言类别 | 支持的扩展名 | 输出格式 |
|----------|-------------|----------|
| **主流编程语言** | `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rs`, `.php`, `.rb` | 对应语言代码块 |
| **前端技术** | `.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.jsx`, `.tsx`, `.svelte` | 对应语言代码块 |
| **脚本语言** | `.r`, `.R`, `.lua`, `.perl`, `.pl`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1` | 对应语言代码块 |
| **配置文件** | `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.cfg`, `.conf` | 对应语言代码块 |
| **其他** | `.sql`, `.dockerfile`, `.makefile`, `.cmake`, `.gradle`, `.proto`, `.graphql` | 对应语言代码块 |

**完整支持列表**：Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby, R, HTML, CSS, SCSS, Sass, Less, Vue, React(JSX), Svelte, JSON, YAML, XML, SQL, Shell scripts, PowerShell, Dockerfile, Makefile, 等85+种语言。

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

### 单文件转换（同步）

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
  "content": "```python\ndef hello_world():\n    print('Hello, World!')\n```",
  "duration_ms": 150
}
```

### 批量文件转换（异步队列）

使用队列模式批量提交多个文件，系统将控制并发数量最多为5个：

```bash
curl -X POST "https://file.medicnex.com/v1/convert-batch" \
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

### 查询任务状态

```bash
curl -X GET "https://file.medicnex.com/v1/task/{task_id}" \
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

### 查询队列状态

```bash
curl -X GET "https://file.medicnex.com/v1/queue/info" \
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
  "content": "```image\n# OCR:\n图表标题：销售数据分析\n\n# Description:\n这是一个显示月度销售趋势的柱状图...\n```",
  "duration_ms": 2500
}
```

## 完整功能示例

以下是一个包含代码块和图片的DOCX文档转换的完整示例，展示了系统的所有核心功能：

### 输入文件
上传一个包含Python代码和图片的Word文档 `test_doc_with_image_and_codeblock.docx`

### 转换结果
```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@test_doc_with_image_and_codeblock.docx"
```

**响应内容**：
```json
{
  "filename": "test_doc_with_image_and_codeblock.docx",
  "size": 15970,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "content": "```document\n<code class=\"language-python\">\ndef hello():\n\nprint(\"hello world\")\n\n</code>\n\n### 图片 1\n\n<img src=\"document_image_1.png\" alt=\"# OCR: HelloWorla!\n\nom! # Description: ### 1. 整体精准描述\n\n这张图片展示了一个简单的用户界面元素，背景为浅蓝色。图中包含一个白色边框的矩形区域，矩形内包含两行不同颜色的文本。整体布局简洁，内容和结构清晰易辨。\n\n### 2. 主要元素和结构\n\n- **背景：** 整个图片的背景为统一的浅蓝色，没有其他图案或装饰。\n- **矩形框：** 位于图片中央，是一个白色矩形框，具有黑色边框，背景颜色为纯白色，显得十分醒目。\n- **文本内容：**\n  - 第一行文本内容为\"Hello World!\"，字体为黑色，字体大小适中，位于矩形框顶部稍靠左的位置。\n  - 第二行文本内容为\" fascinated! \"，字体为红色，较第一行字体稍小，紧接在第一行的下方，同样是稍微偏左对齐。\n- **布局：** 两行文本在矩形框内垂直排列，具有一定的间距，并且都是左对齐，保持一定的对齐美感。\n\n### 3. 表格、图表及其他内容\n\n该图片中并未包含任何表格、图表等其他复杂元素，仅包含两段文字。内容上没有多余修饰，主要聚焦于两行文本信息的展示。\" />\n```",
  "duration_ms": 14208
}
```

### 功能说明

从上面的示例可以看出系统的核心功能：

1. **🔧 代码块转换**：
   - 原始Markdown代码块：````python
   - 转换为HTML标签：`<code class="language-python">`
   - 保持代码格式和语法高亮信息

2. **🖼️ 图片提取与OCR**：
   - 自动提取DOCX文档中的嵌入图片
   - 使用Tesseract OCR识别图片中的文字："HelloWorla! om!"
   - 生成唯一的图片文件名：`document_image_1.png`

3. **🤖 AI视觉识别**：
   - 使用视觉大模型（Qwen/Qwen2.5-VL-72B-Instruct）进行图片分析
   - 提供详细的图片描述，包括：
     - 整体布局和设计（浅蓝色背景，白色矩形框）
     - 文本内容分析（"Hello World!"黑色字体，红色"fascinated!"）
     - 结构和排版信息

4. **📝 HTML标签输出**：
   - 图片转换为：`<img src="图片名" alt="# OCR: ... # Description: ..." />`
   - alt属性包含完整的OCR结果和AI描述
   - 便于前端展示和无障碍访问

5. **⚡ 性能统计**：
   - 处理时间：14.2秒（包含AI视觉分析）
   - 文件大小：15,970字节
   - 输出内容：详细的结构化Markdown

### 获取支持的文件类型

```bash
curl -X GET "https://file.medicnex.com/v1/supported-types" \
  -H "Authorization: Bearer your-api-key"
```

## 队列功能测试

我们提供了一个完整的测试脚本来验证队列功能：

```bash
# 安装测试依赖
pip install aiohttp

# 设置环境变量（如果未设置）
export AGENT_API_KEYS="dev-test-key-123"

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &

# 运行测试
python test_queue.py

# 或运行简单演示
python demo_queue.py
```

测试脚本将验证以下功能：
- ✅ 单文件同步转换
- ✅ 批量文件异步提交
- ✅ 任务状态查询  
- ✅ 队列状态监控
- ✅ 并发限制（最多5个）
- ✅ 任务完成检测

### 队列功能特点

🚀 **新增队列模式的主要优势：**

1. **并发控制**：限制最多5个文档同时处理，避免系统过载
2. **异步处理**：客户端立即获得任务ID，无需等待处理完成
3. **状态跟踪**：实时查询每个任务的处理状态和进度
4. **队列管理**：自动排队处理，支持大批量文档转换
5. **资源优化**：合理利用系统资源，提升整体吞吐量

## 新的API端点总览

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
- **并发图片处理**：文档中多张图片同时进行 OCR 和 AI 视觉识别
  - 支持文件类型：PDF、DOC、DOCX、Excel
  - 性能提升：2-10倍处理速度（取决于图片数量和网络状况）
  - 技术实现：使用 `asyncio.gather()` 并发执行 OCR 和视觉模型调用
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

## 📚 更多资源

- **[转换示例文档](EXAMPLES.md)** - 详细的实际转换案例和功能演示
- **[前端集成指南](FRONTEND_API.md)** - 前端开发者接入文档

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

## 📈 最新更新

### v2.1.0 (2025-01-15)
- ✨ **新增**：并发图片处理功能
  - PDF、DOC、DOCX、Excel 文档中的多张图片现在可以并发处理
  - OCR 和 AI 视觉识别同时进行，大幅提升处理速度
  - 处理速度提升 2-10 倍（取决于图片数量）
- 🔧 **优化**：改进了异常处理和错误恢复机制
- 🐛 **修复**：解决了大型文档图片处理的内存问题

---

> 开发者：Kris  
> 最后更新：2025-01-15 