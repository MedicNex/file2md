from .base import BaseParser
from loguru import logger
import pandas as pd
from tabulate import tabulate
import openpyxl
from openpyxl.drawing.image import Image as OpenpyxlImage
import os
import base64
import asyncio
from app.vision import get_ocr_text, vision_client

class ExcelParser(BaseParser):
    """Excel文件解析器"""
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        return ['.xls', '.xlsx']
    
    async def _process_image_concurrent(self, image_data: bytes, img_name: str, sheet_name: str, sheet_image_counter: int):
        """并发处理单个图片的OCR和视觉识别"""
        try:
            # 创建临时图片文件
            temp_img_path = self.create_temp_file(suffix='.png')
            
            # 保存图片数据
            with open(temp_img_path, 'wb') as img_file:
                img_file.write(image_data)
            
            # 并发执行OCR和视觉识别
            ocr_task = get_ocr_text(temp_img_path)
            vision_task = self._get_vision_description(temp_img_path)
            
            ocr_text, vision_description = await asyncio.gather(ocr_task, vision_task)
            
            # 生成HTML标签格式
            alt_text = f"# OCR: {ocr_text} # Visual_Features: {vision_description}"
            html_img_tag = f'<img src="{img_name}" alt="{alt_text}" />'
            
            logger.info(f"成功处理Excel图片 {sheet_name} 图片{sheet_image_counter}: {img_name}")
            return f"### 工作表 {sheet_name} - 图片 {sheet_image_counter}\n\n{html_img_tag}"
            
        except Exception as e:
            logger.warning(f"Excel图片处理失败 {sheet_name} 图片{sheet_image_counter}: {e}")
            return f"### 工作表 {sheet_name} - 图片 {sheet_image_counter}\n\n*图片处理失败*"
    
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
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"Vision API调用失败: {e}")
            return "视觉模型识别失败"

    async def parse(self, file_path: str) -> str:
        """解析Excel文件"""
        try:
            content_parts = []
            
            # 读取所有工作表的数据
            xlsx_file = pd.ExcelFile(file_path)
            
            for sheet_name in xlsx_file.sheet_names:
                try:
                    # 读取工作表数据
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    # 跳过空工作表
                    if df.empty:
                        continue
                    
                    # 处理NaN值
                    df = df.fillna('')
                    
                    # 添加工作表标题
                    content_parts.append(f"## 工作表: {sheet_name}")
                    
                    # 转换为HTML表格
                    html_table = tabulate(df, headers='keys', tablefmt='html', showindex=False)
                    content_parts.append(html_table)
                    
                    # 添加基本统计信息
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        content_parts.append("### 数据统计")
                        stats_data = []
                        for col in numeric_cols:
                            stats_data.append([
                                col,
                                f"{df[col].count()}",
                                f"{df[col].mean():.2f}" if df[col].count() > 0 else "N/A",
                                f"{df[col].min():.2f}" if df[col].count() > 0 else "N/A",
                                f"{df[col].max():.2f}" if df[col].count() > 0 else "N/A"
                            ])
                        
                        stats_df = pd.DataFrame(stats_data, columns=['列名', '计数', '平均值', '最小值', '最大值'])
                        stats_table = tabulate(stats_df, headers='keys', tablefmt='html', showindex=False)
                        content_parts.append(stats_table)
                    
                except Exception as sheet_error:
                    logger.warning(f"工作表 {sheet_name} 解析失败: {sheet_error}")
                    content_parts.append(f"## 工作表: {sheet_name}\n\n*工作表解析失败: {str(sheet_error)}*")
            
            # 提取并处理图片（仅支持.xlsx格式）
            if file_path.lower().endswith('.xlsx'):
                try:
                    image_parts = await self._extract_images_from_xlsx(file_path)
                    if image_parts:
                        content_parts.extend(image_parts)
                except Exception as img_error:
                    logger.warning(f"Excel图片提取失败: {img_error}")
            
            raw_content = '\n\n'.join(content_parts)
            
            # 处理换行符
            raw_content = raw_content.replace('\\n', '\n')
            
            # 将代码块转换为HTML标签
            raw_content = self.convert_code_blocks_to_html(raw_content)
            
            # 格式化为统一的代码块格式
            markdown_content = f"```sheet\n{raw_content or 'Excel文件为空或无法提取内容'}\n```"
            
            logger.info(f"成功解析Excel文件: {file_path}")
            return markdown_content
            
        except Exception as e:
            logger.error(f"解析Excel文件失败 {file_path}: {e}")
            raise Exception(f"Excel文件解析错误: {str(e)}")
    
    async def _extract_images_from_xlsx(self, file_path: str) -> list[str]:
        """从XLSX文件中提取图片并进行OCR+视觉识别"""
        try:
            # 使用openpyxl打开工作簿
            workbook = openpyxl.load_workbook(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 收集所有图片信息
            all_image_info = []
            
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                sheet_image_counter = 0
                
                # 检查工作表中的图片
                if hasattr(worksheet, '_images') and worksheet._images:
                    for image in worksheet._images:
                        sheet_image_counter += 1
                        
                        # 生成图片文件名
                        img_name = f"{base_name}_{sheet_name}_image_{sheet_image_counter}.png"
                        
                        # 获取图片数据
                        image_data = image._data()
                        
                        all_image_info.append({
                            'data': image_data,
                            'name': img_name,
                            'sheet': sheet_name,
                            'counter': sheet_image_counter
                        })
            
            # 并发处理所有图片
            if all_image_info:
                image_tasks = [
                    self._process_image_concurrent(
                        img_info['data'],
                        img_info['name'],
                        img_info['sheet'],
                        img_info['counter']
                    )
                    for img_info in all_image_info
                ]
                
                try:
                    image_parts = await asyncio.gather(*image_tasks, return_exceptions=True)
                    
                    # 处理结果
                    final_image_parts = []
                    for i, result in enumerate(image_parts):
                        if isinstance(result, Exception):
                            img_info = all_image_info[i]
                            logger.error(f"Excel图片并发处理异常 {img_info['sheet']} 图片{img_info['counter']}: {result}")
                            final_image_parts.append(f"### 工作表 {img_info['sheet']} - 图片 {img_info['counter']}\n\n*图片处理异常*")
                        else:
                            final_image_parts.append(result)
                    
                    total_image_counter = len(all_image_info)
                    if total_image_counter > 0:
                        logger.info(f"Excel文档中共处理了 {total_image_counter} 张图片")
                    
                    workbook.close()
                    return final_image_parts
                    
                except Exception as e:
                    logger.error(f"Excel图片并发处理失败: {e}")
                    workbook.close()
                    # 回退处理
                    return [f"### 工作表 图片处理失败\n\n*图片并发处理失败*" for _ in range(len(all_image_info))]
            
            workbook.close()
            return []
            
        except Exception as e:
            logger.warning(f"Excel图片提取过程失败: {e}")
            return [] 