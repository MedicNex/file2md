# MedicNex File2Markdown 前端对接API文档

## 📖 概述

MedicNex File2Markdown 是一个文档转换 API 服务，支持将多种格式的文件（包括文档、图片、代码文件等）转换为统一的Markdown代码块格式。本文档为前端工程师提供完整的API接口说明。

## 🌐 基础信息

- **API版本**: v1
- **基础URL**: `https://your-domain/v1`
- **协议**: HTTPS
- **认证方式**: Bearer Token
- **请求格式**: multipart/form-data (文件上传)
- **响应格式**: JSON

## ✨ 统一输出格式

所有文件转换结果都采用统一的代码块格式输出，便于前端统一处理和渲染：

| 文件类型 | 输出格式 | 示例用途 |
|----------|----------|----------|
| 代码文件 (83+语言) | ```python, ```javascript 等 | 代码高亮显示 |
| 幻灯片文件 | ```slideshow | PPT文本内容展示（不使用视觉模型） |
| 图像文件 | ```image | OCR + 视觉描述 |
| 纯文本文件 | ```text | 文本内容展示 |
| 文档文件 | ```document | Word/PDF文档 |
| 表格文件 | ```sheet | Excel/CSV数据 |

### 🎨 新增功能特性

1. **文档内图片识别**: DOCX、PDF、DOC、Excel 等文档中的图片将被自动提取并进行 OCR 文字识别和 AI 视觉分析
2. **并发图片处理**: 多张图片同时进行 OCR 和 AI 视觉识别，处理速度提升 2-10 倍
3. **HTML 标签输出**: 文档中的代码块将转换为 HTML `<code>` 标签，图片将转换为 `<img>` 标签
4. **智能内容识别**: 结合 OCR 和 Vision AI 提供更准确的图片内容描述

#### 图片输出格式
```html
<img src="图片文件名.png" alt="# OCR: OCR识别的文字内容 # Visual_Features: AI视觉分析描述" />
```

#### 代码块输出格式
```html
<code class="language-python">
def hello():
    print("hello world")
