from .base import BaseParser
from loguru import logger
import pdfplumber
from PIL import Image
from app.vision import get_ocr_text
import os
import asyncio
from app.config import config
from typing import List, Tuple, Dict

class PdfParser(BaseParser):
    """PDF文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.pdf']
    
    async def _process_image_ocr_only(self, temp_img_path: str, img_name: str, page_num: int, img_idx: int, global_img_id: int):
        """仅对图片进行OCR处理，不使用视觉模型"""
        try:
            # 仅执行OCR处理
            try:
                ocr_text = await get_ocr_text(temp_img_path)
            except Exception as ocr_error:
                logger.warning(f"OCR处理失败，跳过处理 第{page_num}页 图片{img_idx + 1}: {ocr_error}")
                ocr_text = "OCR处理失败"
            
            # 生成HTML标签格式，仅包含OCR结果
            alt_text = f"# OCR: {ocr_text}"
            html_img_tag = f'<img src="{img_name}" alt="{alt_text}" />'
            
            logger.info(f"成功处理PDF图片 第{page_num}页 图片{img_idx + 1}: {img_name}")
            return {
                'global_id': global_img_id,
                'page_num': page_num,
                'img_idx': img_idx,
                'content': f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n{html_img_tag}"
            }
            
        except Exception as e:
            logger.warning(f"PDF图片处理失败，跳过该图片 第{page_num}页 图片{img_idx + 1}: {e}")
            return {
                'global_id': global_img_id,
                'page_num': page_num,
                'img_idx': img_idx,
                'content': f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n*图片处理失败，已跳过*"
            }

    async def parse(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            content_parts = []
            all_image_tasks = []
            global_img_id = 0
            
            with pdfplumber.open(file_path) as pdf:
                # 第一遍：收集所有图片任务
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取文本
                    text = page.extract_text()
                    if text and text.strip():
                        content_parts.append(f"## 第 {page_num} 页\n\n{text.strip()}")
                    
                    # 收集当前页面的所有图片任务
                    images = page.images
                    if images:
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
                                
                                # 创建OCR任务，包含全局ID以保持顺序
                                task = self._process_image_ocr_only(temp_img_path, img_name, page_num, img_idx, global_img_id)
                                all_image_tasks.append(task)
                                global_img_id += 1
                                
                            except Exception as img_error:
                                logger.warning(f"PDF图片提取失败，跳过该图片 第{page_num}页 图片{img_idx + 1}: {img_error}")
                                content_parts.append(f"### 第 {page_num} 页 - 图片 {img_idx + 1}\n\n*图片提取失败，已跳过*")
                
                # 第二遍：并发处理所有图片
                if all_image_tasks:
                    logger.info(f"开始并发处理 {len(all_image_tasks)} 张图片...")
                    try:
                        image_results = await asyncio.gather(*all_image_tasks, return_exceptions=True)
                        
                        # 按全局ID排序，保持原始顺序
                        valid_results = []
                        for result in image_results:
                            if isinstance(result, Exception):
                                logger.error(f"图片并发处理异常: {result}")
                            else:
                                valid_results.append(result)
                        
                        # 按全局ID排序
                        valid_results.sort(key=lambda x: x['global_id'])
                        
                        # 按页面和图片索引重新组织内容
                        page_content_map = {}
                        for result in valid_results:
                            page_num = result['page_num']
                            if page_num not in page_content_map:
                                page_content_map[page_num] = []
                            page_content_map[page_num].append(result['content'])
                        
                        # 按页面顺序插入图片内容
                        current_page = 1
                        for page_num in sorted(page_content_map.keys()):
                            # 如果当前页面没有文本内容，添加页面标题
                            if not any("## 第 " in part for part in content_parts):
                                content_parts.append(f"## 第 {page_num} 页\n")
                            
                            # 添加当前页面的图片内容
                            content_parts.extend(page_content_map[page_num])
                            current_page = page_num + 1
                        
                        logger.info(f"成功并发处理 {len(valid_results)} 张图片")
                        
                    except Exception as e:
                        logger.error(f"图片并发处理失败: {e}")
                        content_parts.append("### 图片处理失败\n\n*图片并发处理失败，已跳过所有图片*")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```document\n{raw_content or 'PDF文件为空或无法提取内容'}\n```"
            
            logger.info(f"成功解析PDF文件: {file_path} (仅OCR处理，不受图片数量限制，全文档并发处理)")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析PDF文件失败 {file_path}: {e}")
            raise Exception(f"PDF文件解析错误: {str(e)}") 