# MedicNex File2Markdown

MedicNex File2Markdown 是一个基于 FastAPI 的微服务，可以将**123种文件格式**（Word、PDF、PowerPoint、Excel、CSV、图片、Apple iWork套件、82种编程语言等）转换为统一的 Markdown 代码块格式。

## 功能特性

- 🔐 **API Key 鉴权**：支持多个 API Key 管理
- 📄 **全面格式支持**：支持 **123种文件格式**，包含 16种解析器类型
- 💻 **代码文件支持**：支持 **82 种编程语言**文件转换，涵盖主流、函数式、脚本、配置等语言
- 🖼️ **智能图片识别**：集成 Vision API 和 Tesseract OCR，支持 SVG 转 PNG 识别
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
| 音频文件 | `````audio` | 语音转录 + 时间轴 |
| 视频文件 | `````video` | SRT字幕 + 音频转录 |
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
| Keynote演示文稿 | `.key` | KeynoteParser | `slideshow` | Apple Keynote演示文稿，提取元数据和结构信息 |
| Pages文档 | `.pages` | PagesParser | `document` | Apple Pages文字处理文档，提取元数据和结构信息 |
| Numbers表格 | `.numbers` | NumbersParser | `sheet` | Apple Numbers电子表格，支持表格数据提取 |
| PowerPoint演示文稿 | `.ppt`, `.pptx` | PptxParser | `slideshow` | 提取幻灯片文本内容（不使用视觉模型） |
| Excel表格 | `.xls`, `.xlsx` | ExcelParser | `sheet` | 转换为HTML表格格式和统计信息，**并发处理图片** |
| CSV数据 | `.csv` | CsvParser | `sheet` | 转换为HTML表格格式和数据分析 |
| 图片文件 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`, `.tga` | ImageParser | `image` | OCR和视觉识别 |
| SVG文件 | `.svg` | SvgParser | `svg` | 同时识别代码结构和视觉特征，**转换为PNG进行OCR和AI视觉分析**（需要ImageMagick或Cairo库） |
| 音频文件 | `.wav`, `.mp3`, `.mp4`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac` | AudioParser | `audio` | **智能语音分析和ASR转换**，基于RMS能量分析自动分割，并发语音识别，自适应阈值检测 |
| 视频文件 | `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp` | AudioParser | `video` | **视频音频提取和字幕生成**，自动提取音频轨道进行ASR转换，生成SRT格式字幕文件 |

### 代码文件（82 种语言）

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
API_KEY=your-api-key-1,your-api-key-2
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

2. 安装系统依赖：

**Ubuntu/Debian：**
```bash
# 基础OCR支持
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng

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

### 音频处理示例

**输入文件**：上传一个包含多段对话的音频文件 `meeting.wav`

```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@meeting.wav"
```

**输出格式** (`audio`块)：
```json
{
  "filename": "meeting.wav",
  "size": 2048000,
  "content_type": "audio/wav",
  "content": "```audio\n# 音频信息\n文件名: meeting.wav\n时长: 00:02:45\n采样率: 16000 Hz\n声道: 单声道\n格式: WAV\n\n# 语音转录\n## 段落 1 (00:00:00 - 00:00:15)\n大家好，欢迎参加今天的产品讨论会议。\n**置信度**: 89%\n\n## 段落 2 (00:00:16 - 00:00:32)\n首先我们来看一下本季度的销售数据分析。\n**置信度**: 92%\n\n## 段落 3 (00:00:33 - 00:00:48)\n从图表可以看出，我们的产品在移动端表现非常优秀。\n**置信度**: 87%\n\n# 处理统计\n- 总段落数: 11\n- 平均段落时长: 15.2秒\n- 整体置信度: 89%\n- 处理时间: 23.4秒\n- 使用的ASR模型: whisper-1\n```",
  "duration_ms": 23400
}
```

### 视频处理示例

**输入文件**：上传一个教学视频 `tutorial.mp4`

```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@tutorial.mp4"
```

**输出格式** (`video`块)：
```json
{
  "filename": "tutorial.mp4", 
  "size": 15728640,
  "content_type": "video/mp4",
  "content": "```video\n# 视频信息\n文件名: tutorial.mp4\n视频时长: 00:05:23\n音频轨道: 已检测\n字幕语言: 中文\n\n# 字幕内容\n1\n00:00:00,000 --> 00:00:12,500\n欢迎来到Python编程入门教程，今天我们将学习基础语法。\n\n2\n00:00:12,500 --> 00:00:28,750\n首先我们来看变量的定义和使用方法。\n\n3\n00:00:28,750 --> 00:00:45,100\n在Python中，你可以使用等号来给变量赋值。\n\n4\n00:00:45,100 --> 00:01:02,300\n例如，name等于引号Hello World引号。\n\n# 处理统计\n- 总字幕条目: 26\n- 平均字幕时长: 12.4秒\n- 整体质量: 良好\n- 处理时间: 45.7秒\n- 提取音频格式: WAV 16kHz\n```",
  "duration_ms": 45700
}
```

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
  "content": "```document\n<code class=\"language-python\">\ndef hello():\n\nprint(\"hello world\")\n\n</code>\n\n### 图片 1\n\n<img src=\"document_image_1.png\" alt=\"# OCR: HelloWorla!\n\nom! # Visual_Features: ### 1. 整体精准描述\n\n这张图片展示了一个简单的用户界面元素，背景为浅蓝色。图中包含一个白色边框的矩形区域，矩形内包含两行不同颜色的文本。整体布局简洁，内容和结构清晰易辨。\n\n### 2. 主要元素和结构\n\n- **背景：** 整个图片的背景为统一的浅蓝色，没有其他图案或装饰。\n- **矩形框：** 位于图片中央，是一个白色矩形框，具有黑色边框，背景颜色为纯白色，显得十分醒目。\n- **文本内容：**\n  - 第一行文本内容为\"Hello World!\"，字体为黑色，字体大小适中，位于矩形框顶部稍靠左的位置。\n  - 第二行文本内容为\" fascinated! \"，字体为红色，较第一行字体稍小，紧接在第一行的下方，同样是稍微偏左对齐。\n- **布局：** 两行文本在矩形框内垂直排列，具有一定的间距，并且都是左对齐，保持一定的对齐美感。\n\n### 3. 表格、图表及其他内容\n\n该图片中并未包含任何表格、图表等其他复杂元素，仅包含两段文字。内容上没有多余修饰，主要聚焦于两行文本信息的展示。\" />\n```",
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
   - 图片转换为：`<img src="图片名" alt="# OCR: ... # Visual_Features: ..." />`
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
export API_KEY="dev-test-key-123"

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
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
| `API_KEY` | API密钥列表（逗号分隔） | `dev-test-key-123` | 是 |
| `VISION_API_KEY` | 视觉API密钥 | - | 否 |
| `VISION_API_BASE` | 视觉API基础URL | `https://api.openai.com/v1` | 否 |
| `VISION_MODEL` | 视觉识别模型名称 | `gpt-4o-mini` | 否 |
| `ASR_API_KEY` | ASR语音识别API密钥 | - | 音频功能必需 |
| `ASR_API_BASE` | ASR API基础URL | `https://api.openai.com/v1` | 否 |
| `ASR_MODEL` | ASR模型名称 | `whisper-1` | 否 |
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
    ├── audio.py         # 音频/视频解析器（智能分块+ASR）
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

- **[支持的文件格式](SUPPORTED_FORMATS.md)** - 详细的109种支持格式列表和功能说明
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

本项目为 MedicNex 私有项目。

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📈 最新更新

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

> 开发者：Kris  