</code>
```

## 🔐 认证机制

所有API请求（除健康检查外）都需要在请求头中携带API密钥：

```http
Authorization: Bearer your-api-key
```

### 获取API密钥
请联系系统管理员获取有效的API密钥。

## 🚀 队列处理模式

### 新增功能
系统现在支持两种处理模式：
1. **单文件同步转换**：适合实时处理小文件
2. **批量队列转换**：支持大批量文档处理，限制最多5个并发任务

### 队列优势
- ⚡ **并发控制**：自动限制最多5个文档同时处理，避免系统过载
- 🔄 **异步处理**：客户端立即获得任务ID，无需等待处理完成
- 📊 **状态跟踪**：实时查询每个任务的处理状态和进度
- 🗂️ **队列管理**：自动排队处理，支持大批量文档转换
- 🎯 **图片并发处理**：文档内多张图片同时处理，大幅提升转换速度

## 📊 API接口列表

### 1. 健康检查

**接口地址**: `GET /v1/health`

**功能说明**: 检查服务运行状态（含队列状态）

**请求参数**: 无

**响应示例**:
```json
{
  "status": "UP",
  "service": "file2markdown",
  "version": "1.0.0",
  "components": {
    "api": {"status": "UP"},
    "parsers": {"status": "UP"},
    "ocr": {"status": "UP"},
    "queue": {
      "status": "UP",
      "info": {
        "max_concurrent": 5,
        "queue_size": 2,
        "active_tasks": 3,
        "total_tasks": 10,
        "pending_count": 2,
        "processing_count": 3,
        "completed_count": 4,
        "failed_count": 1
      }
    }
  }
}
```

### 2. 获取支持的文件类型

**接口地址**: `GET /v1/supported-types`

**功能说明**: 获取服务支持的文件扩展名列表

**请求头**:
```http
Authorization: Bearer your-api-key
```

**响应示例**:
```json
{
  "supported_extensions": [
    ".txt", ".md", ".markdown", ".text",
    ".docx", ".doc", ".rtf", ".odt",
    ".pdf",
    ".pptx", ".ppt",
    ".csv",
    ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp", ".ico", ".tga",
    ".svg",
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs",
    ".html", ".css", ".json", ".yaml", ".xml", ".sql", ".sh"
  ],
  "total_count": 106
}
```

**支持的文件类型**:
- **文档类**: TXT, MD, DOCX, DOC, RTF, ODT, PDF
- **演示文稿**: PPTX, PPT  
- **表格数据**: XLSX, XLS, CSV
- **图像文件**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP, ICO, TGA
- **SVG文件**: SVG（识别为代码格式）
- **代码文件**: 85+种编程语言（Python, JavaScript, Java, C++, Go, Rust等）

### 3. 单文件转换（同步）

**接口地址**: `POST /v1/convert`

**功能说明**: 将上传的文件转换为Markdown代码块格式（同步处理）

**请求头**:
```http
Authorization: Bearer your-api-key
Content-Type: multipart/form-data
```

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 要转换的文件 |

**文件限制**:
- 最大文件大小: 100MB
- 支持的文件类型: 见"支持的文件类型"接口

**响应示例（Python代码文件）**:
```json
{
  "filename": "example.py",
  "size": 1024,
  "content_type": "text/x-python",
  "content": "```python\ndef hello_world():\n    print('Hello, World!')\n    return 'success'\n```",
  "duration_ms": 150
}
```

**响应示例（图片文件）**:
```json
{
  "filename": "chart.png",
  "size": 204800,
  "content_type": "image/png",
  "content": "```image\n# OCR:\n图表标题：销售数据分析\n\n# Visual_Features:\n这是一个显示月度销售趋势的柱状图，包含了12个月的销售数据...\n```",
  "duration_ms": 2500
}
```

**响应示例（Word文档含图片和代码块）**:
```json
{
  "filename": "document.docx",
  "size": 1280345,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "content": "```document\n# 文档标题\n\n这是文档内容...\n\n<code class=\"language-python\">\ndef hello():\n    print(\"hello world\")\n</code>\n\n### 图片 1\n\n<img src=\"document_image_1.png\" alt=\"# OCR: 图片中的文字内容 # Visual_Features: 图片的详细描述...\" />\n\n## 章节2\n\n更多内容...\n```",
  "duration_ms": 420
}
```

## ⚡ 性能优化特性

### 并发图片处理

系统现在支持对文档中的多张图片进行并发处理，显著提升了处理速度：

**优化前（串行处理）**：
```
图片1: OCR → Vision API → 完成 (3秒)
图片2: OCR → Vision API → 完成 (3秒)
图片3: OCR → Vision API → 完成 (3秒)
总计：9秒
```

**优化后（并发处理）**：
```
图片1、2、3: 同时进行 OCR 和 Vision API 调用
总计：3-4秒（提升 2-3倍）
```

**支持的文件类型**：
- ✅ PDF文档：每页图片并发处理
- ✅ Word文档 (.docx, .doc)：所有图片并发处理  
- ✅ Excel表格 (.xlsx)：所有工作表图片并发处理

**性能提升数据**：
- 包含2-3张图片的文档：**2-3倍** 速度提升
- 包含5-10张图片的文档：**5-8倍** 速度提升
- 大型文档（10+张图片）：**8-10倍** 速度提升

### 4. 图片OCR识别（仅OCR）

**接口地址**: `POST /v1/ocr`

**功能说明**: 对上传的图片进行OCR文字识别（仅使用OCR技术，不使用Vision API）

**请求头**:
```http
Authorization: Bearer your-api-key
Content-Type: multipart/form-data
```

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | File | 是 | 要识别的图片文件 |

**支持的文件类型**:
- 图片格式: JPG, JPEG, PNG, BMP, TIFF, TIF, GIF, WEBP

**文件限制**:
- 最大文件大小: 100MB
- 仅支持图片格式文件

**响应示例**:
```json
{
  "filename": "document.png",
  "size": 204800,
  "content_type": "image/png",
  "ocr_text": "这是从图片中识别出的文字内容\n包含多行文本\n支持中文和英文识别",
  "duration_ms": 1200,
  "from_cache": false
}
```

**响应字段说明**:
- `filename`: 原始文件名
- `size`: 文件大小（字节）
- `content_type`: 文件MIME类型
- `ocr_text`: OCR识别出的文字内容
- `duration_ms`: 处理耗时（毫秒）
- `from_cache`: 是否来自缓存结果

**错误响应示例**:
```json
{
  "code": "UNSUPPORTED_TYPE",
  "message": "不支持的文件类型: .pdf，仅支持图片格式: .jpg, .jpeg, .png, .bmp, .tiff, .tif, .gif, .webp"
}
```

### 5. 批量文件转换（异步队列）

**接口地址**: `POST /v1/convert-batch`

**功能说明**: 批量提交多个文件到转换队列（异步处理，最多5个并发）

**请求头**:
```http
Authorization: Bearer your-api-key
Content-Type: multipart/form-data
```

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| files | File[] | 是 | 要转换的文件列表 |

**响应示例**:
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
    }
  ],
  "total_count": 2,
  "success_count": 2,
  "failed_count": 0
}
```

