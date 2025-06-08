from .base import BaseParser
from loguru import logger
from app.vision import image_to_markdown

class ImageParser(BaseParser):
    """图片文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
    
    async def parse(self, file_path: str) -> str:
        """解析图片文件"""
        try:
            # 直接使用视觉模型解析图片
            markdown_content = await image_to_markdown(file_path)
            
            logger.info(f"成功解析图片文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析图片文件失败 {file_path}: {e}")
            raise Exception(f"图片文件解析错误: {str(e)}") 