from .base import BaseParser
from loguru import logger
import pdfplumber
from PIL import Image
from app.vision import image_to_markdown
import os

class PdfParser(BaseParser):
    """PDF文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.pdf']
    
    async def parse(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            content_parts = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取文本
                    text = page.extract_text()
                    if text and text.strip():
                        content_parts.append(f"## 第 {page_num} 页\n\n{text.strip()}")
                    
                    # 提取图片
                    images = page.images
                    for img_idx, img in enumerate(images):
                        try:
                            # 提取图片
                            bbox = (img['x0'], img['top'], img['x1'], img['bottom'])
                            cropped_page = page.crop(bbox)
                            
                            # 保存为临时图片文件
                            temp_img_path = self.create_temp_file(suffix='.png')
                            
                            # 将页面转换为图片
                            page_img = page.to_image(resolution=150)
                            page_img.save(temp_img_path, format='PNG')
                            
                            # 使用视觉模型解析图片
                            img_markdown = await image_to_markdown(temp_img_path)
                            content_parts.append(f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n{img_markdown}")
                            
                        except Exception as img_error:
                            logger.warning(f"PDF图片提取失败 第{page_num}页 图片{img_idx}: {img_error}")
                            content_parts.append(f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n*图片提取失败*")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content or 'PDF文件为空或无法提取内容'}\n```"
            
            logger.info(f"成功解析PDF文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析PDF文件失败 {file_path}: {e}")
            raise Exception(f"PDF文件解析错误: {str(e)}") 