### 6. 查询任务状态

**接口地址**: `GET /v1/task/{task_id}`

**功能说明**: 获取指定任务的状态和结果

**请求头**:
```http
Authorization: Bearer your-api-key
```

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | String | 是 | 任务ID |

**响应示例（处理中）**:
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "document1.docx",
  "file_size": 15970,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "status": "processing",
  "created_at": "2024-01-20T10:30:00",
  "started_at": "2024-01-20T10:30:05",
  "completed_at": null,
  "duration_ms": null,
  "result": null,
  "error": null
}
```

**响应示例（已完成）**:
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

**任务状态说明**:
- `pending`: 等待处理
- `processing`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

### 7. 查询队列状态

**接口地址**: `GET /v1/queue/info`

**功能说明**: 获取转换队列的状态信息

**请求头**:
```http
Authorization: Bearer your-api-key
```

**响应示例**:
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

**字段说明**:
- `max_concurrent`: 最大并发处理数量
- `queue_size`: 当前队列中等待的任务数
- `active_tasks`: 正在处理的任务数
- `total_tasks`: 总任务数（包括所有状态）
- `pending_count`: 等待处理的任务数
- `processing_count`: 正在处理的任务数
- `completed_count`: 已完成的任务数
- `failed_count`: 失败的任务数

### 8. 清理过期任务

**接口地址**: `POST /v1/queue/cleanup`

**功能说明**: 清理超过指定时间的已完成任务

**请求头**:
```http
Authorization: Bearer your-api-key
```

**请求参数（可选）**:
| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| max_age_hours | Integer | 24 | 任务保留时间（小时） |

**响应示例**:
```json
{
  "message": "成功清理 5 个过期任务",
  "cleaned_count": 5,
  "max_age_hours": 24
}
```

## 🚀 实战转换示例

以下是一个真实的转换示例，演示系统处理包含代码和图片的复杂文档的能力：

### 输入
- **文件**: `test_doc_with_image_and_codeblock.docx` (15,970 bytes)
- **内容**: Python代码块 + 界面截图

### API调用
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/v1/convert', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key'
  },
  body: formData
});

const result = await response.json();
```

