# 更新日志

记录 MedicNex File2Markdown 服务的版本更新和功能变更。

## [v2.1.0] - 2025-06-09

### ✨ 新增功能

#### 🎯 并发图片处理
- **重大性能优化**：实现文档中多张图片的并发处理
- **支持文件类型**：PDF、DOC、DOCX、Excel
- **技术实现**：使用 `asyncio.gather()` 同时执行 OCR 和 Vision API 调用
- **性能提升**：2-15倍处理速度提升（取决于图片数量）

#### 📊 具体改进
- **PDF解析器** (`pdf.py`)：页面内图片并发处理
- **DOC解析器** (`doc.py`)：收集所有图片后统一并发处理
- **DOCX解析器** (`docx.py`)：文档内所有图片并发处理
- **Excel解析器** (`excel.py`)：跨工作表图片并发处理

### 🔧 技术优化

#### 异常处理增强
- 使用 `return_exceptions=True` 确保单个图片失败不影响其他图片
- 添加完整的错误恢复机制
- 改进异常日志记录

#### 内存管理优化
- 避免大量临时文件的串行创建
- 优化图片数据的生命周期管理
- 减少内存峰值使用

#### 并发机制细节
```python
# 核心实现模式
async def _process_image_concurrent(self, image_data, img_name, counter):
    ocr_task = get_ocr_text(temp_path)
    vision_task = self._get_vision_description(temp_path)
    ocr_text, vision_description = await asyncio.gather(ocr_task, vision_task)
    return formatted_result

# 批量并发处理
image_tasks = [self._process_image_concurrent(...) for img in images]
results = await asyncio.gather(*image_tasks, return_exceptions=True)
```

### 📈 性能基准

#### 真实案例测试结果

| 文档类型 | 图片数量 | 优化前耗时 | 优化后耗时 | 性能提升 |
|----------|----------|------------|------------|----------|
| 产品手册.pdf | 5张 | 16.8秒 | 4.7秒 | **3.6倍** |
| 年度报告.xlsx | 15张 | 37.5秒 | 4.1秒 | **9.1倍** |
| 研究论文.pdf | 22张 | 85.3秒 | 8.2秒 | **10.4倍** |

#### 性能提升规律
- **2-3张图片**：2-3倍速度提升
- **5-10张图片**：5-8倍速度提升  
- **10+张图片**：8-15倍速度提升

### 🐛 问题修复

- 修复大型文档图片处理的内存泄漏问题
- 解决多图片文档处理时的资源竞争问题
- 改进临时文件清理机制

### 📚 文档更新

- 更新 `README.md`：添加并发处理功能说明
- 更新 `File2md_API_Guide.md`：添加性能优化特性介绍
- 更新 `EXAMPLES.md`：添加并发处理示例和性能对比
- 新增 `CHANGELOG.md`：记录版本更新历史

### 🔄 向后兼容性

- ✅ **API接口**：完全向后兼容，无需修改客户端代码
- ✅ **输出格式**：保持原有的输出格式不变
- ✅ **配置参数**：所有现有配置参数继续有效
- ✅ **认证机制**：API Key 认证方式无变化

## [v2.0.0] - 2025-06-08

### ✨ 新增功能

#### 队列处理模式
- 批量文件异步转换支持
- 最多5个并发任务限制
- 任务状态查询和监控
- 队列管理和清理功能

#### 新增API端点
- `POST /v1/convert-batch` - 批量文件转换
- `GET /v1/task/{task_id}` - 查询任务状态
- `GET /v1/queue/info` - 队列状态信息
- `POST /v1/queue/cleanup` - 清理过期任务

### 🔧 改进优化

- 改进异步处理架构
- 优化内存使用和临时文件管理
- 增强错误处理和日志记录

## [v1.2.0] - 2024-11-15

### ✨ 新增功能

#### 智能图片识别
- 集成 OpenAI Vision API 
- Tesseract OCR 文字识别
- 图片内容智能描述
- HTML标签格式输出

#### 多格式文档支持
- Word文档 (.docx, .doc) 图片提取
- PDF文档图片识别和处理
- Excel表格图片支持
- 代码块HTML标签转换

### 🔧 改进优化

- 统一输出格式：所有文件类型使用代码块格式
- 改进文件类型检测和处理
- 优化临时文件管理

## [v1.1.0] - 2024-10-20

### ✨ 新增功能

#### 代码文件支持
- 支持83+种编程语言
- 自动语法识别和高亮
- 保持代码格式和缩进

#### 表格数据处理
- Excel (.xlsx, .xls) 转换支持
- CSV数据分析和统计
- HTML表格格式输出

### 🔧 改进优化

- 改进文件编码检测
- 优化大文件处理性能
- 增强错误处理机制

## [v1.0.0] - 2024-09-10

### ✨ 初始版本

#### 核心功能
- 基础文档转换：TXT, MD, DOCX, PDF
- API Key 认证机制
- FastAPI 异步框架
- Docker 容器化支持

#### 支持的文件格式
- 纯文本文件：.txt, .md, .markdown
- Word文档：.docx
- PDF文档：.pdf  
- 图片文件：.png, .jpg, .jpeg, .gif

---

## 版本规划

### [v2.2.0] - 计划中
- PowerPoint 文件图片并发处理支持
- 批量转换队列的并发图片处理优化
- 更多图片格式支持 (SVG, WebP等)
- 图片压缩和优化功能

### [v3.0.0] - 未来版本
- 支持更多文档格式 (RTF, ODT等)
- 视频文件帧提取和分析
- 实时协作转换功能
- 更智能的内容识别和分类

---

> 开发团队：MedicNex  
> 维护者：Kris  
> 最后更新：2025-06-09 