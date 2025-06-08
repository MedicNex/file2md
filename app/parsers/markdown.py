from .base import BaseParser
from loguru import logger
import chardet

class MarkdownParser(BaseParser):
    """Markdown文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.md', '.markdown']
    
    async def parse(self, file_path: str) -> str:
        """解析Markdown文件，保持原有格式"""
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
            
            # 直接返回markdown内容，不包装在代码块中
            logger.info(f"成功解析Markdown文件: {file_path}")
            return content.strip()
            
        except Exception as e:
            logger.error(f"解析Markdown文件失败 {file_path}: {e}")
            raise Exception(f"Markdown文件解析错误: {str(e)}") 