### 实际输出
```json
{
  "filename": "test_doc_with_image_and_codeblock.docx",
  "size": 15970,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "content": "```document\n<code class=\"language-python\">\ndef hello():\n\nprint(\"hello world\")\n\n</code>\n\n### 图片 1\n\n<img src=\"document_image_1.png\" alt=\"# OCR: HelloWorla!\n\nom! # Visual_Features: ### 1. 整体精准描述\n\n这张图片展示了一个简单的用户界面元素，背景为浅蓝色。图中包含一个白色边框的矩形区域，矩形内包含两行不同颜色的文本。整体布局简洁，内容和结构清晰易辨。\n\n### 2. 主要元素和结构\n\n- **背景：** 整个图片的背景为统一的浅蓝色，没有其他图案或装饰。\n- **矩形框：** 位于图片中央，是一个白色矩形框，具有黑色边框，背景颜色为纯白色，显得十分醒目。\n- **文本内容：**\n  - 第一行文本内容为\\\"Hello World!\\\"，字体为黑色，字体大小适中，位于矩形框顶部稍靠左的位置。\n  - 第二行文本内容为\\\" fascinated! \\\"，字体为红色，较第一行字体稍小，紧接在第一行的下方，同样是稍微偏左对齐。\n- **布局：** 两行文本在矩形框内垂直排列，具有一定的间距，并且都是左对齐，保持一定的对齐美感。\n\n### 3. 表格、图表及其他内容\n\n该图片中并未包含任何表格、图表等其他复杂元素，仅包含两段文字。内容上没有多余修饰，主要聚焦于两行文本信息的展示。\" />\n```",
  "duration_ms": 14208
}
```

### 前端处理建议

1. **代码高亮显示**：
   ```javascript
   // 提取并渲染代码块
   const codeBlocks = content.match(/<code class="language-(\w+)">(.*?)<\/code>/gs);
   codeBlocks?.forEach(block => {
     // 使用 Prism.js 或 highlight.js 进行语法高亮
     highlightCode(block);
   });
   ```

2. **图片展示**：
   ```javascript
   // 提取图片信息
   const images = content.match(/<img src="([^"]*)" alt="([^"]*)" \/>/g);
   images?.forEach(img => {
     const [, src, alt] = img.match(/src="([^"]*)" alt="([^"]*)"/);
     // 显示图片和OCR/AI分析结果
     displayImageWithAnalysis(src, alt);
   });
   ```

3. **性能监控**：
   ```javascript
   // 监控转换性能
   console.log(`文档转换完成: ${result.filename}`);
   console.log(`处理时间: ${result.duration_ms}ms`);
   console.log(`内容长度: ${result.content.length} 字符`);
   ```

## 🎯 JavaScript SDK 示例

### 基础配置

```javascript
class MedicNexAPI {
  constructor(baseURL, apiKey) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  // 通用请求方法
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      ...options.headers
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || `API Error: ${response.status}`);
    }

    return response.json();
  }

  // 健康检查
  async healthCheck() {
    return fetch(`${this.baseURL}/health`).then(res => res.json());
  }

  // 获取支持的文件类型
  async getSupportedTypes() {
    return this.request('/supported-types');
  }

  // 单文件转换（同步）
  async convertFile(file, onProgress = null) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/convert`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || 'Upload failed');
    }

    return response.json();
  }

  // 批量文件转换（异步队列）
  async convertBatchFiles(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${this.baseURL}/convert-batch`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || 'Batch upload failed');
    }

    return response.json();
  }

  // 查询任务状态
  async getTaskStatus(taskId) {
    return this.request(`/task/${taskId}`);
  }

  // 查询队列状态
  async getQueueInfo() {
    return this.request('/queue/info');
  }

  // 清理过期任务
  async cleanupOldTasks(maxAgeHours = 24) {
    const response = await fetch(`${this.baseURL}/queue/cleanup?max_age_hours=${maxAgeHours}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail?.message || 'Cleanup failed');
    }

    return response.json();
  }

  // 等待任务完成
  async waitForTaskCompletion(taskId, maxWaitMs = 60000, pollIntervalMs = 2000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < maxWaitMs) {
      const status = await this.getTaskStatus(taskId);
      
      if (status.status === 'completed') {
        return status;
      } else if (status.status === 'failed') {
        throw new Error(`Task failed: ${status.error}`);
      }
      
      // 等待下次轮询
      await new Promise(resolve => setTimeout(resolve, pollIntervalMs));
    }
    
    throw new Error('Task completion timeout');
  }

  // 检查文件类型是否支持
  async isFileSupported(filename) {
    const types = await this.getSupportedTypes();
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return types.supported_extensions.includes(ext);
  }
}

// 使用示例
const api = new MedicNexAPI('https://your-domain/v1', 'your-api-key');
```

### 文件上传组件示例 (React)

```jsx
import React, { useState, useCallback } from 'react';

const FileConverter = () => {
  const [files, setFiles] = useState([]);
  const [converting, setConverting] = useState(false);
  const [results, setResults] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('single'); // 'single' or 'batch'

  const api = new MedicNexAPI('https://your-domain/v1', 'your-api-key');

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    if (selectedFiles.length === 0) return;

    // 检查文件类型
    const validFiles = [];
    for (const file of selectedFiles) {
      const isSupported = await api.isFileSupported(file.name);
      if (isSupported) {
        validFiles.push(file);
      } else {
        console.warn(`不支持的文件类型: ${file.name}`);
      }
    }

    if (validFiles.length === 0) {
      setError('没有支持的文件类型');
      return;
    }

    setFiles(validFiles);
    setResults([]);
    setTasks([]);
    setError(null);
  };

  const handleConvert = async () => {
    if (files.length === 0) return;

    setConverting(true);
    setError(null);

    try {
      if (mode === 'single' && files.length === 1) {
        // 单文件同步转换
        const response = await api.convertFile(files[0]);
        setResults([response]);
      } else {
        // 批量异步转换
        const batchResponse = await api.convertBatchFiles(files);
        setTasks(batchResponse.submitted_tasks);
        
        // 开始轮询任务状态
        pollTaskStatus(batchResponse.submitted_tasks);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      if (mode === 'single') {
        setConverting(false);
      }
    }
  };

  const pollTaskStatus = async (submittedTasks) => {
    const completedResults = [];
    const taskIds = submittedTasks.map(task => task.task_id).filter(id => id);
    
    try {
      for (const taskId of taskIds) {
        try {
          const result = await api.waitForTaskCompletion(taskId);
          completedResults.push(result);
        } catch (err) {
          console.error(`Task ${taskId} failed:`, err.message);
          completedResults.push({
            task_id: taskId,
            status: 'failed',
            error: err.message
          });
        }
      }
      
      setResults(completedResults);
    } catch (err) {
      setError(err.message);
    } finally {
      setConverting(false);
    }
  };

  // 解析代码块类型
  const parseCodeBlock = (content) => {
    const match = content.match(/^```(\w+)\n([\s\S]*?)```$/);
    if (match) {
      return {
        language: match[1],
        content: match[2]
      };
    }
    return { language: 'text', content: content };
  };

  const renderResults = () => {
    if (results.length === 0) return null;

    return (
      <div className="results">
        <h3>转换结果 ({results.length} 个文件)</h3>
        {results.map((result, index) => {
          if (result.status === 'failed') {
            return (
              <div key={index} className="result error">
                <h4>{result.filename || `任务 ${index + 1}`}</h4>
                <p className="error-msg">转换失败: {result.error}</p>
              </div>
            );
          }

          const { language, content } = parseCodeBlock(result.result || result.content);
          
          return (
            <div key={index} className="result">
              <h4>{result.filename}</h4>
              <div className="file-info">
                <p>大小: {(result.file_size || result.size || 0 / 1024).toFixed(1)} KB</p>
                <p>处理时间: {result.duration_ms} ms</p>
                <p>状态: {result.status || 'completed'}</p>
              </div>
              
              {/* 根据不同类型渲染内容 */}
              {language === 'image' ? (
                <div className="image-result">
                  <pre>{content}</pre>
                </div>
              ) : language !== 'text' ? (
                <pre className={`language-${language}`}>
                  <code>{content}</code>
                </pre>
              ) : (
                <div className="text-result">
                  <pre>{content}</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  const renderTasks = () => {
    if (tasks.length === 0) return null;

    return (
      <div className="tasks">
        <h3>任务状态</h3>
        {tasks.map((task, index) => (
          <div key={index} className="task">
            <p><strong>{task.filename}</strong></p>
            <p>状态: {task.status}</p>
            <p>任务ID: {task.task_id}</p>
            {task.message && <p>{task.message}</p>}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="file-converter">
      <div className="mode-selector">
        <label>
          <input 
            type="radio" 
            value="single" 
            checked={mode === 'single'} 
            onChange={(e) => setMode(e.target.value)}
          />
          单文件同步转换
        </label>
        <label>
          <input 
            type="radio" 
            value="batch" 
            checked={mode === 'batch'} 
            onChange={(e) => setMode(e.target.value)}
          />
          批量异步转换
        </label>
      </div>

      <div className="upload-area">
        <input 
          type="file" 
          multiple={mode === 'batch'}
          onChange={handleFileSelect}
          disabled={converting}
        />
        
        {files.length > 0 && (
          <div className="file-info">
            <p>已选择: {files.length} 个文件</p>
            <ul>
              {files.map((file, index) => (
                <li key={index}>{file.name}</li>
              ))}
            </ul>
            <button 
              onClick={handleConvert} 
              disabled={converting}
            >
              {converting ? 
                (mode === 'single' ? '转换中...' : '处理中...') : 
                (mode === 'single' ? '开始转换' : '批量提交')
              }
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error">
          错误: {error}
        </div>
      )}

      {renderTasks()}
      {renderResults()}
    </div>
  );
};

export default FileConverter;
```

## 🎨 CSS样式参考

```css
.file-converter {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.mode-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.mode-selector label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
}

.mode-selector input[type="radio"] {
  margin: 0;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
}

.upload-area.dragging {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.file-info ul {
  text-align: left;
  max-height: 150px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin: 10px 0;
}

.convert-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

.convert-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
}

.tasks {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.tasks h3 {
  margin-top: 0;
  color: #856404;
}

.task {
  background-color: #fff;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
  margin: 10px 0;
}

.task p {
  margin: 5px 0;
}

.results {
  margin: 20px 0;
}

.result {
  background-color: #d4edda;
  color: #155724;
  padding: 20px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid #c3e6cb;
}

.result.error {
  background-color: #f8d7da;
  color: #721c24;
  border-color: #f5c6cb;
}

.result h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.file-info {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.file-info p {
  margin: 5px 0;
  font-size: 14px;
}

.markdown-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
  border: 1px solid #e9ecef;
}

.markdown-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
}

.image-result, .text-result {
  margin-top: 10px;
}

.language-python, .language-javascript, .language-java {
  background-color: #2d3748;
  color: #e2e8f0;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* 队列状态指示器 */
.queue-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 8px;
  padding: 15px;
  margin: 15px 0;
}

.queue-status .status-item {
  text-align: center;
  flex: 1;
}

.queue-status .status-item .label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
}

.queue-status .status-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #1976d2;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mode-selector {
    flex-direction: column;
    gap: 10px;
  }
  
  .queue-status {
    flex-direction: column;
    gap: 10px;
  }
  
  .queue-status .status-item {
    display: flex;
    justify-content: space-between;
    width: 100%;
  }
}
```

## ❌ 错误处理

### 错误响应格式

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "detail": "详细错误信息"
  }
}
```

### 常见错误码

| HTTP状态码 | 错误码 | 说明 | 解决方案 |
|------------|--------|------|----------|
| 401 | INVALID_API_KEY | API密钥无效 | 检查API密钥是否正确 |
| 404 | TASK_NOT_FOUND | 任务未找到 | 检查任务ID是否正确 |
| 415 | UNSUPPORTED_TYPE | 不支持的文件类型 | 检查文件扩展名是否受支持 |
| 422 | INVALID_FILE | 文件无效 | 检查文件是否损坏或为空 |
| 422 | PARSE_ERROR | 解析失败 | 文件格式可能有问题 |
| 413 | FILE_TOO_LARGE | 文件过大 | 减小文件大小或分片上传 |

### 错误处理示例

```javascript
async function convertFileWithErrorHandling(file) {
  try {
    const result = await api.convertFile(file);
    return { success: true, data: result };
  } catch (error) {
    let errorMessage = '转换失败';
    
    if (error.message.includes('401')) {
      errorMessage = 'API密钥无效，请检查配置';
    } else if (error.message.includes('415')) {
      errorMessage = '不支持的文件类型';
    } else if (error.message.includes('413')) {
      errorMessage = '文件太大，请选择小于100MB的文件';
    }
    
    return { success: false, error: errorMessage };
  }
}
```

## 📱 文件类型特殊说明

### 图片文件处理
对于图片文件（.png, .jpg, .jpeg, .gif, .bmp, .tiff, .webp），API会返回：
```markdown
# OCR

