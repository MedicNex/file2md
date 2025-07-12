import openai
import base64
import os
import tempfile
from loguru import logger
from typing import Optional
# 移除 pytesseract 导入，改用 PaddleOCR
# import pytesseract
from PIL import Image
import httpx
import asyncio
import aiofiles

from app.config import config

# 初始化 PaddleOCR
_ocr_engine = None

def _is_gpu_available() -> bool:
    """检测系统是否存在可用 GPU 并且 PaddlePaddle 编译支持 CUDA"""
    try:
        import paddle
        if paddle.device.is_compiled_with_cuda():
            return paddle.device.cuda.device_count() > 0
    except Exception as e:
        # 捕获所有异常（包括未安装 paddle 的情况）
        logger.debug(f"GPU 检测失败或不可用: {e}")
    return False

def init_paddle_ocr():
    """初始化 PaddleOCR 引擎"""
    global _ocr_engine
    try:
        from paddleocr import PaddleOCR
        
        # 根据系统环境自动检测是否启用 GPU
        gpu_available = _is_gpu_available()

        try:
            # 尝试新版本参数
            _ocr_engine = PaddleOCR(
                use_textline_orientation=True,  # 使用文本行方向检测 (新参数名)
                lang='ch',  # 中文识别
                use_gpu=gpu_available  # 自动选择 GPU 或 CPU
            )
            logger.info(
                f"PaddleOCR ({'GPU' if gpu_available else 'CPU'}) 初始化成功 - 使用新版API"
            )
        except TypeError:
            # 回退到旧版本参数（use_angle_cls）
            logger.info("使用旧版本PaddleOCR API参数")
            _ocr_engine = PaddleOCR(
                use_angle_cls=True,  # 使用角度分类器 (旧参数名)
                lang='ch',  # 中文识别
                use_gpu=gpu_available  # 自动选择 GPU 或 CPU
            )
            logger.info(
                f"PaddleOCR ({'GPU' if gpu_available else 'CPU'}) 初始化成功 - 使用旧版API"
            )
        
        return _ocr_engine
        
    except ImportError:
        logger.error("PaddleOCR 未安装，请运行: pip install paddleocr")
        return None
    except Exception as e:
        logger.error(f"PaddleOCR 初始化失败: {e}")
        return None

def get_ocr_engine():
    """获取 OCR 引擎实例"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = init_paddle_ocr()
    return _ocr_engine

# 兼容性函数 - 废弃 Tesseract 配置
def configure_tesseract():
    """废弃的 Tesseract 配置函数，保持兼容性"""
    logger.warning("configure_tesseract() 已废弃，现在使用 PaddleOCR")
    return None

# 初始化时配置 PaddleOCR
init_paddle_ocr()
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
            return content or "视觉模型返回空内容"
            
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
    使用PaddleOCR提取图片中的文字
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        提取的文字内容
        
    Raises:
        OCRError: OCR处理失败
    """
    try:
        # 获取 PaddleOCR 引擎
        ocr_engine = get_ocr_engine()
        if ocr_engine is None:
            raise OCRError("PaddleOCR 引擎未初始化")
        
        # 验证图片文件存在
        if not os.path.exists(image_path):
            raise OCRError(f"图片文件不存在: {image_path}")
        
        # 图片预处理 - 为了兼容性，检查图片格式
        processed_image_path = image_path
        temp_converted_path = None
        
        try:
            with Image.open(image_path) as image:
                # 如果图片有多个帧（如动态GIF），只处理第一帧
                if hasattr(image, 'n_frames') and image.n_frames > 1:  # type: ignore
                    image.seek(0)
                
                # 确保图片格式兼容 PaddleOCR
                if image.mode not in ('RGB', 'L'):
                    if image.mode == 'RGBA':
                        # RGBA转RGB，使用白色背景
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[-1])
                        # 保存转换后的图片
                        temp_converted_path = image_path + "_converted.png"
                        background.save(temp_converted_path, 'PNG')
                        processed_image_path = temp_converted_path
                    elif image.mode in ('P', 'CMYK', '1'):
                        # 其他格式转RGB
                        rgb_image = image.convert('RGB')
                        temp_converted_path = image_path + "_converted.png"
                        rgb_image.save(temp_converted_path, 'PNG')
                        processed_image_path = temp_converted_path
                        
        except (IOError, OSError) as e:
            logger.warning(f"图片格式检查失败，直接使用原图: {e}")
        
        # 使用 PaddleOCR 进行文字识别
        try:
            logger.debug(f"使用 PaddleOCR 处理图片: {processed_image_path}")
            
            # PaddleOCR 识别
            result = ocr_engine.ocr(processed_image_path, cls=True)
            
            # 解析 PaddleOCR 结果
            ocr_text_list = []
            if result and result[0]:  # result是一个列表，包含每页的结果
                for line in result[0]:  # 遍历每一行文字
                    if line and len(line) >= 2:
                        text = line[1][0]  # 获取识别的文字
                        confidence = line[1][1]  # 获取置信度
                        # 只保留置信度较高的文字
                        if confidence > 0.5:  # 置信度阈值
                            ocr_text_list.append(text)
            
            # 合并识别结果
            if ocr_text_list:
                ocr_text = '\n'.join(ocr_text_list)
                logger.info(f"PaddleOCR 成功提取文字: {len(ocr_text_list)} 行文字")
                return ocr_text.strip()
            else:
                logger.warning(f"PaddleOCR 未能提取到文字: {image_path}")
                return "未检测到文字内容"
                
        except Exception as ocr_error:
            logger.error(f"PaddleOCR 处理失败 {image_path}: {ocr_error}")
            
            # 检查是否是模型加载问题
            if "No module named" in str(ocr_error) or "ImportError" in str(ocr_error):
                raise OCRError(f"PaddleOCR 依赖缺失: {str(ocr_error)}")
            elif "download" in str(ocr_error).lower():
                raise OCRError(f"PaddleOCR 模型下载失败，请检查网络连接: {str(ocr_error)}")
            else:
                raise OCRError(f"PaddleOCR 识别失败: {str(ocr_error)}")
        
        finally:
            # 清理临时转换的图片文件
            if temp_converted_path and os.path.exists(temp_converted_path):
                try:
                    os.unlink(temp_converted_path)
                except:
                    pass
            
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
    使用PaddleOCR作为OCR处理方案 (保持向后兼容)
    
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