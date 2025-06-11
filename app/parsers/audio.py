import os
import asyncio
import tempfile
import subprocess
import numpy as np
from typing import List, Tuple, Optional
import httpx
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

from .base import BaseParser
from app.config import config

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub未安装，音频处理功能将受限")

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger.warning("librosa未安装，高级音频分析功能将受限")


class AudioSegmentInfo:
    """音频片段信息"""
    def __init__(self, start_time: float, end_time: float, segment, 
                 confidence: float = 1.0):
        self.start_time = start_time
        self.end_time = end_time
        self.segment = segment
        self.confidence = confidence
        self.duration = end_time - start_time


class AudioParser(BaseParser):
    """音频/视频文件解析器 - 支持分块处理和ASR转换"""
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        return ['.wav', '.mp3', '.mp4', '.m4a', '.flac', '.ogg', '.wma', '.aac', 
                '.avi', '.mov', '.wmv', '.mkv', '.webm', '.3gp']
    
    def __init__(self):
        super().__init__()
        self.asr_model = os.getenv("ASR_MODEL", "")
        self.asr_api_base = os.getenv("ASR_API_BASE", "")
        self.asr_api_key = os.getenv("ASR_API_KEY", "")
        self.max_segment_duration = 30  # 最大段长度(秒)
        self.min_segment_duration = 2   # 最小段长度(秒)
        
        # 视频格式列表
        self.video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm', '.3gp'}
    
    async def parse(self, file_path: str) -> str:
        """解析音频/视频文件并转换为文本"""
        try:
            if not PYDUB_AVAILABLE:
                raise Exception("音频处理需要安装pydub库: pip install pydub")
            
            # 检查文件类型
            file_extension = os.path.splitext(file_path)[1].lower()
            is_video = file_extension in self.video_extensions
            
            if is_video:
                logger.info(f"开始解析视频文件: {file_path}")
            else:
                logger.info(f"开始解析音频文件: {file_path}")
            
            # 1. 预处理音频（视频文件会自动提取音频轨道）
            audio = await self._preprocess_audio(file_path)
            
            # 2. 基于能量分析进行分块
            segments = await self._split_audio_by_energy(audio)
            
            # 3. 并发ASR转换
            transcriptions = await self._batch_transcribe_segments(segments)
            
            # 4. 格式化输出（根据文件类型选择输出格式）
            if is_video:
                formatted_content = await self._format_video_subtitle_output(
                    file_path, audio, segments, transcriptions
                )
            else:
                formatted_content = await self._format_audio_output(
                    file_path, audio, segments, transcriptions
                )
            
            logger.info(f"成功解析{'视频' if is_video else '音频'}文件: {file_path}, 共{len(segments)}个片段")
            return formatted_content
            
        except Exception as e:
            logger.error(f"解析{'视频' if is_video else '音频'}文件失败 {file_path}: {e}")
            raise Exception(f"{'视频' if is_video else '音频'}文件解析错误: {str(e)}")
    
    async def _preprocess_audio(self, file_path: str):
        """音频预处理 - 统一采样率、转单声道、去直流偏移"""
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(file_path)
            
            # 转换为单声道
            if audio.channels > 1:
                audio = audio.set_channels(1)
                logger.info("音频转换为单声道")
            
            # 统一采样率为16kHz (适合语音识别)
            target_sample_rate = 16000
            if audio.frame_rate != target_sample_rate:
                audio = audio.set_frame_rate(target_sample_rate)
                logger.info(f"音频采样率调整为 {target_sample_rate}Hz")
            
            # 去直流偏移 (使用高通滤波)
            audio = audio.high_pass_filter(80)  # 80Hz高通，去除低频噪声
            
            logger.info(f"音频预处理完成: {len(audio)/1000:.1f}秒, {audio.frame_rate}Hz")
            return audio
            
        except Exception as e:
            logger.error(f"音频预处理失败: {e}")
            raise
    
    async def _split_audio_by_energy(self, audio, 
                                   frame_ms: int = 20,
                                   min_silence_len: int = 300,
                                   silence_thresh_db: Optional[float] = None,
                                   highpass_hz: int = 150) -> List[AudioSegmentInfo]:
        """基于能量分析的智能音频分块"""
        try:
            logger.info("开始基于能量分析的音频分块...")
            
            # 高通滤波去除低频噪声
            if highpass_hz:
                filtered_audio = audio.high_pass_filter(highpass_hz)
            else:
                filtered_audio = audio
            
            # 计算短时能量(RMS)
            frame_samples = int(audio.frame_rate * frame_ms / 1000)
            raw = np.array(filtered_audio.get_array_of_samples())
            
            # 确保能整除成完整帧
            total_frames = len(raw) // frame_samples
            raw = raw[:total_frames * frame_samples]
            frames = raw.reshape(-1, frame_samples)
            
            # 计算RMS能量
            rms = np.sqrt((frames.astype(np.float32)**2).mean(axis=1))
            rms_db = 20 * np.log10(rms + 1e-10)  # 避免log(0)
            
            # 自适应阈值计算
            if silence_thresh_db is None:
                # 使用分位数方法: 10分位值 + 3dB缓冲
                p10 = np.percentile(rms_db, 10)
                silence_thresh_db = p10 + 3
                logger.info(f"自动计算静音阈值: {silence_thresh_db:.1f} dBFS")
            
            # 标记静音帧
            silent = rms_db < silence_thresh_db
            
            # 合并连续静音区域
            change = np.diff(np.r_[0, silent, 0])
            starts = np.where(change == 1)[0]
            ends = np.where(change == -1)[0]
            
            # 过滤短静音，并合并相近的静音区域
            valid_silences = []
            for s, e in zip(starts, ends):
                duration_ms = (e - s) * frame_ms
                if duration_ms >= min_silence_len:
                    valid_silences.append((s * frame_ms, e * frame_ms))
            
            # 合并间隔很近的静音区域 (< 200ms)
            merged_silences = self._merge_close_silences(valid_silences, 200)
            
            # 生成音频片段
            segments = []
            last_end = 0
            
            for silence_start, silence_end in merged_silences:
                # 添加当前语音段
                if silence_start > last_end:
                    segment_audio = audio[last_end:silence_start]
                    if len(segment_audio) >= self.min_segment_duration * 1000:
                        # 计算置信度 (基于平均能量)
                        segment_frames = frames[last_end//frame_ms:silence_start//frame_ms]
                        if len(segment_frames) > 0:
                            avg_energy = np.mean(rms_db[last_end//frame_ms:silence_start//frame_ms])
                            confidence = min(1.0, max(0.1, (avg_energy - silence_thresh_db) / 20))
                        else:
                            confidence = 0.5
                        
                        segments.append(AudioSegmentInfo(
                            start_time=last_end / 1000,
                            end_time=silence_start / 1000,
                            segment=segment_audio,
                            confidence=confidence
                        ))
                
                last_end = silence_end
            
            # 添加最后一段
            if last_end < len(audio):
                segment_audio = audio[last_end:]
                if len(segment_audio) >= self.min_segment_duration * 1000:
                    avg_energy = np.mean(rms_db[last_end//frame_ms:])
                    confidence = min(1.0, max(0.1, (avg_energy - silence_thresh_db) / 20))
                    
                    segments.append(AudioSegmentInfo(
                        start_time=last_end / 1000,
                        end_time=len(audio) / 1000,
                        segment=segment_audio,
                        confidence=confidence
                    ))
            
            # 进一步处理过长的片段
            final_segments = []
            for seg in segments:
                if seg.duration > self.max_segment_duration:
                    # 分割过长的段
                    sub_segments = self._split_long_segment(seg)
                    final_segments.extend(sub_segments)
                else:
                    final_segments.append(seg)
            
            logger.info(f"音频分块完成: {len(final_segments)}个片段, 阈值 {silence_thresh_db:.1f} dBFS")
            
            # 如果没有找到有效片段，使用时间分割作为后备方案
            if not final_segments:
                logger.warning("基于能量的分块未发现有效片段，使用时间分割后备方案")
                return self._fallback_time_split(audio)
            
            return final_segments
            
        except Exception as e:
            logger.error(f"音频分块失败: {e}")
            # 降级方案：简单时间分割
            return self._fallback_time_split(audio)
    
    def _merge_close_silences(self, silences: List[Tuple[int, int]], 
                            merge_threshold_ms: int) -> List[Tuple[int, int]]:
        """合并间隔很近的静音区域"""
        if not silences:
            return []
        
        merged = [silences[0]]
        for start, end in silences[1:]:
            last_end = merged[-1][1]
            if start - last_end <= merge_threshold_ms:
                # 合并
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        
        return merged
    
    def _split_long_segment(self, segment: AudioSegmentInfo) -> List[AudioSegmentInfo]:
        """分割过长的音频段"""
        sub_segments = []
        current_time = segment.start_time
        segment_audio = segment.segment
        
        while current_time < segment.end_time:
            chunk_end_time = min(current_time + self.max_segment_duration, segment.end_time)
            chunk_start_ms = int((current_time - segment.start_time) * 1000)
            chunk_end_ms = int((chunk_end_time - segment.start_time) * 1000)
            
            chunk_audio = segment_audio[chunk_start_ms:chunk_end_ms]
            
            sub_segments.append(AudioSegmentInfo(
                start_time=current_time,
                end_time=chunk_end_time,
                segment=chunk_audio,
                confidence=segment.confidence
            ))
            
            current_time = chunk_end_time
        
        return sub_segments
    
    def _fallback_time_split(self, audio) -> List[AudioSegmentInfo]:
        """降级方案：简单时间分割"""
        logger.warning("使用降级方案：简单时间分割")
        segments = []
        current_time = 0
        
        while current_time < len(audio) / 1000:
            end_time = min(current_time + self.max_segment_duration, len(audio) / 1000)
            start_ms = int(current_time * 1000)
            end_ms = int(end_time * 1000)
            
            segment_audio = audio[start_ms:end_ms]
            segments.append(AudioSegmentInfo(
                start_time=current_time,
                end_time=end_time,
                segment=segment_audio,
                confidence=0.8  # 中等置信度
            ))
            
            current_time = end_time
        
        return segments
    
    async def _batch_transcribe_segments(self, segments: List[AudioSegmentInfo]) -> List[str]:
        """并发批量ASR转换"""
        try:
            logger.info(f"开始并发ASR转换 {len(segments)} 个片段...")
            
            # 使用线程池并发处理
            max_workers = min(len(segments), config.MAX_CONCURRENT)
            
            async def transcribe_single_segment(segment: AudioSegmentInfo) -> str:
                try:
                    # 保存片段到临时文件
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        segment.segment.export(temp_file.name, format='wav')
                        temp_path = temp_file.name
                    
                    try:
                        # 调用ASR API
                        transcription = await self._call_asr_api(temp_path)
                        
                        # 根据置信度调整输出
                        if segment.confidence < 0.3:
                            transcription = f"[低质量音频] {transcription}"
                        
                        return transcription
                        
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                            
                except Exception as e:
                    logger.warning(f"片段转换失败: {e}")
                    return f"[转换失败: {str(e)}]"
            
            # 并发执行转换
            tasks = [transcribe_single_segment(seg) for seg in segments]
            transcriptions = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            results = []
            for i, result in enumerate(transcriptions):
                if isinstance(result, Exception):
                    logger.error(f"片段 {i} 转换异常: {result}")
                    results.append(f"[转换异常: {str(result)}]")
                else:
                    results.append(result)
            
            logger.info(f"ASR转换完成: {len(results)}个片段")
            return results
            
        except Exception as e:
            logger.error(f"批量ASR转换失败: {e}")
            return [f"[ASR转换失败: {str(e)}]"] * len(segments)
    
    async def _call_asr_api(self, audio_file_path: str) -> str:
        """调用ASR API进行语音识别"""
        if not self.asr_api_key or not self.asr_api_base:
            return "[ASR未配置]"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(audio_file_path, 'rb') as f:
                    files = {'file': f}
                    data = {
                        'model': self.asr_model or 'whisper-1',
                        'response_format': 'text'
                    }
                    headers = {
                        'Authorization': f'Bearer {self.asr_api_key}'
                    }
                    
                    response = await client.post(
                        f"{self.asr_api_base.rstrip('/')}/audio/transcriptions",
                        files=files,
                        data=data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        return response.text.strip()
                    else:
                        logger.error(f"ASR API错误: {response.status_code} - {response.text}")
                        return f"[ASR API错误: {response.status_code}]"
                        
        except Exception as e:
            logger.error(f"ASR API调用失败: {e}")
            return f"[ASR调用失败: {str(e)}]"
    
    async def _format_audio_output(self, file_path: str, audio, 
                                 segments: List[AudioSegmentInfo], 
                                 transcriptions: List[str]) -> str:
        """格式化音频解析输出"""
        try:
            # 基本信息
            duration_seconds = len(audio) / 1000
            sample_rate = audio.frame_rate
            channels = audio.channels
            
            # 构建输出内容
            output_parts = []
            
            # 音频基本信息
            output_parts.append("# 音频信息")
            output_parts.append(f"**文件名**: {os.path.basename(file_path)}")
            output_parts.append(f"**时长**: {duration_seconds:.1f} 秒")
            output_parts.append(f"**采样率**: {sample_rate} Hz")
            output_parts.append(f"**声道数**: {channels}")
            output_parts.append(f"**片段数**: {len(segments)}")
            output_parts.append("")
            
            # 分段转录结果
            output_parts.append("# 语音转录")
            output_parts.append("")
            
            for i, (segment, transcription) in enumerate(zip(segments, transcriptions)):
                start_time = segment.start_time
                end_time = segment.end_time
                confidence = segment.confidence
                
                # 时间戳格式化
                start_str = self._format_timestamp(start_time)
                end_str = self._format_timestamp(end_time)
                
                # 片段标题
                output_parts.append(f"## 片段 {i+1} [{start_str} - {end_str}]")
                
                # 置信度指示
                if confidence >= 0.8:
                    quality_indicator = "🟢 高质量"
                elif confidence >= 0.5:
                    quality_indicator = "🟡 中等质量"
                else:
                    quality_indicator = "🔴 低质量"
                
                output_parts.append(f"**音质**: {quality_indicator} (置信度: {confidence:.2f})")
                output_parts.append("")
                
                # 转录文本
                if transcription and transcription.strip():
                    output_parts.append(transcription.strip())
                else:
                    output_parts.append("*[无法识别的语音内容]*")
                
                output_parts.append("")
            
            # 统计信息
            total_chars = sum(len(t) for t in transcriptions if t)
            valid_segments = sum(1 for t in transcriptions if t and not t.startswith('['))
            
            output_parts.append("# 处理统计")
            output_parts.append(f"**有效片段**: {valid_segments}/{len(segments)}")
            output_parts.append(f"**转录字符数**: {total_chars}")
            if len(segments) > 0:
                output_parts.append(f"**平均片段时长**: {duration_seconds/len(segments):.1f} 秒")
            else:
                output_parts.append("**平均片段时长**: N/A (无有效片段)")
            
            # 格式化为音频代码块
            content = '\n'.join(output_parts)
            formatted_content = f"```audio\n{content}\n```"
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"格式化输出失败: {e}")
            return f"```audio\n# 音频解析失败\n错误: {str(e)}\n```"
    
    async def _format_video_subtitle_output(self, file_path: str, audio, 
                                           segments: List[AudioSegmentInfo], 
                                           transcriptions: List[str]) -> str:
        """格式化视频字幕输出"""
        try:
            # 基本信息
            duration_seconds = len(audio) / 1000
            sample_rate = audio.frame_rate
            
            # 构建输出内容
            output_parts = []
            
            # 视频基本信息
            output_parts.append("# Video Information")
            output_parts.append(f"**Filename**: {os.path.basename(file_path)}")
            output_parts.append(f"**Audio Duration**: {duration_seconds:.1f} seconds")
            output_parts.append(f"**Sample Rate**: {sample_rate} Hz")
            output_parts.append(f"**Segments**: {len(segments)}")
            output_parts.append("")
            
            # 字幕内容
            output_parts.append("# Subtitles")
            output_parts.append("")
            
            for i, (segment, transcription) in enumerate(zip(segments, transcriptions)):
                start_time = segment.start_time
                end_time = segment.end_time
                confidence = segment.confidence
                
                # SRT格式的时间戳
                start_str = self._format_srt_timestamp(start_time)
                end_str = self._format_srt_timestamp(end_time)
                
                # 字幕条目（类似SRT格式）
                output_parts.append(f"{i+1}")
                output_parts.append(f"{start_str} --> {end_str}")
                
                # 转录文本（如果有效）
                if transcription and transcription.strip() and not transcription.startswith('['):
                    output_parts.append(transcription.strip())
                else:
                    # 如果是低质量或失败的转录，添加质量标记
                    if confidence < 0.5:
                        output_parts.append(f"[Low Quality Audio] {transcription}")
                    else:
                        output_parts.append("*[Inaudible]*")
                
                output_parts.append("")  # 空行分隔
            
            # 处理统计
            total_chars = sum(len(t) for t in transcriptions if t and not t.startswith('['))
            valid_segments = sum(1 for t in transcriptions if t and not t.startswith('['))
            
            output_parts.append("# Processing Statistics")
            output_parts.append(f"**Valid Segments**: {valid_segments}/{len(segments)}")
            output_parts.append(f"**Total Characters**: {total_chars}")
            if len(segments) > 0:
                output_parts.append(f"**Average Segment Duration**: {duration_seconds/len(segments):.1f} seconds")
            else:
                output_parts.append("**Average Segment Duration**: N/A (no valid segments)")
            
            # 格式化为视频代码块
            content = '\n'.join(output_parts)
            formatted_content = f"```video\n{content}\n```"
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"视频字幕格式化失败: {e}")
            return f"```video\n# Video Subtitle Generation Failed\nError: {str(e)}\n```"
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """格式化SRT时间戳为 HH:MM:SS,mmm 格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为 MM:SS.mmm 格式"""
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}" 