[提取的文字内容]

# Description

[AI视觉模型的详细描述]
```

### 表格文件处理
CSV和Excel文件会转换为HTML表格格式，包含：
- 数据统计信息
- 完整的HTML表格数据
- 数值列的统计分析
- 统一的表格样式和格式

### 文档文件处理
Word和PDF文件会保持原有的：
- 标题层级结构
- 列表格式
- 表格布局
- 基本文本格式

## 🔄 批量处理示例

### 使用队列模式处理大批量文件

```javascript
class BatchProcessor {
  constructor(api) {
    this.api = api;
  }

  // 批量提交并等待完成
  async processFiles(files, onProgress) {
    try {
      // 1. 批量提交到队列
      console.log(`批量提交 ${files.length} 个文件...`);
      const batchResponse = await this.api.convertBatchFiles(files);
      
      const successTasks = batchResponse.submitted_tasks.filter(task => task.task_id);
      console.log(`成功提交 ${successTasks.length} 个任务`);
      
      // 2. 监控队列状态
      if (onProgress) {
        this.monitorQueue(onProgress);
      }
      
      // 3. 等待所有任务完成
      const results = [];
      for (let i = 0; i < successTasks.length; i++) {
        const task = successTasks[i];
        try {
          const result = await this.api.waitForTaskCompletion(task.task_id);
          results.push(result);
          
          if (onProgress) {
            onProgress(results.length, successTasks.length, 'completed');
          }
        } catch (error) {
          console.error(`任务 ${task.task_id} 失败:`, error.message);
          results.push({
            task_id: task.task_id,
            filename: task.filename,
            status: 'failed',
            error: error.message
          });
          
          if (onProgress) {
            onProgress(results.length, successTasks.length, 'failed');
          }
        }
      }
      
      return results;
      
    } catch (error) {
      console.error('批量处理失败:', error);
      throw error;
    }
  }

