from .base import BaseParser
from loguru import logger
import subprocess
import tempfile
import os

class RtfParser(BaseParser):
    """RTF文档解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.rtf']
    
    async def parse(self, file_path: str) -> str:
        """解析RTF文件"""
        try:
            # 使用pandoc将RTF转换为Markdown
            # 创建临时输出文件，指定UTF-8编码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md_path = temp_md.name
            
            self.temp_files.append(temp_md_path)
            
            # 使用pandoc转换RTF到Markdown
            try:
                result = subprocess.run([
                    'pandoc', 
                    file_path,
                    '-t', 'markdown',
                    '-o', temp_md_path,
                    '--wrap=none'  # 不自动换行
                ], capture_output=True, text=True, check=True)
                
                # 读取转换后的Markdown内容
                with open(temp_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"成功解析RTF文件: {file_path}")
                return content.strip()
                
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