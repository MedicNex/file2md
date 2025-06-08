import openai
import base64
import os
from loguru import logger
from typing import Optional
import pytesseract
from PIL import Image
import httpx
from dotenv import load_dotenv
from pathlib import Path

# 确保加载环境变量，指定.env文件路径
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 配置视觉API客户端
VISION_API_KEY = os.getenv("VISION_API_KEY")
VISION_API_BASE = os.getenv("VISION_API_BASE", "https://api.openai.com/v1")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o-mini")

def init_vision_client():
    """初始化视觉API客户端"""
    if not VISION_API_KEY and not os.getenv("OPENAI_API_KEY"):
        logger.info("未配置Vision API密钥")
        return None
        
    try:
        if VISION_API_KEY:
            if VISION_API_BASE and VISION_API_BASE != "https://api.openai.com/v1":
                # 使用自定义API配置
                client = openai.OpenAI(
                    api_key=VISION_API_KEY,
                    base_url=VISION_API_BASE
                )
                logger.info(f"使用自定义Vision API: {VISION_API_BASE}")
                return client
            else:
                # 使用默认OpenAI配置
                client = openai.OpenAI(api_key=VISION_API_KEY)
                logger.info("使用OpenAI Vision API")
                return client
        elif os.getenv("OPENAI_API_KEY"):
            # 兼容旧配置
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("使用OPENAI_API_KEY初始化Vision client")
            return client
    except Exception as e:
        logger.error(f"Vision client初始化失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        return None
    
    return None

# 配置Vision客户端
vision_client = init_vision_client()

async def image_to_markdown(image_path: str) -> str:
    """
    使用视觉大模型和OCR将图片转换为Markdown文本
    """
    try:
        # 读取图片并转换为base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        markdown_content = ""
        
        # 先获取OCR结果
        ocr_text = await get_ocr_text(image_path)
        
        # 如果配置了Vision API，使用Vision API获取描述
        vision_description = ""
        logger.info(f"Vision client状态: {vision_client is not None}")
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
                                    "text": "请详细描述这张图片的内容，包括：1. 图片的整体精准描述；2. 图片的主要元素和结构；3. 如果有表格、图表等，请详细描述其内容和布局。请只返回描述内容，不要包含OCR文字提取。"
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                vision_description = response.choices[0].message.content
                logger.info(f"Vision API成功处理图片: {image_path}，使用模型: {VISION_MODEL}")
            except Exception as e:
                logger.warning(f"Vision API调用失败: {e}")
                vision_description = "视觉模型不可用，无法提供详细描述。"
        else:
            vision_description = "视觉模型未配置，无法提供详细描述。"
        
        # 组合OCR和视觉描述结果
        markdown_content = format_image_result(ocr_text, vision_description)
        
        return markdown_content or "*无法识别图片内容*"
        
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        return f"*图片处理失败: {str(e)}*"

async def get_ocr_text(image_path: str) -> str:
    """
    使用Tesseract OCR提取图片中的文字
    """
    try:
        # 使用Tesseract进行OCR
        image = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        if ocr_text.strip():
            logger.info(f"OCR成功提取文字: {image_path}")
            return ocr_text.strip()
        else:
            logger.warning(f"OCR未能提取到文字: {image_path}")
            return "未检测到文字内容"
            
    except Exception as e:
        logger.error(f"OCR处理失败: {e}")
        return f"OCR处理错误: {str(e)}"

def format_image_result(ocr_text: str, vision_description: str) -> str:
    """
    格式化图片处理结果，按照要求的markdown格式
    """
    # 处理换行符
    ocr_text = ocr_text.replace('\\n', '\n')
    vision_description = vision_description.replace('\\n', '\n')
    
    # 使用统一的代码块格式
    result = f"```image\n# OCR:\n{ocr_text}\n\n# Description:\n{vision_description}\n```"
    return result

async def fallback_ocr(image_path: str) -> str:
    """
    使用Tesseract OCR作为回退方案 (保持向后兼容)
    """
    ocr_text = await get_ocr_text(image_path)
    vision_description = "图片包含文字内容，已通过OCR技术提取。"
    return format_image_result(ocr_text, vision_description) 