  // 监控队列状态
  async monitorQueue(onQueueUpdate) {
    const interval = setInterval(async () => {
      try {
        const queueInfo = await this.api.getQueueInfo();
        onQueueUpdate(null, null, 'queue_status', queueInfo);
        
        // 如果没有处理中的任务，停止监控
        if (queueInfo.processing_count === 0 && queueInfo.pending_count === 0) {
          clearInterval(interval);
        }
      } catch (error) {
        console.error('监控队列状态失败:', error);
        clearInterval(interval);
      }
    }, 3000); // 每3秒检查一次
  }

  // 手动检查特定任务状态
  async checkTaskStatus(taskId) {
    return await this.api.getTaskStatus(taskId);
  }

  // 清理过期任务
  async cleanupOldTasks(maxAgeHours = 24) {
    return await this.api.cleanupOldTasks(maxAgeHours);
  }
}

// 使用示例
const processor = new BatchProcessor(api);

// 批量处理文件
const results = await processor.processFiles(files, (completed, total, status, queueInfo) => {
  if (status === 'queue_status') {
    console.log('队列状态:', queueInfo);
    console.log(`队列中: ${queueInfo.queue_size}, 处理中: ${queueInfo.processing_count}`);
  } else {
    console.log(`进度: ${completed}/${total} (${status})`);
  }
});

