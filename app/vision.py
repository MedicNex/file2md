import openai
import base64
import os
from loguru import logger
from typing import Optional
import pytesseract
from PIL import Image
import httpx

# 配置视觉API客户端
VISION_API_KEY = os.getenv("VISION_API_KEY")
VISION_API_BASE = os.getenv("VISION_API_BASE", "https://api.openai.com/v1")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o-mini")

# 配置Vision客户端
vision_client = None
if VISION_API_KEY:
    try:
        if VISION_API_BASE and VISION_API_BASE != "https://api.openai.com/v1":
            # 使用自定义API配置
            vision_client = openai.OpenAI(
                api_key=VISION_API_KEY,
                base_url=VISION_API_BASE
            )
        else:
            # 使用默认OpenAI配置
            vision_client = openai.OpenAI(api_key=VISION_API_KEY)
    except Exception as e:
        logger.warning(f"Vision client初始化失败: {e}")
        vision_client = None
elif os.getenv("OPENAI_API_KEY"):
    # 兼容旧配置
    try:
        vision_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        logger.warning(f"OpenAI client初始化失败: {e}")
        vision_client = None

async def image_to_markdown(image_path: str) -> str:
    """
    使用视觉大模型和OCR将图片转换为Markdown文本
    """
    try:
        # 读取图片并转换为base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        markdown_content = ""
        
        # 如果配置了Vision API，使用Vision API
        if vision_client:
            try:
                response = vision_client.chat.completions.create(
                    model=VISION_MODEL,
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
                                    "text": "请描述这张图片的内容，并提取其中的所有文字。如果图片包含表格、图表或结构化内容，请以Markdown格式输出。"
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                markdown_content = response.choices[0].message.content
                logger.info(f"Vision API成功处理图片: {image_path}，使用模型: {VISION_MODEL}")
            except Exception as e:
                logger.warning(f"Vision API调用失败: {e}，回退到OCR")
                markdown_content = await fallback_ocr(image_path)
        else:
            # 回退到OCR
            markdown_content = await fallback_ocr(image_path)
        
        return markdown_content or "![图片](image)\n\n*无法识别图片内容*"
        
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        return f"![图片处理失败]({image_path})\n\n*错误: {str(e)}*"

async def fallback_ocr(image_path: str) -> str:
    """
    使用Tesseract OCR作为回退方案
    """
    try:
        # 使用Tesseract进行OCR
        image = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        if ocr_text.strip():
            logger.info(f"OCR成功提取文字: {image_path}")
            return f"![图片](image)\n\n**提取的文字内容：**\n\n{ocr_text.strip()}"
        else:
            logger.warning(f"OCR未能提取到文字: {image_path}")
            return "![图片](image)\n\n*未检测到文字内容*"
            
    except Exception as e:
        logger.error(f"OCR处理失败: {e}")
        return f"![图片](image)\n\n*OCR错误: {str(e)}*" 