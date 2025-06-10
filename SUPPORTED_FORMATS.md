# 支持的文件格式详细列表

MedicNex File2Markdown 支持 **106 种文件格式**，分布在 **13 个解析器**中。

## 📊 统计概览

- **总支持扩展名数量**: 106 种
- **解析器数量**: 13 个
- **最大类别**: 代码文件（82种）
- **文档类型**: 9种
- **图片类型**: 10种

## 🔧 按解析器分类

### 1. CodeParser（82种）
**主流编程语言**：
`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rs`, `.php`, `.rb`

**前端技术**：
`.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.jsx`, `.tsx`, `.svelte`

**脚本语言**：
`.r`, `.lua`, `.perl`, `.pl`, `.sh`, `.bash`, `.zsh`, `.fish`, `.ps1`

**配置文件**：
`.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.cfg`, `.conf`

**数据库和其他**：
`.sql`, `.dockerfile`, `.makefile`, `.cmake`, `.gradle`, `.proto`, `.graphql`

**函数式语言**：
`.hs`, `.lhs`, `.clj`, `.cljs`, `.elm`, `.erl`, `.ex`, `.exs`, `.fs`, `.fsx`

**系统和工具**：
`.vim`, `.vimrc`, `.env`, `.gitignore`, `.gitattributes`, `.editorconfig`

**Web框架**：
`.astro`, `.postcss`, `.styl`

**科学计算**：
`.m`, `.mat`, `.tex`, `.jl`

**移动开发**：
`.swift`, `.kt`, `.dart`

**其他工具**：
`.bat`, `.cmd`, `.cc`, `.cxx`, `.h`, `.hpp`, `.groovy`, `.scala`, `.dockerignore`

### 2. ImageParser（9种）
`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.ico`, `.tga`

### 3. MarkdownParser（2种）
`.md`, `.markdown`

### 4. PlainParser（2种）
`.txt`, `.text`

### 5. PptxParser（2种）
`.ppt`, `.pptx`

### 6. ExcelParser（2种）
`.xls`, `.xlsx`

### 7. DocxParser（1种）
`.docx`

### 8. DocParser（1种）
`.doc`

### 9. SvgParser（1种）
`.svg`

### 10. RtfParser（1种）
`.rtf`

### 11. PdfParser（1种）
`.pdf`

### 12. OdtParser（1种）
`.odt`

### 13. CsvParser（1种）
`.csv`

## 📋 完整格式列表（按字母排序）

`.astro`, `.bash`, `.bat`, `.bmp`, `.c`, `.cc`, `.cfg`, `.clj`, `.cljs`, `.cmake`, `.cmd`, `.conf`, `.cpp`, `.cs`, `.css`, `.csv`, `.cxx`, `.dart`, `.doc`, `.dockerfile`, `.dockerignore`, `.docx`, `.editorconfig`, `.elm`, `.env`, `.erl`, `.ex`, `.exs`, `.fish`, `.fs`, `.fsx`, `.gif`, `.gitattributes`, `.gitignore`, `.go`, `.gql`, `.gradle`, `.graphql`, `.groovy`, `.h`, `.hpp`, `.hs`, `.htm`, `.html`, `.ico`, `.ini`, `.java`, `.jl`, `.jpeg`, `.jpg`, `.js`, `.json`, `.jsx`, `.kt`, `.less`, `.lhs`, `.lua`, `.m`, `.make`, `.makefile`, `.markdown`, `.mat`, `.md`, `.odt`, `.pdf`, `.perl`, `.php`, `.pl`, `.png`, `.postcss`, `.ppt`, `.pptx`, `.proto`, `.ps1`, `.py`, `.r`, `.rb`, `.rs`, `.rtf`, `.sass`, `.scala`, `.scss`, `.sh`, `.sql`, `.styl`, `.svelte`, `.svg`, `.swift`, `.tex`, `.text`, `.tga`, `.tiff`, `.toml`, `.ts`, `.tsx`, `.txt`, `.vim`, `.vimrc`, `.vue`, `.webp`, `.xls`, `.xlsx`, `.xml`, `.yaml`, `.yml`, `.zsh`

## 🎯 特殊功能说明

### SVG 文件
- **同时识别**代码结构和视觉特征
- **自动转换**为 PNG 进行 OCR 和 AI 视觉分析
- **依赖库**：ImageMagick（优先）或 CairoSVG（备选）
- **输出格式**：
  ```svg
  # Code
  <code class="language-svg">...</code>
  # Visual_Features: ...
  ```

### 图片文件
- **OCR识别**：使用 Tesseract 提取文字
- **视觉分析**：使用 AI 模型分析图像内容
- **并发处理**：同时进行 OCR 和视觉识别

### 代码文件
- **语法高亮**：保持对应语言的代码块格式
- **自动识别**：根据文件扩展名自动选择语言
- **特殊处理**：支持 Dockerfile、Makefile 等无扩展名文件

### 文档文件
- **图片提取**：自动提取并处理文档中的图片
- **并发处理**：多张图片同时进行识别
- **格式保持**：保留表格、列表等结构

## 📈 性能特性

- **并发图片处理**：处理速度提升 2-10 倍
- **异步队列**：支持批量文件转换
- **智能降级**：依赖库不可用时提供明确提示
- **内存优化**：大文件流式处理

## 🔄 输出格式映射

| 解析器类型 | 输出代码块格式 | 示例 |
|------------|----------------|------|
| CodeParser | 对应语言标识符 | ````python`, ````javascript` |
| ImageParser | `image` | ````image` |
| SvgParser | `svg` | ````svg` |
| MarkdownParser | `markdown` | ````markdown` |
| PlainParser | `text` | ````text` |
| DocxParser | `document` | ````document` |
| DocParser | `document` | ````document` |
| PdfParser | `document` | ````document` |
| PptxParser | `slideshow` | ````slideshow` |
| ExcelParser | `sheet` | ````sheet` |
| CsvParser | `sheet` | ````sheet` |
| RtfParser | `document` | ````document` |
| OdtParser | `document` | ````document` |

---

> 最后更新：2025-01-15  
> 统计数据：106种格式 / 13个解析器  
> 测试脚本：`test_supported_types.py` 