console.log('所有文件处理完成:', results);

// 手动查询队列状态
const queueStatus = await api.getQueueInfo();
console.log('当前队列状态:', queueStatus);
```

### 高级用法：实时状态监控

```javascript
class QueueMonitor {
  constructor(api) {
    this.api = api;
    this.listeners = [];
  }

  // 添加状态监听器
  addListener(callback) {
    this.listeners.push(callback);
  }

  // 开始监控
  startMonitoring() {
    this.intervalId = setInterval(async () => {
      try {
        const queueInfo = await this.api.getQueueInfo();
        this.notifyListeners('queue_update', queueInfo);
      } catch (error) {
        this.notifyListeners('error', error);
      }
    }, 2000);
  }

  // 停止监控
  stopMonitoring() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  // 通知所有监听器
  notifyListeners(type, data) {
    this.listeners.forEach(callback => {
      try {
        callback(type, data);
      } catch (error) {
        console.error('监听器回调错误:', error);
      }
    });
  }
}

// 使用示例
const monitor = new QueueMonitor(api);

monitor.addListener((type, data) => {
  if (type === 'queue_update') {
    console.log(`队列状态: 队列${data.queue_size} | 活跃${data.active_tasks} | 完成${data.completed_count}`);
    
    // 更新UI显示
    updateQueueStatusUI(data);
  } else if (type === 'error') {
    console.error('监控错误:', data);
  }
});

