from .base import BaseParser
from loguru import logger
import chardet

class PlainParser(BaseParser):
    """纯文本和Markdown文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.txt', '.md', '.markdown', '.text']
    
    async def parse(self, file_path: str) -> str:
        """解析纯文本或Markdown文件"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 处理换行符
            content = content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            formatted_content = f"```text\n{content.strip()}\n```"
            
            logger.info(f"成功解析纯文本文件: {file_path}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"解析纯文本文件失败 {file_path}: {e}")
            raise Exception(f"纯文本文件解析错误: {str(e)}") 