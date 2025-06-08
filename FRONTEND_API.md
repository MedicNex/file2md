# MedicNex File2Markdown 前端对接API文档

## 📖 概述

MedicNex File2Markdown 是一个文档转换微服务，支持将多种格式的文件（包括文档、图片、代码文件等）转换为统一的Markdown代码块格式。本文档为前端工程师提供完整的API接口说明。

## 🌐 基础信息

- **API版本**: v1
- **基础URL**: `https://file.medicnex.com/v1`
- **协议**: HTTPS (推荐) / HTTP
- **认证方式**: Bearer Token
- **请求格式**: multipart/form-data (文件上传)
- **响应格式**: JSON

## ✨ 统一输出格式

所有文件转换结果都采用统一的代码块格式输出，便于前端统一处理和渲染：

| 文件类型 | 输出格式 | 示例用途 |
|----------|----------|----------|
| 代码文件 (83+语言) | ```python, ```javascript 等 | 代码高亮显示 |
| 幻灯片文件 | ```slideshow | PPT内容展示 |
| 图像文件 | ```image | OCR + 视觉描述 |
| 纯文本文件 | ```text | 文本内容展示 |
| 文档文件 | ```document | Word/PDF文档 |
| 表格文件 | ```sheet | Excel/CSV数据 |

## 🔐 认证机制

所有API请求（除健康检查外）都需要在请求头中携带API密钥：

```http
Authorization: Bearer your-api-key
```

### 获取API密钥
请联系系统管理员获取有效的API密钥。

## 📊 API接口列表

### 1. 健康检查

**接口地址**: `GET /v1/health`

**功能说明**: 检查服务运行状态

**请求参数**: 无

**响应示例**:
```json
{
  "status": "healthy",
  "service": "file2markdown"
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
    ".docx", ".doc", 
    ".pdf",
    ".pptx", ".ppt",
    ".csv",
    ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp",
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs",
    ".html", ".css", ".json", ".yaml", ".xml", ".sql", ".sh"
  ],
  "total_count": 90
}
```

**支持的文件类型**:
- **文档类**: TXT, MD, DOCX, DOC, PDF
- **演示文稿**: PPTX, PPT  
- **表格数据**: XLSX, XLS, CSV
- **图像文件**: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- **代码文件**: 83+种编程语言（Python, JavaScript, Java, C++, Go, Rust等）

### 3. 文件转换

**接口地址**: `POST /v1/convert`

**功能说明**: 将上传的文件转换为Markdown代码块格式

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
  "markdown": "```python\ndef hello_world():\n    print('Hello, World!')\n    return 'success'\n```",
  "duration_ms": 150
}
```

**响应示例（图片文件）**:
```json
{
  "filename": "chart.png",
  "size": 204800,
  "content_type": "image/png",
  "markdown": "```image\n# OCR:\n图表标题：销售数据分析\n\n# Description:\n这是一个显示月度销售趋势的柱状图，包含了12个月的销售数据...\n```",
  "duration_ms": 2500
}
```

**响应示例（Word文档）**:
```json
{
  "filename": "document.docx",
  "size": 1280345,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "markdown": "```document\n# 文档标题\n\n这是文档内容...\n\n## 章节2\n\n更多内容...\n```",
  "duration_ms": 420
}
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

  // 文件转换
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

  // 检查文件类型是否支持
  async isFileSupported(filename) {
    const types = await this.getSupportedTypes();
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return types.supported_extensions.includes(ext);
  }
}

// 使用示例
const api = new MedicNexAPI('https://file.medicnex.com/v1', 'your-api-key');
```

### 文件上传组件示例 (React)

```jsx
import React, { useState, useCallback } from 'react';

const FileConverter = () => {
  const [file, setFile] = useState(null);
  const [converting, setConverting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const api = new MedicNexAPI('https://file.medicnex.com/v1', 'your-api-key');

  const handleFileSelect = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;

    // 检查文件类型
    const isSupported = await api.isFileSupported(selectedFile.name);
    if (!isSupported) {
      setError('不支持的文件类型');
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const handleConvert = async () => {
    if (!file) return;

    setConverting(true);
    setError(null);

    try {
      const response = await api.convertFile(file);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setConverting(false);
    }
  };

  // 解析代码块类型
  const parseCodeBlock = (markdown) => {
    const match = markdown.match(/^```(\w+)\n([\s\S]*?)```$/);
    if (match) {
      return {
        language: match[1],
        content: match[2]
      };
    }
    return { language: 'text', content: markdown };
  };

  const renderResult = () => {
    if (!result) return null;

    const { language, content } = parseCodeBlock(result.markdown);

    return (
      <div className="result">
        <h3>转换结果 ({language})</h3>
        <div className="file-info">
          <p>文件名: {result.filename}</p>
          <p>大小: {(result.size / 1024).toFixed(1)} KB</p>
          <p>处理时间: {result.duration_ms} ms</p>
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
  };

  return (
    <div className="file-converter">
      <div className="upload-area">
        <input 
          type="file" 
          onChange={handleFileSelect}
          disabled={converting}
        />
        
        {file && (
          <div className="file-info">
            <p>已选择: {file.name}</p>
            <button 
              onClick={handleConvert} 
              disabled={converting}
            >
              {converting ? '转换中...' : '开始转换'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error">
          错误: {error}
        </div>
      )}

      {renderResult()}
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

.convert-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
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

.result {
  background-color: #d4edda;
  color: #155724;
  padding: 20px;
  border-radius: 4px;
  margin: 10px 0;
}

.markdown-content {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.markdown-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
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
CSV和Excel文件会转换为Markdown表格格式，包含：
- 数据统计信息
- 完整的表格数据
- 数值列的统计分析

### 文档文件处理
Word和PDF文件会保持原有的：
- 标题层级结构
- 列表格式
- 表格布局
- 基本文本格式

## 🔄 批量处理示例

```javascript
class BatchProcessor {
  constructor(api, maxConcurrent = 3) {
    this.api = api;
    this.maxConcurrent = maxConcurrent;
  }

  async processFiles(files, onProgress) {
    const results = [];
    const chunks = this.chunkArray(files, this.maxConcurrent);
    
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      const chunkPromises = chunk.map(file => 
        this.api.convertFile(file).catch(error => ({
          filename: file.name,
          error: error.message
        }))
      );
      
      const chunkResults = await Promise.all(chunkPromises);
      results.push(...chunkResults);
      
      if (onProgress) {
        onProgress(results.length, files.length);
      }
    }
    
    return results;
  }

  chunkArray(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }
}

// 使用示例
const processor = new BatchProcessor(api, 3);
const results = await processor.processFiles(files, (completed, total) => {
  console.log(`进度: ${completed}/${total}`);
});
```

## 📋 最佳实践

1. **文件验证**：上传前检查文件类型和大小
2. **错误处理**：提供友好的错误提示信息
3. **进度显示**：大文件上传时显示处理进度
4. **缓存策略**：对相同文件避免重复转换
5. **安全考虑**：在客户端验证文件类型，但不依赖它作为唯一安全措施

## 🔗 相关链接

- **API文档**: `https://file.medicnex.com/docs`
- **在线测试**: `https://file.medicnex.com/redoc`
- **健康检查**: `https://file.medicnex.com/v1/health`

## 📞 技术支持

如有技术问题，请提供：
- API请求详情（URL、Headers、Body）
- 错误响应内容
- 文件类型和大小信息
- 浏览器控制台错误日志

---

**祝您开发愉快！如有疑问，随时联系技术支持团队。** 