monitor.startMonitoring();

// 在适当时候停止监控
// monitor.stopMonitoring();
```

## 📋 最佳实践

### 单文件 vs 批量处理选择建议

**单文件同步转换**适用于：
- 实时预览需求
- 小文件（< 5MB）
- 用户交互要求即时反馈
- 简单的文档类型

**批量队列转换**适用于：
- 大量文件批量处理
- 大文件（> 5MB）或复杂文档
- 后台处理场景
- 需要处理进度跟踪

### 开发建议

1. **文件验证**：上传前检查文件类型和大小
2. **错误处理**：提供友好的错误提示信息
3. **进度监控**：
   - 单文件：显示上传和处理进度
   - 批量：显示队列状态和任务进度
4. **状态管理**：
   - 合理使用任务ID进行状态跟踪
   - 定期清理已完成的任务
5. **用户体验**：
   - 提供模式切换选项
   - 显示预估处理时间
   - 支持任务取消（如需要）
6. **性能优化**：
   - 避免频繁轮询队列状态
   - 合理设置轮询间隔（建议2-5秒）
   - 及时清理过期任务
7. **安全考虑**：在客户端验证文件类型，但不依赖它作为唯一安全措施

## 🔗 相关链接

- **API文档**: `https://your-domain/docs`
- **在线测试**: `https://your-domain/redoc`
- **健康检查**: `https://your-domain/v1/health`

## 📞 技术支持

如有技术问题，请提供：
- API请求详情（URL、Headers、Body）
- 错误响应内容
- 文件类型和大小信息
- 浏览器控制台错误日志

---

**祝您开发愉快！如有疑问，随时联系技术支持团队。** 