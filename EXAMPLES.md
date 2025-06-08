# MedicNex File2Markdown 转换示例

本文档提供了各种文件类型的真实转换示例，帮助开发者更好地理解系统功能。

## 📋 目录

1. [复杂DOCX文档转换](#复杂docx文档转换)
2. [代码文件转换](#代码文件转换)
3. [图片文件转换](#图片文件转换)
4. [PDF文档转换](#pdf文档转换)
5. [Excel表格转换](#excel表格转换)

## 复杂DOCX文档转换

### 输入文件
- **文件名**: `test_doc_with_image_and_codeblock.docx`
- **大小**: 15,970 bytes
- **内容**: 包含Python代码块和UI界面截图

### API调用
```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@test_doc_with_image_and_codeblock.docx"
```

### 完整响应
```json
{
  "filename": "test_doc_with_image_and_codeblock.docx",
  "size": 15970,
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "content": "```document\n<code class=\"language-python\">\ndef hello():\n\nprint(\"hello world\")\n\n</code>\n\n### 图片 1\n\n<img src=\"document_image_1.png\" alt=\"# OCR: HelloWorla!\n\nom! # Description: ### 1. 整体精准描述\n\n这张图片展示了一个简单的用户界面元素，背景为浅蓝色。图中包含一个白色边框的矩形区域，矩形内包含两行不同颜色的文本。整体布局简洁，内容和结构清晰易辨。\n\n### 2. 主要元素和结构\n\n- **背景：** 整个图片的背景为统一的浅蓝色，没有其他图案或装饰。\n- **矩形框：** 位于图片中央，是一个白色矩形框，具有黑色边框，背景颜色为纯白色，显得十分醒目。\n- **文本内容：**\n  - 第一行文本内容为\"Hello World!\"，字体为黑色，字体大小适中，位于矩形框顶部稍靠左的位置。\n  - 第二行文本内容为\" fascinated! \"，字体为红色，较第一行字体稍小，紧接在第一行的下方，同样是稍微偏左对齐。\n- **布局：** 两行文本在矩形框内垂直排列，具有一定的间距，并且都是左对齐，保持一定的对齐美感。\n\n### 3. 表格、图表及其他内容\n\n该图片中并未包含任何表格、图表等其他复杂元素，仅包含两段文字。内容上没有多余修饰，主要聚焦于两行文本信息的展示。\" />\n```",
  "duration_ms": 14208
}
```

### 功能亮点分析

1. **🔧 智能代码块转换**
   ```
   原始: ```python
   转换: <code class="language-python">
   ```
   - 保持语法高亮标识
   - 适配前端代码高亮库

2. **🖼️ 图片OCR识别**
   ```
   识别结果: "HelloWorla! om!"
   ```
   - 支持中英文混合识别
   - 容错性强，部分识别错误也能提供有用信息

3. **🤖 AI视觉分析**
   - **布局分析**: 浅蓝色背景，白色矩形框，黑色边框
   - **文本分析**: "Hello World!" (黑色) + "fascinated!" (红色)
   - **结构描述**: 垂直排列，左对齐，间距合理

4. **📝 HTML标签规范**
   ```html
   <img src="document_image_1.png" 
        alt="# OCR: ... # Description: ..." />
   ```
   - src: 唯一图片标识
   - alt: 结构化的OCR和AI分析结果

## 代码文件转换

### Python文件示例
```bash
# 输入文件: hello.py
def greet(name):
    """向用户问好"""
    print(f"Hello, {name}!")
    return f"Greeting sent to {name}"

if __name__ == "__main__":
    greet("World")
```

### 转换结果
```json
{
  "filename": "hello.py",
  "size": 156,
  "content_type": "text/x-python",
  "content": "```python\ndef greet(name):\n    \"\"\"向用户问好\"\"\"\n    print(f\"Hello, {name}!\")\n    return f\"Greeting sent to {name}\"\n\nif __name__ == \"__main__\":\n    greet(\"World\")\n```",
  "duration_ms": 23
}
```

## 图片文件转换

### 输入: 测试图片
- **文件**: `test_image.png` 
- **内容**: 包含"MedicNex File2Markdown Vision API Test"文字的界面

### 转换结果
```json
{
  "filename": "test_image.png",
  "size": 3072,
  "content_type": "image/png",
  "content": "```image\n# OCR:\nMedicNex File2Markdown\n\nVision API Test\n\n# Description:\n这张图片展示了一个简洁的测试界面，主要用于验证视觉API功能。图片包含清晰的英文标题文字，布局整洁，适合用作API功能测试。\n```",
  "duration_ms": 8456
}
```

## 性能基准测试

| 文件类型 | 大小 | 处理时间 | 主要耗时 |
|----------|------|----------|----------|
| 纯文本 (.txt) | < 1KB | < 50ms | 文件读取 |
| 代码文件 (.py/.js) | < 10KB | < 100ms | 语法识别 |
| 简单图片 (.png) | < 5MB | 3-8秒 | OCR处理 |
| 复杂DOCX | < 20MB | 10-15秒 | 图片提取+AI分析 |
| PDF文档 | < 50MB | 15-30秒 | 页面解析+图片处理 |

## 最佳实践建议

### 1. 文件上传优化
```javascript
// 检查文件大小
if (file.size > 100 * 1024 * 1024) { // 100MB
  alert('文件过大，请选择小于100MB的文件');
  return;
}

// 检查文件类型
const allowedTypes = ['.docx', '.pdf', '.png', '.jpg', '.py'];
const fileExt = file.name.toLowerCase().substr(file.name.lastIndexOf('.'));
if (!allowedTypes.includes(fileExt)) {
  alert('不支持的文件类型');
  return;
}
```

### 2. 处理超时设置
```javascript
// 根据文件大小设置合理的超时时间
const timeoutMs = Math.max(30000, file.size / 1024); // 至少30秒
const controller = new AbortController();
setTimeout(() => controller.abort(), timeoutMs);

fetch('/v1/convert', {
  signal: controller.signal,
  // ... 其他配置
});
```

### 3. 结果渲染优化
```javascript
// 渲染代码块
function renderCodeBlocks(content) {
  return content.replace(
    /<code class="language-(\w+)">(.*?)<\/code>/gs,
    (match, lang, code) => {
      return `<pre><code class="language-${lang}">${escapeHtml(code)}</code></pre>`;
    }
  );
}

// 渲染图片
function renderImages(content) {
  return content.replace(
    /<img src="([^"]*)" alt="([^"]*)" \/>/g,
    (match, src, alt) => {
      const [ocrText, description] = alt.split('# Description:');
      return `
        <div class="image-container">
          <img src="${src}" alt="${alt}" loading="lazy" />
          <details class="image-analysis">
            <summary>查看AI分析</summary>
            <div class="ocr-result">${ocrText}</div>
            <div class="ai-description">${description}</div>
          </details>
        </div>
      `;
    }
  );
}
```

## 故障排除

### 常见问题

1. **处理时间过长**
   - 原因：图片过多或尺寸过大
   - 解决：压缩图片或拆分文档

2. **OCR识别不准确**
   - 原因：图片质量低或文字模糊
   - 解决：提高图片分辨率，使用清晰字体

3. **视觉API调用失败**
   - 原因：API密钥无效或网络问题
   - 解决：检查环境配置，查看健康检查接口

### 调试建议

```bash
# 检查服务状态
curl -s "http://localhost:8999/v1/health" | jq

# 查看支持的文件类型
curl -s -H "Authorization: Bearer your-key" \
     "http://localhost:8999/v1/supported-types" | jq

# 测试简单文件
echo "test" > test.txt
curl -X POST -H "Authorization: Bearer your-key" \
     -F "file=@test.txt" "http://localhost:8999/v1/convert"
```

---

> 📝 此文档会随着系统功能更新而持续完善
> 🔗 更多信息请参考: [README.md](README.md) | [FRONTEND_API.md](FRONTEND_API.md) 