from .base import BaseParser
from loguru import logger
import mammoth
import docx2txt
import subprocess
from markdownify import markdownify
import os
import base64
import asyncio
from app.vision import get_ocr_text, vision_client
from app.config import config

class DocParser(BaseParser):
    """DOC文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.doc']
    
    async def _process_image_concurrent(self, temp_path: str, img_name: str, img_idx: int):
        """并发处理单个图片的OCR和视觉识别"""
        if not temp_path or not os.path.exists(temp_path):
            return img_name, f'<img src="{img_name}" alt="图片提取失败，已跳过" />'
        
        try:
            # 并发执行OCR和视觉识别，添加异常保护
            try:
                ocr_task = get_ocr_text(temp_path)
                vision_task = self._get_vision_description(temp_path)
                
                ocr_text, vision_description = await asyncio.gather(ocr_task, vision_task)
            except Exception as ocr_vision_error:
                logger.warning(f"OCR/视觉识别失败，跳过处理 图片{img_idx}: {ocr_vision_error}")
                ocr_text = "OCR处理失败"
                vision_description = "视觉识别失败"
            
            # 生成HTML标签格式
            alt_text = f"# OCR: {ocr_text} # Visual_Features: {vision_description}"
            html_img_tag = f'<img src="{img_name}" alt="{alt_text}" />'
            
            logger.info(f"成功处理DOC图片: {img_name}")
            return img_name, html_img_tag
            
        except Exception as e:
            logger.warning(f"DOC图片OCR/视觉识别失败，跳过该图片: {e}")
            html_img_tag = f'<img src="{img_name}" alt="图片处理失败，已跳过" />'
            return img_name, html_img_tag
    
    async def _get_vision_description(self, temp_img_path: str) -> str:
        """获取视觉模型描述"""
        if not vision_client:
            return "视觉模型未配置"
        
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
                                "text": "Please provide a detailed description of this image, including: 1. Overall accurate description of the image; 2. Main elements and structure of the image; 3. If there are tables, charts, etc., please describe their content and layout in detail."
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content or "视觉模型识别失败"
        except Exception as e:
            logger.warning(f"Vision API调用失败: {e}")
            return "视觉模型识别失败"

    async def parse(self, file_path: str) -> str:
        """解析DOC文件"""
        try:
            logger.info(f"开始解析DOC文件: {file_path}")
            
            # 首先尝试使用antiword处理DOC文件（最适合传统二进制DOC文件）
            try:
                logger.info("尝试使用antiword解析DOC文件...")
                result = subprocess.run(['antiword', file_path], 
                                      capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    raw_content = result.stdout
                    logger.info("antiword解析成功")
                else:
                    raise Exception(f"antiword返回错误码: {result.returncode}, 错误信息: {result.stderr}")
            except Exception as antiword_error:
                logger.warning(f"antiword解析失败: {antiword_error}")
                
                # 如果antiword失败，尝试使用docx2txt
                try:
                    logger.info("尝试使用docx2txt解析DOC文件...")
                    raw_content = str(docx2txt.process(file_path) or "")
                    logger.info("docx2txt解析成功")
                except Exception as docx2txt_error:
                    logger.warning(f"docx2txt解析失败: {docx2txt_error}")
                    
                    # 如果docx2txt失败，尝试使用mammoth（主要用于DOCX，但某些DOC文件可能兼容）
                    try:
                        logger.info("尝试使用mammoth解析DOC文件...")
                        with open(file_path, "rb") as doc_file:
                            result = mammoth.convert_to_html(doc_file)
                            raw_content = result.value
                            
                            # 记录警告信息
                            if result.messages:
                                for message in result.messages:
                                    logger.warning(f"DOC转换警告: {message}")
                        
                        # 将HTML转换为Markdown
                        raw_content = markdownify(raw_content, heading_style="ATX")
                        logger.info("mammoth解析成功")
                        
                    except Exception as mammoth_error:
                        logger.error(f"所有DOC解析方法都失败了: {mammoth_error}")
                        raise Exception(f"无法解析DOC文件，所有解析方法都失败: antiword({antiword_error}), docx2txt({docx2txt_error}), mammoth({mammoth_error})")
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content.strip()}\n```"
            
            logger.info(f"成功解析DOC文件: {file_path}")
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析DOC文件失败 {file_path}: {e}")
            raise Exception(f"DOC文件解析错误: {str(e)}") 