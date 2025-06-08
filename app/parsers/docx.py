from .base import BaseParser
from loguru import logger
import docx
from markdownify import markdownify
import io
import os
from PIL import Image
from app.vision import image_to_markdown, get_ocr_text, vision_client
import base64

class DocxParser(BaseParser):
    """DOCX文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.docx']
    
    async def parse(self, file_path: str) -> str:
        """解析DOCX文件"""
        try:
            doc = docx.Document(file_path)
            
            # 提取所有段落文本
            content_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # 处理不同的段落样式
                    text = paragraph.text.strip()
                    
                    # 检查是否是标题
                    if paragraph.style.name.startswith('Heading'):
                        level = int(paragraph.style.name.split()[-1])
                        text = f"{'#' * level} {text}"
                    
                    content_parts.append(text)
            
            # 处理表格
            for table in doc.tables:
                content_parts.append(self._parse_table(table))
            
            # 提取并处理图片
            image_parts = await self._extract_images(doc, file_path)
            content_parts.extend(image_parts)
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content}\n```"
            
            logger.info(f"成功解析DOCX文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析DOCX文件失败 {file_path}: {e}")
            raise Exception(f"DOCX文件解析错误: {str(e)}")
    
    def _parse_table(self, table) -> str:
        """解析表格为Markdown格式"""
        try:
            rows = []
            for i, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                if i == 0:
                    # 表头
                    rows.append('| ' + ' | '.join(cells) + ' |')
                    rows.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
                else:
                    # 数据行
                    rows.append('| ' + ' | '.join(cells) + ' |')
            
            return '\n'.join(rows)
        except Exception as e:
            logger.warning(f"表格解析失败: {e}")
            return "[表格解析失败]"
    
    async def _extract_images(self, doc, file_path: str) -> list[str]:
        """提取DOCX文档中的图片并进行OCR+视觉识别"""
        image_parts = []
        
        try:
            # 获取文档的关系部分来访问图片
            rels = doc.part.rels
            image_counter = 0
            
            for rel_id, rel in rels.items():
                if "image" in rel.target_ref:
                    try:
                        image_counter += 1
                        # 获取图片数据
                        image_data = rel.target_part.blob
                        
                        # 创建临时图片文件
                        temp_img_path = self.create_temp_file(suffix='.png')
                        
                        # 保存图片
                        with open(temp_img_path, 'wb') as img_file:
                            img_file.write(image_data)
                        
                        # 生成图片文件名
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        img_name = f"{base_name}_image_{image_counter}.png"
                        
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
                        
                        image_parts.append(f"### 图片 {image_counter}\n\n{html_img_tag}")
                        
                        logger.info(f"成功处理DOCX图片 {image_counter}: {img_name}")
                        
                    except Exception as img_error:
                        logger.warning(f"DOCX图片提取失败 图片{image_counter}: {img_error}")
                        image_parts.append(f"### 图片 {image_counter}\n\n*图片提取失败*")
            
            if image_counter > 0:
                logger.info(f"DOCX文档中共提取到 {image_counter} 张图片")
            
        except Exception as e:
            logger.warning(f"DOCX图片提取过程失败: {e}")
        
        return image_parts 