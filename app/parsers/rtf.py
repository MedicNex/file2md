from .base import BaseParser
from loguru import logger
import subprocess
import tempfile
import os
import re

class RtfParser(BaseParser):
    """RTF文档解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.rtf']
    
    async def parse(self, file_path: str) -> str:
        """解析RTF文件"""
        try:
            # 安全性检查
            if not self._validate_file_security(file_path):
                raise Exception("文件安全验证失败")
                
            # 使用pandoc将RTF转换为Markdown
            # 创建临时输出文件，指定UTF-8编码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md_path = temp_md.name
            
            self.temp_files.append(temp_md_path)
            
            # 使用pandoc转换RTF到Markdown
            try:
                result = subprocess.run([
                    'pandoc', 
                    os.path.abspath(file_path),  # 使用绝对路径防止路径遍历
                    '-t', 'markdown',
                    '-o', temp_md_path,
                    '--wrap=none',  # 不自动换行
                    '--sandbox'  # 启用沙箱模式
                ], capture_output=True, text=True, check=True, timeout=30)  # 添加超时
                
                # 读取转换后的Markdown内容
                with open(temp_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 内容清理
                content = self._sanitize_content(content)
                
                logger.info(f"成功解析RTF文件: {file_path}")
                return content.strip()
                
            except subprocess.TimeoutExpired:
                logger.error(f"Pandoc转换RTF超时: {file_path}")
                return await self._fallback_parse(file_path)
            except subprocess.CalledProcessError as e:
                logger.error(f"Pandoc转换RTF失败: {e}")
                # 如果pandoc失败，尝试简单的文本提取
                return await self._fallback_parse(file_path)
                
        except Exception as e:
            logger.error(f"解析RTF文件失败 {file_path}: {e}")
            # 尝试备用解析方法
            return await self._fallback_parse(file_path)
    
    async def _fallback_parse(self, file_path: str) -> str:
        """备用解析方法 - 使用striprtf库"""
        try:
            from striprtf.striprtf import rtf_to_text
            
            # 使用更robust的编码读取策略
            rtf_content = None
            encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'windows-1252']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        rtf_content = f.read()
                    logger.info(f"RTF文件使用编码 {encoding} 读取成功")
                    break
                except UnicodeDecodeError:
                    continue
            
            if rtf_content is None:
                # 最后尝试二进制读取
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                rtf_content = raw_data.decode('utf-8', errors='replace')
                logger.warning("RTF文件使用utf-8 errors='replace'模式读取")
            
            # 提取纯文本
            text_content = rtf_to_text(rtf_content)
            
            # 基本格式化
            lines = text_content.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    formatted_lines.append(line)
            
            content = '\n\n'.join(formatted_lines)
            
            logger.info(f"使用备用方法成功解析RTF文件: {file_path}")
            return content
            
        except ImportError:
            logger.warning("striprtf库未安装，无法解析RTF文件")
            raise Exception("RTF解析需要安装striprtf库: pip install striprtf")
        except Exception as e:
            logger.error(f"备用RTF解析失败: {e}")
            raise Exception(f"RTF文件解析错误: {str(e)}")
    
    def _validate_file_security(self, file_path: str) -> bool:
        """验证文件安全性"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小（限制为50MB）
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                logger.error(f"文件过大: {file_size} bytes")
                return False
            
            # 检查文件路径，防止路径遍历攻击
            abs_path = os.path.abspath(file_path)
            if '..' in file_path or abs_path != os.path.normpath(abs_path):
                logger.error(f"检测到可疑文件路径: {file_path}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"文件安全验证失败: {e}")
            return False
    
    def _sanitize_content(self, content: str) -> str:
        """清理内容，防止注入攻击"""
        if not content:
            return content
        
        # 移除潜在的危险字符和模式
        # 限制内容长度
        if len(content) > 1000000:  # 1MB 文本限制
            content = content[:1000000] + "\n\n... (内容被截断，超过限制)"
        
        # 清理潜在的markdown注入
        # 转义可能的代码块标记
        content = content.replace('```', '\\`\\`\\`')
        
        # 清理HTML标签（保留基本格式）
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content