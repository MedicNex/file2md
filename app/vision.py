import openai
import base64
import os
import tempfile
from loguru import logger
from typing import Optional
import pytesseract
from PIL import Image
import httpx
import asyncio
import aiofiles

from app.config import config

# 配置 Tesseract 可执行文件路径
def configure_tesseract():
    """配置 Tesseract OCR 路径"""
    try:
        # 常见的 tesseract 安装路径
        possible_paths = [
            '/usr/bin/tesseract',      # Ubuntu/Debian 默认路径
            '/usr/local/bin/tesseract', # 手动编译安装路径
            '/opt/homebrew/bin/tesseract', # macOS Homebrew 路径
            'tesseract'                # 系统 PATH 中
        ]
        
        for path in possible_paths:
            if path == 'tesseract':
                # 尝试使用默认 PATH
                continue
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"配置 Tesseract 路径: {path}")
                return path
        
        # 如果没有找到明确路径，尝试使用默认设置
        logger.info("使用默认 Tesseract 路径配置")
        return None
        
    except Exception as e:
        logger.warning(f"配置 Tesseract 路径时出错: {e}")
        return None

# 初始化时配置 Tesseract
configure_tesseract()
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
        Exception: 图片处理失败（仅当OCR和视觉分析都失败时）
    """
    try:
        # 验证文件存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 异步读取图片并转换为base64
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # 尝试获取OCR结果，但允许失败
        ocr_text = ""
        try:
            ocr_text = await get_ocr_text(image_path)
            logger.info(f"OCR成功: {image_path}")
        except OCRError as e:
            logger.warning(f"OCR处理失败，但继续进行视觉分析: {e}")
            ocr_text = "未能通过OCR提取到文字内容"
        except Exception as e:
            logger.warning(f"OCR遇到意外错误，继续进行视觉分析: {e}")
            ocr_text = "OCR处理遇到技术问题"
        
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
                logger.info(f"视觉分析成功: {image_path}")
                
            except VisionAPIError as e:
                logger.warning(f"Vision API调用失败: {e}")
                vision_description = f"视觉模型调用失败: {str(e)}"
            except Exception as e:
                logger.warning(f"视觉分析遇到意外错误: {e}")
                vision_description = f"视觉分析遇到技术问题: {str(e)}"
        else:
            vision_description = "视觉模型未配置，无法提供详细描述。"
        
        # 组合OCR和视觉描述结果
        markdown_content = format_image_result(ocr_text, vision_description)
        
        # 如果OCR和视觉分析都没有有效结果，才报错
        if (not ocr_text or ocr_text in ["未能通过OCR提取到文字内容", "OCR处理遇到技术问题"]) and \
           (not vision_description or "失败" in vision_description or "问题" in vision_description):
            logger.error(f"图片处理完全失败，OCR和视觉分析都无法获得有效结果: {image_path}")
            return "*图片处理失败：无法通过OCR或视觉分析获取内容*"
        
        return markdown_content or "*无法识别图片内容*"
        
    except FileNotFoundError:
        # 重新抛出文件不存在错误
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
        # 使用PIL打开图片，增加格式兼容性处理
        try:
            image = Image.open(image_path)
            
            # 如果图片有多个帧（如动态GIF），只处理第一帧
            if hasattr(image, 'n_frames') and image.n_frames > 1:
                image.seek(0)
            
            # 确保图片是RGB模式（Tesseract更好的兼容性）
            if image.mode not in ('RGB', 'L'):  # RGB彩色或L灰度
                if image.mode == 'RGBA':
                    # RGBA转RGB，使用白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                elif image.mode == 'P':
                    # 调色板模式转RGB
                    image = image.convert('RGB')
                else:
                    # 其他模式转RGB
                    image = image.convert('RGB')
            
            # 对于JPEG格式，额外的兼容性处理
            if image_path.lower().endswith('.jpeg') or image_path.lower().endswith('.jpg'):
                # 确保JPEG图片被正确加载
                image.load()
                
        except (IOError, OSError) as e:
            # 如果PIL无法打开图片，尝试使用不同的方法
            logger.warning(f"PIL无法直接打开图片 {image_path}: {e}")
            try:
                # 尝试重新读取图片并转换格式
                import tempfile
                import shutil
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # 尝试用PIL强制转换格式
                with Image.open(image_path) as original_img:
                    original_img.load()
                    if original_img.mode != 'RGB':
                        original_img = original_img.convert('RGB')
                    original_img.save(temp_path, 'PNG')
                
                # 重新打开转换后的图片
                image = Image.open(temp_path)
                logger.info(f"成功转换图片格式: {image_path} -> PNG")
                
                # 清理临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            except Exception as convert_error:
                logger.error(f"图片格式转换失败 {image_path}: {convert_error}")
                raise OCRError(f"不支持的图片格式或图片损坏: {str(convert_error)}")
        
        # 使用Tesseract进行OCR
        try:
            # 先检查 tesseract 是否可用
            tesseract_cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', 'tesseract')
            logger.debug(f"使用 Tesseract 命令: {tesseract_cmd}")
            
            ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        except Exception as ocr_error:
            logger.error(f"Tesseract OCR处理失败 {image_path}: {ocr_error}")
            
            # 诊断 tesseract 是否可用
            tesseract_cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', 'tesseract')
            logger.error(f"当前 Tesseract 命令路径: {tesseract_cmd}")
            
            # 检查是否是路径问题
            if "not installed" in str(ocr_error).lower() or "not in your path" in str(ocr_error).lower():
                logger.error("Tesseract 路径问题，尝试重新配置路径")
                # 重新配置路径
                new_path = configure_tesseract()
                if new_path:
                    logger.info(f"重新配置 Tesseract 路径为: {new_path}")
                    try:
                        ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                        logger.info(f"重新配置路径后 OCR 成功: {image_path}")
                    except Exception as retry_error:
                        logger.error(f"重新配置路径后仍然失败: {retry_error}")
                        raise OCRError(f"Tesseract 路径配置失败: {str(retry_error)}")
                else:
                    raise OCRError(f"无法找到 Tesseract 可执行文件: {str(ocr_error)}")
            else:
                # 尝试只使用英文OCR
                try:
                    ocr_text = pytesseract.image_to_string(image, lang='eng')
                    logger.info(f"回退到英文OCR成功: {image_path}")
                except Exception as fallback_error:
                    logger.error(f"英文OCR也失败 {image_path}: {fallback_error}")
                    # 检查是否是格式不支持的问题，如果是，允许继续处理
                    error_msg = str(fallback_error).lower()
                    if any(keyword in error_msg for keyword in ['unsupported', 'format', 'type', 'decode']):
                        logger.warning(f"图片格式不支持OCR，但可能仍可进行视觉分析: {image_path}")
                        raise OCRError(f"图片格式不支持OCR处理，但图片可能仍可用于视觉分析")
                    else:
                        raise OCRError(f"OCR引擎处理失败: {str(fallback_error)}")
        
        if ocr_text.strip():
            logger.info(f"OCR成功提取文字: {image_path}")
            return ocr_text.strip()
        else:
            logger.warning(f"OCR未能提取到文字: {image_path}")
            return "未检测到文字内容"
            
    except OCRError:
        # 重新抛出OCR错误
        raise
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
    # 清理和验证输入内容
    ocr_text = _sanitize_text_content(ocr_text or "")
    vision_description = _sanitize_text_content(vision_description or "")
    
    # 处理换行符
    ocr_text = ocr_text.replace('\\n', '\n')
    vision_description = vision_description.replace('\\n', '\n')
    
    # 智能判断是否包含OCR内容
    has_valid_ocr = (ocr_text and 
                     ocr_text not in ["未检测到文字内容", "未能通过OCR提取到文字内容", "OCR处理遇到技术问题"] and
                     "失败" not in ocr_text and "问题" not in ocr_text)
    
    # 根据是否有有效OCR内容来格式化输出
    if has_valid_ocr:
        # 包含OCR和视觉描述
        result = f"```image\n# OCR:\n{ocr_text}\n\n# Visual_Features:\n{vision_description}\n```"
    else:
        # 仅包含视觉描述（适用于无文字图片）
        result = f"```image\n# Visual_Features:\n{vision_description}\n```"
    
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

def _sanitize_text_content(content: str) -> str:
    """
    清理文本内容，防止注入攻击
    
    Args:
        content: 原始文本内容
        
    Returns:
        清理后的安全文本内容
    """
    if not content:
        return ""
    
    # 限制内容长度
    max_length = 50000  # 50KB 文本限制
    if len(content) > max_length:
        content = content[:max_length] + "\n\n... (内容被截断，超过长度限制)"
    
    # 移除或转义危险的markdown语法
    # 转义代码块标记，防止markdown注入
    content = content.replace('```', '\\`\\`\\`')
    
    # 移除HTML标签（除了基本的格式标签）
    import re
    # 移除脚本和危险标签
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<object[^>]*>.*?</object>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<embed[^>]*/?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<link[^>]*/?>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<meta[^>]*/?>', '', content, flags=re.IGNORECASE)
    
    # 移除潜在的XSS攻击向量
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)
    
    # 清理控制字符和不可见字符
    content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
    
    # 标准化换行符
    content = re.sub(r'\r\n|\r', '\n', content)
    
    # 移除过多的连续换行符
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    return content.strip()