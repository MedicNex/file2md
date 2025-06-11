# 音频处理功能使用指南

## 概述

MedicNex File2Markdown 现已支持音频文件的智能分块处理和ASR（自动语音识别）转换功能。该功能基于能量分析的音频分块技术，能够自动检测静音区域，智能分割音频，并通过并发方式调用ASR模型进行语音转文字。

## 支持的音频格式

- **无损格式**: `.wav`, `.flac`
- **有损格式**: `.mp3`, `.aac`, `.ogg`, `.wma`
- **容器格式**: `.mp4`, `.m4a`

总计 **8 种音频格式**，通过 `AudioParser` 解析器处理。

## 核心技术特性

### 1. 智能音频预处理

```python
# 预处理步骤：
# ① 统一采样率为 16kHz（适合语音识别）
# ② 转换为单声道（减少计算复杂度）
# ③ 高通滤波去除直流偏移（80Hz高通）
```

### 2. 基于能量分析的分块算法

采用您提到的核心算法实现：

| 步骤      | 关键操作                      | 目的              |
| ------- | ------------------------- | --------------- |
| ① 预处理   | 统一采样率、转单声道、去直流偏移          | 消除硬件差异带来的伪低频    |
| ② 能量分析  | 计算短时能量（RMS）或频带能量谱         | 定位"近乎静音"区段      |
| ③ 阈值自适应 | 用分位数 / Otsu / GMM 等方法动态设阈 | 兼顾不同录音环境的底噪     |
| ④ 片段标记  | 将连续低于阈值的帧合并成"静音节点"        | 得到候选分割点         |
| ⑤ 分割输出  | 在节点处切片、写文件或返回时间戳          | 供后续 ASR / 分析 使用 |

### 3. 关键算法参数

```python
# 短时能量计算
frame_ms = 20                    # 20ms 滑窗
min_silence_len = 300           # 最小静音长度 300ms
highpass_hz = 150               # 高通滤波频率

# 自适应阈值（分位数法）
p10 = np.percentile(rms_db, 10)  # 10分位值作为噪声地板
silence_thresh_db = p10 + 3      # 阈值 = 地板 + 3dB缓冲

# 片段长度控制
min_segment_duration = 2        # 最小段长度 2秒
max_segment_duration = 30       # 最大段长度 30秒
```

### 4. 置信度评估

```python
# 基于平均能量计算置信度
avg_energy = np.mean(rms_db[start:end])
confidence = min(1.0, max(0.1, (avg_energy - silence_thresh_db) / 20))

# 置信度分级：
# 🟢 高质量 (>= 0.8)
# 🟡 中等质量 (0.5 - 0.8)
# 🔴 低质量 (< 0.5)
```

### 5. 并发ASR转换

- **最大并发数**: 受 `MAX_CONCURRENT` 环境变量控制
- **异步处理**: 使用 `asyncio.gather()` 并发调用
- **容错机制**: 单个片段失败不影响其他片段处理
- **API兼容**: 支持 OpenAI Whisper API 格式

## 配置说明

### 环境变量配置

```bash
# ASR Audio API 配置
ASR_MODEL=whisper-1                    # ASR模型名称
ASR_API_BASE=https://api.openai.com/v1 # API基础URL
ASR_API_KEY=your-openai-api-key        # API密钥

# 性能配置
MAX_CONCURRENT=5                       # 最大并发处理数
```

### 依赖库安装

```bash
# 核心依赖
pip install pydub numpy

# 可选高级分析
pip install librosa

# 系统依赖（音频格式支持）
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# 下载 ffmpeg 并添加到 PATH
```

## API 使用

### 单文件转换

```bash
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@recording.wav"
```

### 响应格式

```json
{
  "filename": "recording.wav",
  "size": 2048576,
  "content_type": "audio/wav",
  "content": "```audio\n# 音频信息\n**文件名**: recording.wav\n**时长**: 120.5 秒\n...\n```",
  "duration_ms": 8500
}
```

### 输出示例

```audio
# 音频信息
**文件名**: meeting_recording.wav
**时长**: 180.3 秒
**采样率**: 16000 Hz
**声道数**: 1
**片段数**: 12

# 语音转录

## 片段 1 [00:00.000 - 00:08.450]
**音质**: 🟢 高质量 (置信度: 0.92)

大家好，欢迎参加今天的项目会议。我们今天主要讨论三个议题。

## 片段 2 [00:09.200 - 00:15.680]
**音质**: 🟡 中等质量 (置信度: 0.67)

首先是项目进度汇报，请各组负责人简要介绍一下当前的工作状态。

## 片段 3 [00:16.100 - 00:28.920]
**音质**: 🟢 高质量 (置信度: 0.88)

我们开发组这边已经完成了核心功能的开发，目前正在进行单元测试。预计下周可以提交第一版代码。

