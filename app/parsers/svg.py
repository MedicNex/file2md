from .base import BaseParser
from loguru import logger
import chardet

class SvgParser(BaseParser):
    """SVG文件解析器 - 将SVG识别为代码格式"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.svg']
    
    async def parse(self, file_path: str) -> str:
        """解析SVG文件为代码格式"""
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            # 读取SVG文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 格式化为SVG代码块
            formatted_content = f"```svg\n{content.strip()}\n```"
            
            logger.info(f"成功解析SVG文件为代码格式: {file_path}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"解析SVG文件失败 {file_path}: {e}")
            raise Exception(f"SVG文件解析错误: {str(e)}") 