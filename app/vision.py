import openai
import base64
import os
from loguru import logger
from typing import Optional
import pytesseract
from PIL import Image
import httpx
import asyncio
import aiofiles

from app.config import config
from app.exceptions import (
    VisionAPIError, VisionAPIConnectionError, VisionAPIRateLimitError, OCRError
)

def init_vision_client():
    """初始化视觉API客户端"""
    vision_api_key = config.get_vision_api_key()
    
    if not vision_api_key:
        logger.info("未配置Vision API密钥")
        return None
        
    try:
        if config.VISION_API_KEY:
            if config.VISION_API_BASE and config.VISION_API_BASE != "https://api.openai.com/v1":
                # 使用自定义API配置
                client = openai.OpenAI(
                    api_key=config.VISION_API_KEY,
                    base_url=config.VISION_API_BASE
                )
                logger.info(f"使用自定义Vision API: {config.VISION_API_BASE}")
                return client
            else:
                # 使用默认OpenAI配置
                client = openai.OpenAI(api_key=config.VISION_API_KEY)
                logger.info("使用OpenAI Vision API")
                return client
        elif config.OPENAI_API_KEY:
            # 兼容旧配置
            client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
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

async def call_vision_api_with_retry(base64_image: str, prompt: str) -> str:
    """
    带重试机制的视觉API调用
    
    Args:
        base64_image: base64编码的图片
        prompt: 提示词
        
    Returns:
        API响应内容
        
    Raises:
        VisionAPIError: API调用失败
    """
    if not vision_client:
        raise VisionAPIError("Vision client未初始化")
    
    last_exception = None
    delay = config.VISION_RETRY_DELAY
    
    for attempt in range(config.VISION_MAX_RETRIES):
        try:
            logger.info(f"Vision API调用尝试 {attempt + 1}/{config.VISION_MAX_RETRIES}")
            
            response = vision_client.chat.completions.create(
                model=config.VISION_MODEL,
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
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            logger.info(f"Vision API调用成功，使用模型: {config.VISION_MODEL}")
            return content
            
        except openai.RateLimitError as e:
            last_exception = VisionAPIRateLimitError(f"速率限制: {e}")
            logger.warning(f"Vision API速率限制，尝试 {attempt + 1}/{config.VISION_MAX_RETRIES}: {e}")
            
        except (openai.APIConnectionError, httpx.ConnectError) as e:
            last_exception = VisionAPIConnectionError(f"连接错误: {e}")
            logger.warning(f"Vision API连接失败，尝试 {attempt + 1}/{config.VISION_MAX_RETRIES}: {e}")
            
        except openai.APIError as e:
            last_exception = VisionAPIError(f"API错误: {e}")
            logger.error(f"Vision API错误，尝试 {attempt + 1}/{config.VISION_MAX_RETRIES}: {e}")
            
        except Exception as e:
            last_exception = VisionAPIError(f"未知错误: {e}")
            logger.error(f"Vision API未知错误，尝试 {attempt + 1}/{config.VISION_MAX_RETRIES}: {e}")
        
        # 如果不是最后一次尝试，等待后重试
        if attempt < config.VISION_MAX_RETRIES - 1:
            logger.info(f"等待 {delay:.1f} 秒后重试...")
            await asyncio.sleep(delay)
            delay *= config.VISION_BACKOFF_FACTOR  # 指数退避
    
    # 所有重试都失败了
    logger.error(f"Vision API调用失败，已重试 {config.VISION_MAX_RETRIES} 次")
    raise last_exception or VisionAPIError("所有重试都失败了")

async def image_to_markdown(image_path: str) -> str:
    """
    使用视觉大模型和OCR将图片转换为Markdown文本
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        Markdown格式的文本内容
        
    Raises:
        FileNotFoundError: 图片文件不存在
        OCRError: OCR处理失败
        VisionAPIError: 视觉API调用失败
    """
    try:
        # 验证文件存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 异步读取图片并转换为base64
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        markdown_content = ""
        
        # 先获取OCR结果
        ocr_text = await get_ocr_text(image_path)
        
        # 如果配置了Vision API，使用Vision API获取描述
        vision_description = ""
        logger.info(f"Vision client状态: {vision_client is not None}")
        
        if vision_client:
            try:
                prompt = ("Please provide a detailed description of this image, including: "
                         "1. Overall accurate description of the image; "
                         "2. Main elements and structure of the image; "
                         "3. If there are tables, charts, etc., please describe their content and layout in detail. "
                         "Please only return the description content, do not include OCR text extraction.")
                
                vision_description = await call_vision_api_with_retry(base64_image, prompt)
                
            except VisionAPIError as e:
                logger.warning(f"Vision API调用失败: {e}")
                vision_description = f"视觉模型调用失败: {str(e)}"
        else:
            vision_description = "视觉模型未配置，无法提供详细描述。"
        
        # 组合OCR和视觉描述结果
        markdown_content = format_image_result(ocr_text, vision_description)
        
        return markdown_content or "*无法识别图片内容*"
        
    except (FileNotFoundError, OCRError, VisionAPIError):
        # 重新抛出已知的异常类型
        raise
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        raise Exception(f"图片处理失败: {str(e)}")

async def get_ocr_text(image_path: str) -> str:
    """
    使用Tesseract OCR提取图片中的文字
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        提取的文字内容
        
    Raises:
        OCRError: OCR处理失败
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
        raise OCRError(f"OCR处理错误: {str(e)}")

def format_image_result(ocr_text: str, vision_description: str) -> str:
    """
    格式化图片处理结果，按照要求的markdown格式
    
    Args:
        ocr_text: OCR提取的文字
        vision_description: 视觉描述
        
    Returns:
        格式化的Markdown内容
    """
    # 处理换行符
    ocr_text = ocr_text.replace('\\n', '\n')
    vision_description = vision_description.replace('\\n', '\n')
    
    # 使用统一的代码块格式
    result = f"```image\n# OCR:\n{ocr_text}\n\n# Visual_Features:\n{vision_description}\n```"
    return result

async def fallback_ocr(image_path: str) -> str:
    """
    使用Tesseract OCR作为回退方案 (保持向后兼容)
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        格式化的OCR结果
    """
    try:
        ocr_text = await get_ocr_text(image_path)
        vision_description = "图片包含文字内容，已通过OCR技术提取。"
        return format_image_result(ocr_text, vision_description)
    except OCRError as e:
        logger.error(f"回退OCR失败: {e}")
        return f"*OCR处理失败: {str(e)}*" 