# 处理统计
**有效片段**: 12/12
**转录字符数**: 1847
**平均片段时长**: 15.0 秒
```

## 测试工具

### 使用测试脚本

```bash
# 基础功能测试（创建测试音频）
python scripts/test_audio_parser.py

# 使用自己的音频文件测试
python scripts/test_audio_parser.py -f /path/to/your/audio.wav

# 测试真实ASR API（需要配置环境变量）
python scripts/test_audio_parser.py --test-real-asr

# 创建更长的测试音频
python scripts/test_audio_parser.py -d 30
```

### 测试输出示例

```
🎵 音频解析器测试工具
==================================================
创建 10 秒的测试音频...
测试音频已创建: /tmp/tmpxx7x8x9x.wav

=== 测试音频预处理 ===
✅ 预处理成功
   时长: 10.0 秒
   采样率: 16000 Hz
   声道数: 1

=== 测试音频分块 ===
✅ 分块成功，共 3 个片段
   片段 1: 1.00s - 3.00s (时长: 2.00s, 置信度: 0.85)
   片段 2: 3.50s - 6.50s (时长: 3.00s, 置信度: 0.92)
   片段 3: 7.50s - 9.50s (时长: 2.00s, 置信度: 0.78)

🎉 所有测试完成！音频解析器功能正常
```

## 高级配置

### 自定义分块参数

```python
# 在代码中可以调整这些参数
segments = await parser._split_audio_by_energy(
    audio,
    frame_ms=25,              # 帧长度（毫秒）
    min_silence_len=500,      # 最小静音长度（毫秒）
    silence_thresh_db=-30,    # 静音阈值（dBFS）
    highpass_hz=100           # 高通滤波频率（Hz）
)
```

### 医学音频特殊处理

对于心音、呼吸音等医学音频，可以调整参数：

```python
# 医学低频音频（心音 ≤ 100 Hz）
# 使用带通滤波而非高通
from scipy import signal

# 20-120 Hz 带通滤波器
def medical_audio_filter(audio, low_freq=20, high_freq=120):
    # 实现带通滤波逻辑
    pass
```

## 性能优化建议

### 1. 批量处理

```bash
# 使用批量API处理多个音频文件
curl -X POST "https://file.medicnex.com/v1/convert-batch" \
  -H "Authorization: Bearer your-api-key" \
  -F "files=@audio1.wav" \
  -F "files=@audio2.mp3" \
  -F "files=@audio3.m4a"
```

### 2. 并发优化

- 根据服务器性能调整 `MAX_CONCURRENT`
- 长音频会自动分割为多个片段并发处理
- 推荐并发数：2-8（取决于CPU核心数和网络带宽）

### 3. 内存管理

- 大音频文件采用流式处理
- 临时文件自动清理
- 分块处理避免内存溢出

## 故障排除

### 常见问题

1. **pydub 导入失败**
   ```bash
   pip install pydub
   # macOS 需要安装 ffmpeg
   brew install ffmpeg
   ```

2. **numpy 版本不兼容**
   ```bash
   pip install numpy>=1.24.3
   ```

3. **ASR API 调用失败**
   - 检查 API 密钥是否正确
   - 验证网络连接
   - 确认 API 限制和配额

4. **音频分块异常**
   - 检查音频文件是否损坏
   - 尝试转换音频格式
   - 调整分块参数

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看能量分析结果
import matplotlib.pyplot as plt
plt.plot(rms_db)
plt.axhline(y=silence_thresh_db, color='r', linestyle='--')
plt.show()
```

## 与其他模态的集合

### 音视频文件处理

```bash
# .mp4 文件同时包含音频和视频
curl -X POST "https://file.medicnex.com/v1/convert" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@presentation.mp4"
```

输出将包含音频转录内容（视频帧提取功能需要额外开发）。

### 多模态文档

```bash
# 包含音频的复合文档处理
# 例如：PowerPoint + 音频注释
curl -X POST "https://file.medicnex.com/v1/convert-batch" \
  -H "Authorization: Bearer your-api-key" \
  -F "files=@slides.pptx" \
  -F "files=@narration.wav"
```

## 技术扩展

### 实时流式处理

```python
# 未来可扩展的实时处理接口
async def process_audio_stream(websocket):
    async for audio_chunk in websocket:
        # 实时分块和转录
        segments = await process_chunk(audio_chunk)
        await websocket.send(json.dumps(segments))
```

### 更多ASR模型支持

```python
# 支持多种ASR服务
ASR_PROVIDERS = {
    'openai': OpenAIASRClient,
    'azure': AzureASRClient,
    'google': GoogleASRClient,
    'local': LocalWhisperClient
}
```

---

> **注意**: 该功能需要配置ASR API密钥。建议在生产环境中使用专门的语音识别服务，以获得最佳的转录质量和性能。 