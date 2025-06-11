# 支持的文件格式详细列表

MedicNex File2Markdown 支持 **123 种文件格式**，分布在 **17 个解析器**中。

## 📊 统计概览

- **总支持扩展名数量**: 123 种
- **解析器数量**: 17 个
- **最大类别**: 代码文件（82种）
- **文档类型**: 12种
- **图片类型**: 10种
- **音频类型**: 8种
- **视频类型**: 6种

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

### 3. AudioParser（14种）
**音频格式**: `.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.wma`, `.aac`
**视频格式**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp`

### 4. PlainParser（2种）
`.txt`, `.text`

### 5. MarkdownParser（2种）
`.md`, `.markdown`

### 6. PptxParser（2种）
`.ppt`, `.pptx`

### 7. ExcelParser（2种）
`.xls`, `.xlsx`

### 8. DocxParser（1种）
`.docx`

### 9. DocParser（1种）
`.doc`

### 10. SvgParser（1种）
`.svg`

### 11. RtfParser（1种）
`.rtf`

### 12. PdfParser（1种）
`.pdf`

### 13. OdtParser（1种）
`.odt`

### 14. CsvParser（1种）
`.csv`

### 15. KeynoteParser（1种）
`.key`

### 16. PagesParser（1种）
`.pages`

### 17. NumbersParser（1种）
`.numbers`

## 📋 完整格式列表（按字母排序）

`.3gp`, `.aac`, `.astro`, `.avi`, `.bash`, `.bat`, `.bmp`, `.c`, `.cc`, `.cfg`, `.clj`, `.cljs`, `.cmake`, `.cmd`, `.conf`, `.cpp`, `.cs`, `.css`, `.csv`, `.cxx`, `.dart`, `.doc`, `.dockerfile`, `.dockerignore`, `.docx`, `.editorconfig`, `.elm`, `.env`, `.erl`, `.ex`, `.exs`, `.fish`, `.flac`, `.fs`, `.fsx`, `.gif`, `.gitattributes`, `.gitignore`, `.go`, `.gql`, `.gradle`, `.graphql`, `.groovy`, `.h`, `.hpp`, `.hs`, `.htm`, `.html`, `.ico`, `.ini`, `.java`, `.jl`, `.jpeg`, `.jpg`, `.js`, `.json`, `.jsx`, `.key`, `.kt`, `.less`, `.lhs`, `.lua`, `.m`, `.m4a`, `.make`, `.makefile`, `.markdown`, `.mat`, `.md`, `.mkv`, `.mov`, `.mp3`, `.mp4`, `.numbers`, `.odt`, `.ogg`, `.pages`, `.pdf`, `.perl`, `.php`, `.pl`, `.png`, `.postcss`, `.ppt`, `.pptx`, `.proto`, `.ps1`, `.py`, `.r`, `.rb`, `.rs`, `.rtf`, `.sass`, `.scala`, `.scss`, `.sh`, `.sql`, `.styl`, `.svelte`, `.svg`, `.swift`, `.tex`, `.text`, `.tga`, `.tiff`, `.toml`, `.ts`, `.tsx`, `.txt`, `.vim`, `.vimrc`, `.vue`, `.wav`, `.webm`, `.webp`, `.wma`, `.wmv`, `.xls`, `.xlsx`, `.xml`, `.yaml`, `.yml`, `.zsh`

## 🎯 特殊功能说明

### 音频文件
- **智能分块**：基于能量分析的音频分块，自动检测静音区域
- **并发ASR转换**：多个音频片段同时进行语音识别转换
- **多种技术路线**：
  - ① 预处理：统一采样率、转单声道、去直流偏移
  - ② 能量分析：计算短时RMS能量，动态阈值检测
  - ③ 智能分割：合并相近静音区域，过滤短片段
  - ④ 并发转录：多线程调用ASR API进行语音转文字
- **输出格式**：
  ```audio
  # 音频信息
  **文件名**: example.wav
  **时长**: 120.5 秒
  **采样率**: 16000 Hz
  **声道数**: 1
  **片段数**: 8
  
  # 语音转录
  ## 片段 1 [00:00.000 - 00:15.230]
  **音质**: 🟢 高质量 (置信度: 0.85)
  
  这里是转录的文字内容...
  ```

### 视频文件
- **音频提取**：自动从视频文件中提取音频轨道
- **字幕生成**：使用相同的智能分块和ASR技术生成字幕
- **SRT格式时间戳**：标准的HH:MM:SS,mmm时间格式
- **支持格式**：`.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.webm`, `.3gp`
- **输出格式**：
  ```video
  # Video Information
  **Filename**: presentation.mp4
  **Audio Duration**: 180.5 seconds
  **Sample Rate**: 16000 Hz
  **Segments**: 12
  
  # Subtitles
  
  1
  00:00:00,000 --> 00:00:08,450
  大家好，欢迎参加今天的项目会议。
  
  2
  00:00:09,200 --> 00:00:15,680
  我们今天主要讨论三个议题。
  
  # Processing Statistics
  **Valid Segments**: 12/12
  **Total Characters**: 1847
  ```

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
| KeynoteParser | `slideshow` | ````slideshow` |
| PagesParser | `document` | ````document` |
| NumbersParser | `sheet` | ````sheet` |
| AudioParser | `audio`/`video` | ````audio` (音频文件) / ````video` (视频文件) |

---

> 最后更新：2025-06-11  
> 统计数据：123种格式 / 17个解析器  
> 新增功能：音频文件智能分块和ASR转换、视频文件字幕生成  