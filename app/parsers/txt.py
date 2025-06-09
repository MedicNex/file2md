from .base import BaseParser
from loguru import logger
import chardet
import aiofiles
import os
from app.config import config

class PlainParser(BaseParser):
    """纯文本文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.txt', '.text', '.md', '.markdown']
    
    async def parse(self, file_path: str) -> str:
        """解析纯文本文件"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(file_path)
            logger.info(f"开始解析文本文件: {file_path}, 大小: {file_size} bytes")
            
            # 检测文件编码（只读取前几KB用于编码检测）
            sample_size = min(file_size, 10240)  # 最多读取10KB用于编码检测
            with open(file_path, 'rb') as f:
                raw_sample = f.read(sample_size)
                detected_encoding = chardet.detect(raw_sample)
                encoding = detected_encoding.get('encoding') or 'utf-8'
                confidence = detected_encoding.get('confidence', 0)
                
                logger.info(f"检测到文件编码: {encoding} (置信度: {confidence:.2f})")
            
            # 使用异步方式读取文件内容
            try:
                content = await self.read_file_async(file_path, mode='r', encoding=encoding)
            except UnicodeDecodeError as e:
                logger.warning(f"使用检测编码 {encoding} 读取失败，尝试使用 utf-8: {e}")
                # 如果检测的编码失败，尝试使用utf-8
                try:
                    content = await self.read_file_async(file_path, mode='r', encoding='utf-8')
                    encoding = 'utf-8'
                except UnicodeDecodeError:
                    # 如果utf-8也失败，使用latin-1（不会失败）然后尝试转换
                    logger.warning("utf-8 编码也失败，使用 latin-1 编码读取")
                    content = await self.read_file_async(file_path, mode='r', encoding='latin-1')
                    encoding = 'latin-1'
            
            # 统计文件信息
            line_count = content.count('\n') + 1 if content else 0
            char_count = len(content)
            
            logger.info(f"文件读取成功: {line_count} 行, {char_count} 字符, 编码: {encoding}")
            
            # 检查文本文件大小限制
            if char_count > config.MAX_TEXT_CHARS:
                raise Exception(f"文本文件过大: {char_count} 字符，最大允许: {config.MAX_TEXT_CHARS} 字符")
            
            if line_count > config.MAX_TEXT_LINES:
                raise Exception(f"文本文件行数过多: {line_count} 行，最大允许: {config.MAX_TEXT_LINES} 行")
            
            # 处理换行符
            content = content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            formatted_content = f"```text\n{content.strip()}\n```"
            
            logger.info(f"成功解析纯文本文件: {file_path}")
            return formatted_content
            
        except FileNotFoundError as e:
            logger.error(f"文件不存在: {file_path}")
            raise Exception(f"文件不存在: {str(e)}")
        except PermissionError as e:
            logger.error(f"文件权限不足: {file_path}")
            raise Exception(f"文件权限不足: {str(e)}")
        except MemoryError as e:
            logger.error(f"文件过大，内存不足: {file_path}")
            raise Exception(f"文件过大，内存不足: {str(e)}")
        except Exception as e:
            logger.error(f"解析纯文本文件失败 {file_path}: {e}")
            raise Exception(f"纯文本文件解析错误: {str(e)}") 