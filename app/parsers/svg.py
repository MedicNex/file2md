from .base import BaseParser
from loguru import logger
import chardet
import os
import asyncio
import re
from app.vision import get_ocr_text, call_vision_api_with_retry, vision_client
from app.config import config
import base64

# 尝试导入SVG转换库
try:
    from wand.image import Image as WandImage
    from wand.color import Color
    WAND_AVAILABLE = True
except ImportError:
    logger.warning("Wand (ImageMagick) 未安装，SVG转PNG功能将受限")
    WAND_AVAILABLE = False

try:
    import cairosvg
    CAIRO_AVAILABLE = True
except (ImportError, OSError) as e:
    logger.warning(f"CairoSVG 不可用: {e}")
    CAIRO_AVAILABLE = False

# 如果两种库都不可用，发出警告
if not WAND_AVAILABLE and not CAIRO_AVAILABLE:
    logger.warning("既没有ImageMagick也没有CairoSVG，SVG视觉识别功能将不可用")

class SvgParser(BaseParser):
    """SVG文件解析器 - 同时识别代码和视觉特征"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.svg']
    
    async def _convert_svg_to_png(self, svg_path: str) -> str:
        """将SVG文件转换为PNG格式以便视觉识别"""
        if not WAND_AVAILABLE and not CAIRO_AVAILABLE:
            raise Exception("没有可用的SVG转换库，无法进行视觉识别")
        
        # 创建临时PNG文件
        temp_png_path = self.create_temp_file(suffix='.png')
        
        try:
            if CAIRO_AVAILABLE:
                # 优先使用CairoSVG（更轻量级）
                await self._convert_with_cairo(svg_path, temp_png_path)
            elif WAND_AVAILABLE:
                # 回退到ImageMagick
                await self._convert_with_wand(svg_path, temp_png_path)
            
            logger.info(f"成功将SVG转换为PNG: {svg_path} -> {temp_png_path}")
            return temp_png_path
            
        except Exception as e:
            logger.error(f"SVG转PNG失败 {svg_path}: {e}")
            raise Exception(f"SVG转换错误: {str(e)}")
    
    async def _convert_with_cairo(self, svg_path: str, png_path: str):
        """使用CairoSVG转换SVG到PNG"""
        # 读取SVG内容
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # 转换为PNG
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=png_path,
            output_width=800,  # 设置输出宽度
            output_height=600,  # 设置输出高度
            background_color='white'
        )
    
    async def _convert_with_wand(self, svg_path: str, png_path: str):
        """使用Wand(ImageMagick)转换SVG到PNG"""
        with WandImage() as img:
            with Color('white') as background_color:
                img.background_color = background_color
            
            # 设置安全选项
            img.options['svg:xml-parse-huge'] = 'false'
            img.options['svg:xml-parse-nonet'] = 'true'
            
            # 读取SVG文件
            img.read(filename=os.path.abspath(svg_path))
            
            # 限制输出尺寸
            if img.width > 2000 or img.height > 2000:
                img.resize(2000, 2000)
            
            # 设置输出格式为PNG
            img.format = 'png'
            
            # 设置分辨率提高质量（限制最大分辨率）
            img.resolution = (min(300, 300), min(300, 300))
            
            # 保存为PNG
            img.save(filename=png_path)
    
    async def _get_vision_description(self, png_path: str) -> str:
        """获取视觉模型描述"""
        if not vision_client:
            return "视觉模型未配置，无法提供详细描述"
        
        try:
            # 读取PNG图片并转换为base64
            with open(png_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            prompt = ("Please provide a detailed description of this SVG image, including: "
                     "1. Overall accurate description of the visual elements; "
                     "2. Main elements, shapes, colors, and structure; "
                     "3. If there are charts, diagrams, icons, or text elements, describe their content and layout; "
                     "4. Visual design characteristics and styling.")
            
            vision_description = await call_vision_api_with_retry(base64_image, prompt)
            return vision_description
            
        except Exception as e:
            logger.warning(f"Vision API调用失败: {e}")
            return f"视觉模型识别失败: {str(e)}"
    
    async def parse(self, file_path: str) -> str:
        """解析SVG文件为代码格式和视觉特征"""
        try:
            # 安全性检查
            if not self._validate_svg_security(file_path):
                raise Exception("SVG文件安全验证失败")
                
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            # 读取SVG文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                svg_content = f.read()
            
            # 清理SVG内容
            svg_content = self._sanitize_svg_content(svg_content)
            
            # 格式化SVG代码块
            code_section = f'<code class="language-svg">\n{svg_content.strip()}\n</code>'
            
            # 转换SVG为PNG并进行视觉识别
            visual_features = ""
            if WAND_AVAILABLE or CAIRO_AVAILABLE:
                try:
                    # 转换SVG到PNG
                    png_path = await self._convert_svg_to_png(file_path)
                    
                    # 并发执行OCR和视觉识别
                    ocr_task = get_ocr_text(png_path)
                    vision_task = self._get_vision_description(png_path)
                    
                    ocr_text, vision_description = await asyncio.gather(ocr_task, vision_task)
                    
                    # 组合OCR和视觉描述
                    if ocr_text and ocr_text.strip() != "未检测到文字内容":
                        visual_features = f"# OCR: {ocr_text}\n\n# Visual_Features: {vision_description}"
                    else:
                        visual_features = f"# Visual_Features: {vision_description}"
                    
                except Exception as e:
                    logger.warning(f"SVG视觉识别失败 {file_path}: {e}")
                    visual_features = "# Visual_Features: 视觉识别失败，无法提供SVG的视觉描述"
            else:
                # 没有转换库可用时的降级方案
                visual_features = "# Visual_Features: 无可用的SVG转换库（需要ImageMagick或Cairo），仅提供代码结构"
            
            # 组合代码块和视觉特征
            formatted_content = f"```svg\n# Code\n{code_section}\n\n{visual_features}\n```"
            
            logger.info(f"成功解析SVG文件（代码+视觉）: {file_path}")
            return formatted_content
            
        except Exception as e:
            logger.error(f"解析SVG文件失败 {file_path}: {e}")
            raise Exception(f"SVG文件解析错误: {str(e)}")
    
    def _validate_svg_security(self, file_path: str) -> bool:
        """验证SVG文件安全性"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件大小（限制为10MB）
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:
                logger.error(f"SVG文件过大: {file_size} bytes")
                return False
            
            # 检查文件路径，防止路径遍历攻击
            abs_path = os.path.abspath(file_path)
            if '..' in file_path or abs_path != os.path.normpath(abs_path):
                logger.error(f"检测到可疑文件路径: {file_path}")
                return False
            
            # 检查SVG内容是否包含危险元素
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含危险的SVG元素
                dangerous_patterns = [
                    r'<script[^>]*>',
                    r'javascript:',
                    r'on\w+\s*=',  # onclick, onload等事件
                    r'<foreignObject',
                    r'<iframe',
                    r'<object',
                    r'<embed'
                ]
                
                for pattern in dangerous_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        logger.error(f"SVG包含危险元素: {pattern}")
                        return False
                        
            except UnicodeDecodeError:
                logger.error("SVG文件编码错误")
                return False
            
            return True
        except Exception as e:
            logger.error(f"SVG安全验证失败: {e}")
            return False
    
    def _sanitize_svg_content(self, content: str) -> str:
        """清理SVG内容，移除危险元素"""
        if not content:
            return content
        
        # 限制内容长度
        if len(content) > 500000:  # 500KB 文本限制
            content = content[:500000] + "\n<!-- 内容被截断，超过限制 -->"
        
        # 移除危险的脚本和事件处理器
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'javascript:[^"\']*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        
        # 移除危险的嵌入元素
        content = re.sub(r'<foreignObject[^>]*>.*?</foreignObject>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<object[^>]*>.*?</object>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<embed[^>]*/?>', '', content, flags=re.IGNORECASE)
        
        return content