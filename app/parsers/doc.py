from .base import BaseParser
from loguru import logger
import mammoth
from markdownify import markdownify
import os
import base64
from app.vision import get_ocr_text, vision_client

class DocParser(BaseParser):
    """DOC文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.doc']
    
    async def parse(self, file_path: str) -> str:
        """解析DOC文件"""
        try:
            image_counter = 0
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 定义图片转换函数，用于处理嵌入的图片
            def convert_image(image):
                nonlocal image_counter
                image_counter += 1
                
                try:
                    # 创建临时图片文件
                    temp_img_path = self.create_temp_file(suffix='.png')
                    
                    # 保存图片数据
                    with open(temp_img_path, 'wb') as img_file:
                        img_file.write(image.read())
                    
                    # 生成图片文件名
                    img_name = f"{base_name}_image_{image_counter}.png"
                    
                    # 这里返回一个占位符，稍后会被替换为完整的HTML标签
                    return {
                        "src": img_name,
                        "temp_path": temp_img_path,
                        "placeholder": f"__IMAGE_PLACEHOLDER_{image_counter}__"
                    }
                    
                except Exception as e:
                    logger.warning(f"DOC图片处理失败: {e}")
                    return {
                        "src": f"{base_name}_image_{image_counter}.png",
                        "temp_path": None,
                        "placeholder": f"__IMAGE_ERROR_{image_counter}__"
                    }
            
            # 使用mammoth将DOC转换为HTML，同时处理图片
            with open(file_path, "rb") as doc_file:
                # 创建图片转换器
                image_results = []
                
                def image_converter(image):
                    result = convert_image(image)
                    image_results.append(result)
                    return result["placeholder"]
                
                result = mammoth.convert_to_html(
                    doc_file,
                    convert_image=mammoth.images.img_element(image_converter)
                )
                html_content = result.value
                
                # 记录警告信息
                if result.messages:
                    for message in result.messages:
                        logger.warning(f"DOC转换警告: {message}")
            
            # 将HTML转换为Markdown
            raw_content = markdownify(html_content, heading_style="ATX")
            
            # 处理图片占位符，替换为完整的HTML标签
            for img_result in image_results:
                placeholder = img_result["placeholder"]
                img_name = img_result["src"]
                temp_path = img_result["temp_path"]
                
                if temp_path and os.path.exists(temp_path):
                    try:
                        # 进行OCR和视觉识别
                        ocr_text = await get_ocr_text(temp_path)
                        
                        vision_description = ""
                        if vision_client:
                            try:
                                # 读取图片并转换为base64
                                with open(temp_path, "rb") as image_file:
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
                        
                        # 替换占位符
                        raw_content = raw_content.replace(placeholder, html_img_tag)
                        
                        logger.info(f"成功处理DOC图片: {img_name}")
                        
                    except Exception as e:
                        logger.warning(f"DOC图片OCR/视觉识别失败: {e}")
                        # 替换为简单的图片标签
                        html_img_tag = f'<img src="{img_name}" alt="图片处理失败" />'
                        raw_content = raw_content.replace(placeholder, html_img_tag)
                else:
                    # 图片提取失败的情况
                    html_img_tag = f'<img src="{img_name}" alt="图片提取失败" />'
                    raw_content = raw_content.replace(placeholder, html_img_tag)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content.strip()}\n```"
            
            if image_counter > 0:
                logger.info(f"DOC文档中共处理了 {image_counter} 张图片")
            
            logger.info(f"成功解析DOC文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析DOC文件失败 {file_path}: {e}")
            raise Exception(f"DOC文件解析错误: {str(e)}") 