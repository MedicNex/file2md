from .base import BaseParser
from loguru import logger
import pdfplumber
from PIL import Image
from app.vision import image_to_markdown, get_ocr_text, vision_client
import os
import base64

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
                            page_img = cropped_page.to_image(resolution=150)
                            page_img.save(temp_img_path, format='PNG')
                            
                            # 生成图片文件名
                            base_name = os.path.splitext(os.path.basename(file_path))[0]
                            img_name = f"{base_name}_page{page_num}_image_{img_idx + 1}.png"
                            
                            # 进行OCR和视觉识别
                            ocr_text = await get_ocr_text(temp_img_path)
                            
                            vision_description = ""
                            if vision_client:
                                try:
                                    # 读取图片并转换为base64
                                    with open(temp_img_path, "rb") as image_file:
                                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                                    
                                    response = vision_client.chat.completions.create(
                                        model=os.getenv("VISION_MODEL", "gpt-4o-mini"),
                                        messages=[
                                            {
                                                "role": "user",
                                                "content": [
                                                    {
                                                        "type": "image_url",
                                                        "image_url": {
                                                            "url": f"data:image/png;base64,{base64_image}"
                                                        }
                                                    },
                                                    {
                                                        "type": "text", 
                                                        "text": "请详细描述这张图片的内容，包括：1. 图片的整体精准描述；2. 图片的主要元素和结构；3. 如果有表格、图表等，请详细描述其内容和布局。"
                                                    }
                                                ]
                                            }
                                        ],
                                        max_tokens=1000
                                    )
                                    vision_description = response.choices[0].message.content
                                except Exception as e:
                                    logger.warning(f"Vision API调用失败: {e}")
                                    vision_description = "视觉模型识别失败"
                            else:
                                vision_description = "视觉模型未配置"
                            
                            # 生成HTML标签格式
                            alt_text = f"# OCR: {ocr_text} # Description: {vision_description}"
                            html_img_tag = f'<img src="{img_name}" alt="{alt_text}" />'
                            
                            content_parts.append(f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n{html_img_tag}")
                            
                            logger.info(f"成功处理PDF图片 第{page_num}页 图片{img_idx + 1}: {img_name}")
                            
                        except Exception as img_error:
                            logger.warning(f"PDF图片提取失败 第{page_num}页 图片{img_idx + 1}: {img_error}")
                            content_parts.append(f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n*图片提取失败*")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content or 'PDF文件为空或无法提取内容'}\n```"
            
            logger.info(f"成功解析PDF文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析PDF文件失败 {file_path}: {e}")
            raise Exception(f"PDF文件解析错误: {str(e)}") 